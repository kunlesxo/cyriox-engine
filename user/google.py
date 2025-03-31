import requests
from .models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsAdmin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken


class GoogleAuthView(APIView):
    permission_classes = [IsAdmin]
    def post(self, request):
        id_token = request.data.get("access_token")  # This is actually an ID Token
        if not id_token:
            return Response({"error": "ID token is required"}, status=400)

        # Google API to validate ID token
        google_api_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        response = requests.get(google_api_url)

        if response.status_code != 200:
            return Response({"error": "Invalid Google token"}, status=401)

        user_data = response.json()
        email = user_data.get("email")
        username = user_data.get("name")

        if not email:
            return Response({"error": "Email not provided by Google"}, status=400)

        # Ensure unique username
        base_username = username.replace(" ", "_").lower()
        unique_username = base_username
        count = 1
        while User.objects.filter(username=unique_username).exists():
            unique_username = f"{base_username}_{count}"
            count += 1

        user, created = User.objects.get_or_create(
            email=email, defaults={"username": unique_username}, role=User.ROLE.BASE_USER,
        )

        if created:
            user.set_unusable_password()
            user.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            }
        )

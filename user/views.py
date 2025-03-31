from .serializers import (
    UserSerializer, UserLoginSerializer, UserSignupSerializer, 
    VerifySerializer, DistributorSignupSerializer, ChangePasswordSerializer , AdminSignupSerializer
)
from rest_framework.views import APIView
from rest_framework import status, generics
from .models import User
from datetime import datetime
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from .verify import send_otp_email
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.apps import apps


class AdminSignupView(APIView):
    """API to register a new admin user"""
    def post(self, request):
        serializer = AdminSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Admin account created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        email = serializer.validated_data.get("email")
        refresh = RefreshToken.for_user(user)
        response_data = {
            "message": "Registration successful",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": str(user.id),
                "role": user.role,
                "email": user.email,
                "username": user.username
            },
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class DistributorSignupView(generics.CreateAPIView):
    serializer_class = DistributorSignupSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        distributor = serializer.save()
        refresh = RefreshToken.for_user(distributor)
        response_data = {
            "message": "Distributor registration successful",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "distributor": {
                "id": str(distributor.id),
                "role": distributor.role,
                "email": distributor.email,
                "username": distributor.username
            },
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class VerifyUserAccount(generics.GenericAPIView):
    serializer_class = VerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        otp = serializer.validated_data.get("otp")

        session_email = request.session.get("create_account_email")
        session_otp = request.session.get("create_account_otp")

        if session_email != email or session_otp != otp:
            return Response({"error": "Invalid OTP or email"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            user.verified = True  
            user.save()
            del request.session["create_account_email"]
            del request.session["create_account_otp"]
            return Response({"message": "Account verified successfully!"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)


class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            login(request, user)
            user_data = {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'email': user.email
            }
            return Response({
                "message": "Login successful.",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "data": user_data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateUserView(APIView):
    def patch(self, request):
        user = request.user  # Get logged-in user
        distributor_id = request.data.get("distributor")
        branch_id = request.data.get("branch_id")  # Get branch by ID
        branch_name = request.data.get("branch_name")  # Get branch by Name

        Distributor = apps.get_model("distributor", "Distributor")
        Branch = apps.get_model("branch", "Branch")

        # Assign Distributor by ID
        if distributor_id:
            try:
                distributor = Distributor.objects.get(id=distributor_id)
                user.distributor = distributor
            except Distributor.DoesNotExist:
                return Response({"error": "Distributor not found"}, status=status.HTTP_404_NOT_FOUND)

        # Assign Branch by ID
        if branch_id:
            try:
                branch = Branch.objects.get(id=branch_id)
                user.branch = branch
            except Branch.DoesNotExist:
                return Response({"error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)

        # Assign Branch by Name (if ID is not provided)
        elif branch_name:
            try:
                branch = Branch.objects.get(name=branch_name)
                user.branch = branch
            except Branch.DoesNotExist:
                return Response({"error": "Branch not found with the given name"}, status=status.HTTP_404_NOT_FOUND)

        user.save()
        return Response({"message": "User updated successfully", "user": UserSerializer(user).data}, status=status.HTTP_200_OK)
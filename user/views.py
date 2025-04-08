from .serializers import (
    UserDetailSerializer, UserLoginSerializer, UserSignupSerializer, 
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

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
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

        refresh = RefreshToken.for_user(user)

        response_data = {
            "message": "Registration successful",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": str(user.id),
                "role": user.role,
                "email": user.email,
                "username": user.username,
                "distributor_name": user.distributor.name  
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


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny  # Add this import

class LoginView(APIView):
    authentication_classes = []  # Disable authentication for this view
    permission_classes = [AllowAny]  # Allow any user to access this view without authentication

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # Attempt to authenticate the user with provided email and password
        user = authenticate(email=email, password=password)
        
        if user is None:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create refresh token for the user
        refresh = RefreshToken.for_user(user)
        
        # Return the response with tokens and user data
        return Response({
            "success": True,
            "message": "Login successful",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "role": user.role,
            "distributor_id": str(user.id)  # Return distributor ID (or user ID, depending on your model)
        }, status=status.HTTP_200_OK)

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
        serializer = UserDetailSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateUserView(APIView):
    def patch(self, request):
        user = request.user
        distributor_id = request.data.get("distributor")
        branch_id = request.data.get("branch_id")
        branch_name = request.data.get("branch_name")

        Distributor = apps.get_model("distributor", "Distributor")
        Branch = apps.get_model("branch", "Branch")

        if distributor_id:
            try:
                distributor = Distributor.objects.get(id=distributor_id)
                user.distributor = distributor
            except Distributor.DoesNotExist:
                return Response({"error": "Distributor not found"}, status=status.HTTP_404_NOT_FOUND)

        if branch_id:
            try:
                branch = Branch.objects.get(id=branch_id)
                user.branch = branch
            except Branch.DoesNotExist:
                return Response({"error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)

        elif branch_name:
            try:
                branch = Branch.objects.get(name=branch_name)
                user.branch = branch
            except Branch.DoesNotExist:
                return Response({"error": "Branch not found with the given name"}, status=status.HTTP_404_NOT_FOUND)

        user.save()
        return Response({"message": "User updated successfully", "user": UserDetailSerializer(user).data}, status=status.HTTP_200_OK)




from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserDetailSerializer
from .models import User
from distributor.models import DistributorCustomer
class DistributorCustomerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if the logged-in user is a distributor
        if request.user.role != 'Distributor':
            return Response({"detail": "You are not authorized to view these users."}, status=status.HTTP_403_FORBIDDEN)

        # Ensure that the distributor field is properly set on the user
        distributor = request.user.distributor
        if not distributor:
            return Response({"detail": "No distributor found for this user."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch all users (customers) linked to this distributor via DistributorCustomer model
        customers = DistributorCustomer.objects.filter(distributor=distributor)

        # Log the customers for debugging
        print(f"Distributor: {distributor}, Customers: {customers}")

        # Return the customer list
        serializer = UserDetailSerializer([customer.customer for customer in customers], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


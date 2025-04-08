from .models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from distributor.models import Distributor, Branch

### Admin Signup ###

class AdminSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    access_code = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'access_code', 'phone_number', 'role']

    def validate_access_code(self, value):
        if value != "2001":
            raise serializers.ValidationError("Invalid access code.")
        return value

    def create(self, validated_data):
        # Pop access code since it's only for validation
        validated_data.pop('access_code', None)

        # Ensure `is_staff` and `is_superuser` are set for the admin user
        validated_data['is_staff'] = True
        validated_data['is_superuser'] = True

        # Default role for admin users
        validated_data['role'] = 'Admin'

        # Ensure that phone_number is in the validated_data
        if 'phone_number' not in validated_data:
            validated_data['phone_number'] = None  # Set a default value if not provided

        return User.objects.create_user(**validated_data)

### Base User Signup ###
class UserSignupSerializer(serializers.ModelSerializer):
    distributor_name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone_number', 'password', 'role', 'distributor_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'role': {'read_only': True}
        }

    def create(self, validated_data):
        distributor_name = validated_data.pop('distributor_name', None)

        # Extract required fields explicitly
        email = validated_data.get('email')
        username = validated_data.get('username')
        phone_number = validated_data.get('phone_number')
        password = validated_data.get('password')
        role = 'Base User'  # Or however you're assigning it

        # Create user with required args
        user = User.objects.create_user(
            email=email,
            username=username,
            phone_number=phone_number,
            role=role,
            password=password
        )

        # Optional distributor linking for customers
        if distributor_name:
            try:
                distributor = Distributor.objects.get(name=distributor_name)
                user.distributor = distributor
                user.save()
            except Distributor.DoesNotExist:
                raise serializers.ValidationError({"distributor_name": "Distributor not found."})

        return user

### Distributor Signup ###
class DistributorSignupSerializer(serializers.ModelSerializer):
    distributor_name = serializers.CharField(write_only=True)
    branch_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "email", "username", "phone_number", "password", "role", "distributor_name", "branch_name"]
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'role': {'read_only': True}
        }

    def create(self, validated_data):
        distributor_name = validated_data.pop("distributor_name")
        branch_name = validated_data.pop("branch_name", None)

        # Set fixed role
        validated_data["role"] = "Distributor"

        # Extract required fields for user creation
        email = validated_data.get("email")
        username = validated_data.get("username")
        phone_number = validated_data.get("phone_number")
        password = validated_data.get("password")
        role = validated_data.get("role")

        # Create user
        user = User.objects.create_user(
            email=email,
            username=username,
            phone_number=phone_number,
            role=role,
            password=password
        )

        # Create Distributor and Branch
        distributor = Distributor.objects.create(name=distributor_name, user=user)
        
        if branch_name:
            Branch.objects.create(name=branch_name, distributor=distributor)

        return user


### Login ###
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required")

        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid credentials")

        data["user"] = user
        return data

### Change Password ###
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context['request'].user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError("Old password is incorrect")
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

### User Verification (e.g. OTP) ###
class VerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

### Generic User Serializer (For Retrieval) ###
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'username', 'role']

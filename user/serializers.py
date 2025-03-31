from .models import User
from rest_framework import serializers
from django.contrib.auth import authenticate



class AdminSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    access_code = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'access_code']

    def validate_access_code(self, value):
        """Ensure the provided access code matches the required secret key"""
        if value != "2001":  # Replace with your actual access code
            raise serializers.ValidationError("Invalid access code.")
        return value

    def create(self, validated_data):
        """Create an admin user and remove the access_code field before saving"""
        validated_data['is_staff'] = True
        validated_data['is_superuser'] = True
        return User.objects.create_user(**validated_data)
    
class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }

    def create(self, validated_data):
        password = validated_data['password']
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email:
            raise serializers.ValidationError("Email is required")
        if not password:
            raise serializers.ValidationError("Password is required")
        
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        data["user"] = user
        return data

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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class VerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


from rest_framework import serializers
from distributor.models import Distributor
from distributor.models import Branch

class DistributorSignupSerializer(serializers.ModelSerializer):
    distributor_name = serializers.CharField(write_only=True)
    branch_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "email", "username", "phone_number", "password", "role", "distributor_name", "branch_name"]
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'role': {'read_only': True}  # Prevent overriding role manually
        }

    def create(self, validated_data):
        # ✅ Extract distributor_name and branch_name before passing to User
        distributor_name = validated_data.pop("distributor_name")
        branch_name = validated_data.pop("branch_name", None)
        
        # ✅ Set the role explicitly
        validated_data["role"] = "Distributor"

        # ✅ Create the user (password is handled automatically)
        user = User.objects.create_user(**validated_data)

        # ✅ Create the distributor and assign it to the user
        distributor = Distributor.objects.create(name=distributor_name, user=user) 
        user.distributor_profile = distributor  # ✅ Use `related_name`
        user.save()

        # ✅ If a branch name is provided, create and assign it
        if branch_name:
            Branch.objects.create(name=branch_name, distributor=distributor)

        return user
import uuid
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.apps import apps
from django.conf import settings  # ✅ SAFE IMPORT

class AppUserManager(BaseUserManager):
    def create_user(self, email, phone_number, username, role, password=None):
        if not email:
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")

        user = self.model(
            id=uuid.uuid4(),  # Auto-generate UUID
            email=self.normalize_email(email), 
            phone_number=phone_number, 
            role=role, 
            username=username
        )
        user.set_password(password)
        user.save(using=self._db)  # ✅ Save user
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(email=email, username=username, password=password, phone_number=None, role="Admin")
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    class ROLE(models.TextChoices):
        BASE_USER = "Base User", "Base User"
        ADMIN = "Admin", "Admin"
        SUPPORT = "Support", "Support"
        MANAGER = "Manager", "Manager"
        DISTRIBUTOR = "Distributor", "Distributor"
        BRANCH_MANAGER = "Branch Manager", "Branch Manager"
        STAFF = "Staff", "Staff"
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    phone_number = models.CharField(max_length=14, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE.choices, null=True, default=ROLE.BASE_USER)
    distributor = models.OneToOneField(
        "distributor.Distributor", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="distributor_profile"  # ✅ FIX: Avoids reverse accessor conflict
    )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = AppUserManager()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.username} ({self.role})"

    def get_distributor(self):
        """Dynamically get the distributor linked to this user"""
        Distributor = apps.get_model("distributor", "Distributor")
        return Distributor.objects.filter(user_profile=self).first()

    def get_branch(self):
        """Dynamically get the branch linked to this user"""
        Branch = apps.get_model("branch", "Branch")
        return Branch.objects.filter(user=self).first()

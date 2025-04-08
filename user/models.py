import uuid
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.apps import apps
from django.core.exceptions import ValidationError


class AppUserManager(BaseUserManager):
    def create_user(self, email, phone_number, username, role, password=None, distributor_name=None, is_staff=False, is_superuser=False):
        if not email:
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")

        user = self.model(
            id=uuid.uuid4(),  # Auto-generate UUID
            email=self.normalize_email(email),
            phone_number=phone_number,
            role=role,  # Role is now passed correctly
            username=username,
            is_staff=is_staff,  # Set is_staff value
            is_superuser=is_superuser  # Set is_superuser value
        )
        user.set_password(password)

        # If distributor_name is provided, link to a distributor
        if distributor_name:
            try:
                Distributor = apps.get_model("distributor", "Distributor")
                distributor = Distributor.objects.get(name=distributor_name)
                user.distributor = distributor
            except Distributor.DoesNotExist:
                raise ValidationError("Distributor not found.")

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

    def get_full_name(self):
        """Fetch the full name of the user."""
        return f"{self.first_name} {self.last_name}"  # Ensure these fields exist

    def get_distributor(self):
        """Fetch distributor associated with this user using DistributorCustomer."""
        from distributor.models import DistributorCustomer
        dist_rel = DistributorCustomer.objects.filter(customer=self).first()
        return dist_rel.distributor if dist_rel else None

    def get_branch(self):
        """Dynamically get the branch linked to this user."""
        Branch = apps.get_model("branch", "Branch")
        return Branch.objects.filter(user=self).first()

    def is_distributor(self):
        """Check if the user is a distributor."""
        return self.role == self.ROLE.DISTRIBUTOR

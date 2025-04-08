from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class PayoutStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SUCCESSFUL = "successful", "Successful"
    FAILED = "failed", "Failed"


class Payout(models.Model):
    """Model for handling payouts to users"""
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="payouts")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    recipient_code = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=PayoutStatus.choices, default=PayoutStatus.PENDING)
    reference = models.CharField(max_length=100, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payout {self.reference} - {self.status}"

    def save(self, *args, **kwargs):
        """Generate a unique reference if not set"""
        if not self.reference:
            self.reference = f"PYT-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class TransactionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"


class Transaction(models.Model):
    """Model for tracking user transactions"""
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="transactions")
    reference = models.CharField(max_length=100, unique=True, editable=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField(null=True, blank=True)
    has_made_payment = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=TransactionStatus.choices, default=TransactionStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.reference}: {self.user.email} - {self.amount} - {self.status}"

    def save(self, *args, **kwargs):
        """Generate a unique reference if not set"""
        if not self.reference:
            self.reference = f"TRX-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


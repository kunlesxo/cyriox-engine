from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()

from django.db import models
from django.conf import settings
from user.models import User  # Import User model from the user app

class Distributor(models.Model):
    """Main distributor account"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # ✅ Replace direct import with this
        on_delete=models.CASCADE,
        related_name="distributor_profile"
    )
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class DistributorCustomer(models.Model):
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE, related_name="customers")  # Link to Distributor model
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_distributor")  # Link to User model
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('distributor', 'customer')

    def __str__(self):
        return f"{self.customer.username} -> {self.distributor.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
    ]

    distributor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    branch = models.ForeignKey("Branch", on_delete=models.CASCADE, related_name="branch_orders")
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_orders")
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.product_name} ({self.status})"

class Invoice(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Failed", "Failed"),
    ]

    distributor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_invoices")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.id} - {self.status}"
    
class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    transaction_id = models.CharField(max_length=255, unique=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount_paid}"    


from django.db import models
import uuid

class Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    distributor = models.ForeignKey(
        "distributor.Distributor",  # ✅ Should reference Distributor, not User
        on_delete=models.CASCADE,
        related_name="branches"
    )
    name = models.CharField(max_length=255)
    location = models.TextField()
    manager = models.ForeignKey(
        "user.User",  # ✅ Reference User for manager
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_branches"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.distributor.name}"  # ✅ Updated to use distributor's name


class Stock(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="stocks")
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.product_name} - {self.branch.name}"

class StockHistory(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="history")
    action = models.CharField(max_length=50)  # Added, Updated, Deleted, Order Placed
    quantity_changed = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stock.product_name} - {self.action} ({self.quantity_changed})"
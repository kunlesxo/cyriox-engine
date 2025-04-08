from rest_framework import serializers
from django.utils.formats import localize
from .models import Transaction

class PaystackPaymentSerializer(serializers.Serializer):
    """Serializer for initializing Paystack payments"""
    email = serializers.EmailField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1)

    def validate_amount(self, value):
        """Ensure amount is a positive value"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transactions"""
    user = serializers.CharField(source="user.email", read_only=True)  # Return user email instead of ID
    reference = serializers.CharField(read_only=True)  # Ensure reference is read-only
    created_at = serializers.DateTimeField(read_only=True)
    formatted_amount = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ["user", "reference", "amount", "formatted_amount", "status", "status_label", "created_at"]

    def get_formatted_amount(self, obj):
        """Format the amount as currency"""
        return f"₦{localize(obj.amount)}"

    def get_status_label(self, obj):
        """Get a human-readable status label"""
        return {
            "pending": "Pending",
            "success": "Successful",
            "failed": "Failed"
        }.get(obj.status, "Unknown")

from rest_framework import serializers
from .models import DistributorCustomer,  Order , Invoice , Payment , Branch , Stock , StockHistory

from user.models import User  # Ensure this is imported correctly

class DistributorCustomerSerializer(serializers.ModelSerializer):
    # Customer fields
    customer_email = serializers.EmailField(source="customer.email")
    customer_name = serializers.CharField(source="customer.get_full_name", read_only=True)

    # Distributor field (optional, you can adjust based on requirements)
    distributor_name = serializers.CharField(source="distributor.name", read_only=True)
    
    class Meta:
        model = DistributorCustomer
        fields = ["id", "customer_email", "customer_name", "distributor_name"]

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = "__all__"   


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"



class StockHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StockHistory
        fields = "__all__"


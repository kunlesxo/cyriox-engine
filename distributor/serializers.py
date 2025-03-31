from rest_framework import serializers
from .models import DistributorCustomer,  Order , Invoice , Payment , Branch , Stock , StockHistory



class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class DistributorCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributorCustomer
        fields = ['id', 'distributor', 'customer', 'created_at']
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

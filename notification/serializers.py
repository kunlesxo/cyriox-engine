from rest_framework import serializers
from .models import StockNotification

class StockNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockNotification
        fields = ["id", "message", "is_read", "created_at"]

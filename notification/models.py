from django.conf import settings
from django.db import models
from distributor.models import Stock

class StockNotification(models.Model):
    distributor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Low stock: {self.stock.product_name} ({self.stock.quantity} left)"

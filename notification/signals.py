from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from distributor.models import Stock
from .models import StockNotification

@receiver(post_save, sender=Stock)
def check_low_stock(sender, instance, **kwargs):
    if instance.quantity <= settings.LOW_STOCK_THRESHOLD:
        # Save notification in the database
        StockNotification.objects.create(
            distributor=instance.branch.distributor,
            stock=instance,
            message=f"⚠️ Low stock alert! {instance.product_name} has only {instance.quantity} items left."
        )

        # Send WebSocket alert
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "stock_updates",
            {
                "type": "stock_update",
                "message": f"⚠️ Low stock alert! {instance.product_name} has only {instance.quantity} items left.",
            },
        )

        # Send Email Alert
        subject = "Low Stock Alert 🚨"
        message = f"Dear {instance.branch.distributor.username},\n\n" \
                  f"Your stock for {instance.product_name} is running low ({instance.quantity} left). " \
                  f"Please restock to avoid running out.\n\n" \
                  f"Best regards,\nCyriox Team"

        send_mail(
            subject,
            message,
            "noreply@cyriox.com",
            [instance.branch.distributor.email],
            fail_silently=False,
        )

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import StockNotification
from .serializers import StockNotificationSerializer

class UnreadNotificationsView(generics.ListAPIView):
    serializer_class = StockNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StockNotification.objects.filter(distributor=self.request.user, is_read=False)

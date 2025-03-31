from django.urls import path
from .views import UnreadNotificationsView

urlpatterns = [
    path("unread/", UnreadNotificationsView.as_view(), name="unread-notifications"),
]

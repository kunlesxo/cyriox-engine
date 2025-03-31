from django.urls import path
from .views import (
    PaystackPaymentInitView,
    TransactionStatusView, paystack_webhook,
      VerifyPaystackPaymentView
)

urlpatterns = [
    # Function-based view for initializing payment

    # Class-based view for initializing payment
    path("paystack/init-class/", PaystackPaymentInitView.as_view(), name="paystack-initialize-class"),
    path("transaction-status/<str:reference>/", TransactionStatusView.as_view(), name="transaction-status"),
    path("paystack-webhook/", paystack_webhook, name="paystack-webhook"),  # Webhook
    path("verify-payment/<str:reference>/", VerifyPaystackPaymentView.as_view(), name="verify-payment"),  # Verify Paymentx

    # Payment verification endpoint
]



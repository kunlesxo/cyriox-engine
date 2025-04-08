from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Transaction
from .paystack import initialize_transaction, verify_transaction
from .serializers import PaystackPaymentSerializer, TransactionSerializer
from user.models import User
import requests
import logging
import hmac
import hashlib

logger = logging.getLogger(__name__)
User = get_user_model()

from rest_framework.permissions import IsAuthenticated


class PaystackPaymentInitView(APIView):
    """Initialize Paystack Payment"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaystackPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        amount = serializer.validated_data["amount"]
        user = request.user

        try:
            response = initialize_transaction(email, amount)
            if response.get("status"):
                transaction = Transaction.objects.create(
                    user=user,
                    reference=response["data"]["reference"],
                    amount=amount,
                    status="pending"
                )

                return Response({
                    "message": "Transaction initialized",
                    "authorization_url": response["data"]["authorization_url"],
                    "transaction": TransactionSerializer(transaction).data
                }, status=status.HTTP_200_OK)

            return Response({
                "error": "Paystack transaction initialization failed",
                "details": response
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error initializing Paystack transaction: {str(e)}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(["POST"])
def paystack_webhook(request):
    """Securely handle Paystack Webhook Events"""
    try:
        # Verify webhook signature
        signature = request.headers.get("X-Paystack-Signature")
        secret = settings.PAYSTACK_SECRET_KEY.encode()
        computed_hash = hmac.new(secret, request.body, hashlib.sha512).hexdigest()

        if signature != computed_hash:
            logger.warning("Invalid Paystack webhook signature.")
            return Response({"error": "Invalid signature"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        event = data.get("event")
        reference = data["data"].get("reference")

        transaction = Transaction.objects.filter(reference=reference).first()

        if not transaction:
            logger.warning(f"Webhook received for unknown reference: {reference}")
            return Response({"status": "ignored"}, status=status.HTTP_200_OK)

        if event == "charge.success":
            transaction.status = "success"
            transaction.paid_at = timezone.now()
            transaction.save()

            user = transaction.user
            user.has_made_payment = True
            user.save()

            logger.info(f"Transaction {reference} marked as successful via webhook.")

        elif event == "charge.failed":
            transaction.status = "failed"
            transaction.save()
            logger.info(f"Transaction {reference} marked as failed.")

        return Response({"status": "success"}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionStatusView(APIView):
    """Get Transaction Status by Reference"""

    def get(self, request, reference):
        transaction = Transaction.objects.filter(reference=reference).first()
        if not transaction:
            return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyPaystackPaymentView(APIView):
    """Verify Paystack Transaction via Reference"""

    def get(self, request, reference):
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)
        data = response.json()

        if data.get("status") and data["data"]["status"] == "success":
            transaction = Transaction.objects.filter(reference=reference).first()
            if transaction:
                transaction.status = "success"
                transaction.paid_at = timezone.now()
                transaction.save()

                user = transaction.user
                user.has_made_payment = True
                user.save()

            return Response({
                "message": "Payment verified successfully",
                "transaction": data["data"]
            }, status=status.HTTP_200_OK)

        return Response({
            "error": "Payment verification failed",
            "details": data
        }, status=status.HTTP_400_BAD_REQUEST)

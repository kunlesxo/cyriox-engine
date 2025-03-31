from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import get_user_model  
from .models import Transaction
from .paystack import initialize_transaction, verify_transaction
from .serializers import PaystackPaymentSerializer, TransactionSerializer
import logging
from user.models import User
import requests
from django.conf import settings


# Initialize logger
logger = logging.getLogger(__name__)

# Get custom user model
User = get_user_model()
from rest_framework.permissions import IsAuthenticated

class PaystackPaymentInitView(APIView):
    """Initialize Paystack Payment"""
    permission_classes = [IsAuthenticated]  # Enforce authentication

    def post(self, request):
        serializer = PaystackPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        amount = serializer.validated_data["amount"]
        user = request.user  # Get the authenticated user

        # Call Paystack API to initialize transaction
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
                    "authorization_url": response["data"]["authorization_url"],  # Send this to frontend
                    "transaction": TransactionSerializer(transaction).data
                }, status=status.HTTP_200_OK)

            return Response({
                "error": "Paystack transaction initialization failed",
                "details": response
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error initializing Paystack transaction: {str(e)}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def paystack_webhook(request):
    """Handle Paystack Webhook Events"""
    try:
        data = request.data
        event = data.get("event")

        if event == "charge.success":
            reference = data["data"]["reference"]
            transaction = Transaction.objects.filter(reference=reference).first()

            if transaction:
                transaction.status = "success"
                transaction.save()

                # Update user data (if needed)
                user = transaction.user
                user.has_made_payment = True  # Example field on the user model
                user.save()

                logger.info(f"Transaction {reference} marked as successful via webhook")

            else:
                logger.warning(f"Webhook received for unknown transaction reference: {reference}")

        return Response({"status": "success"}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error handling Paystack webhook: {str(e)}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TransactionStatusView(APIView):
    """Retrieve transaction status by reference"""

    def get(self, request, reference):
        transaction = Transaction.objects.filter(reference=reference).first()

        if not transaction:
            return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)

class VerifyPaystackPaymentView(APIView):
    """Verify Paystack Payment"""

    def get(self, request, reference):
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        
        response = requests.get(url, headers=headers)
        data = response.json()

        if data.get("status") and data["data"]["status"] == "success":
            # Update transaction status
            transaction = Transaction.objects.filter(reference=reference).first()
            if transaction:
                transaction.status = "success"
                transaction.save()

                # Update user data
                user = transaction.user
                user.has_made_payment = True  # Example field on the user model
                user.save()

            return Response({
                "message": "Payment verified successfully",
                "transaction": data["data"]
            }, status=status.HTTP_200_OK)

        return Response({
            "error": "Payment verification failed",
            "details": data
        }, status=status.HTTP_400_BAD_REQUEST)

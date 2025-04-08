from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import DistributorCustomer ,Order , Invoice , Payment , Branch , Stock , StockHistory
from .serializers import (
DistributorCustomerSerializer ,OrderSerializer , StockSerializer,InvoiceSerializer ,
StockHistorySerializer, PaymentSerializer ,  BranchSerializer
)
from django.contrib.auth import get_user_model

User = get_user_model()

class AssignCustomerToDistributorAPIView(generics.CreateAPIView):
    queryset = DistributorCustomer.objects.all()
    serializer_class = DistributorCustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        distributor_id = request.data.get("distributor")
        customer_id = request.data.get("customer")

        # Validate users
        try:
            distributor = User.objects.get(id=distributor_id, role="distributor")
            customer = User.objects.get(id=customer_id, role="user")
        except User.DoesNotExist:
            return Response({"error": "Invalid distributor or customer ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if customer is already assigned
        if DistributorCustomer.objects.filter(customer=customer).exists():
            return Response({"error": "Customer is already assigned to a distributor"}, status=status.HTTP_400_BAD_REQUEST)

        # Assign customer to distributor
        DistributorCustomer.objects.create(distributor=distributor, customer=customer)
        return Response({"message": "Customer assigned successfully"}, status=status.HTTP_201_CREATED)



class GetDistributorCustomersAPIView(generics.ListAPIView):
    serializer_class = DistributorCustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ensure only distributors can access their assigned customers
        if self.request.user.role == "Distributor":  # Adjust role comparison to match exactly
            distributor = getattr(self.request.user, 'distributor_profile', None)  # Access distributor profile
            if distributor:
                return DistributorCustomer.objects.filter(distributor=distributor)
        return DistributorCustomer.objects.none()  # Return empty queryset if no distributor found

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({"message": "No customers assigned"}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetDistributorOrdersAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "distributor":
            return Order.objects.filter(distributor=self.request.user)
        return Order.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No orders found"}, status=200)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=200)


   

    def patch(self, request, *args, **kwargs):
        order_id = kwargs.get("order_id")
        new_status = request.data.get("status")

        if new_status not in ["Pending", "Processing", "Shipped", "Delivered"]:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, distributor=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        order.status = new_status
        order.save()

        return Response({"message": "Order status updated successfully"}, status=status.HTTP_200_OK)


class GetDistributorInvoicesAPIView(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "distributor":
            return Invoice.objects.filter(distributor=self.request.user)
        return Invoice.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No invoices found"}, status=200)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=200)



class GetDistributorPaymentsAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "distributor":
            distributor_invoices = Invoice.objects.filter(distributor=self.request.user)
            return Payment.objects.filter(invoice__in=distributor_invoices)
        return Payment.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No payment history found"}, status=200)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=200)



class GetDistributorBranchesAPIView(generics.ListAPIView):
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "distributor":
            return Branch.objects.filter(distributor=self.request.user)
        return Branch.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No branches found"}, status=200)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=200)


class GetBranchStockAPIView(generics.ListAPIView):
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        branch_id = self.kwargs.get("branch_id")

        # Ensure the branch belongs to the logged-in distributor
        if self.request.user.role == "distributor":
            branch = Branch.objects.filter(id=branch_id, distributor=self.request.user).first()
            if branch:
                return Stock.objects.filter(branch=branch)

        return Stock.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No stock available for this branch"}, status=200)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=200)









class GetBranchOrdersAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        branch_id = self.kwargs.get("branch_id")

        # Ensure the branch belongs to the distributor
        if self.request.user.role == "distributor":
            return Order.objects.filter(branch__id=branch_id, branch__distributor=self.request.user)

        return Order.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No orders found for this branch"}, status=200)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=200)


class UpdateOrderStatusAPIView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        order_id = kwargs.get("order_id")

        try:
            order = Order.objects.get(id=order_id, branch__distributor=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found or unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        serializer = OrderSerializer(order, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Order status updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class AddStockAPIView(generics.CreateAPIView):

    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        branch_id = kwargs.get("branch_id")

        # Ensure branch belongs to distributor
        try:
            branch = Branch.objects.get(id=branch_id, distributor=request.user)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found or unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        data["branch"] = branch.id  
        serializer = StockSerializer(data=data)

        if serializer.is_valid():
            stock = serializer.save()
            StockHistory.objects.create(stock=stock, action="Added", quantity_changed=stock.quantity)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class UpdateStockAPIView(generics.UpdateAPIView):
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        stock_id = kwargs.get("stock_id")

        try:
            stock = Stock.objects.get(id=stock_id, branch__distributor=request.user)
        except Stock.DoesNotExist:
            return Response({"error": "Stock not found or unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        previous_quantity = stock.quantity
        serializer = StockSerializer(stock, data=request.data, partial=True)

        if serializer.is_valid():
            updated_stock = serializer.save()

            # Log stock change
            StockHistory.objects.create(
                stock=stock,
                action="Updated",
                quantity_changed=updated_stock.quantity - previous_quantity
            )

            # Broadcast update via WebSockets
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "stock_updates",
                {
                    "type": "stock_update",
                    "message": f"Stock for {updated_stock.product_name} updated to {updated_stock.quantity}",
                },
            )

            return Response({"message": "Stock updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteStockAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        stock_id = kwargs.get("stock_id")

        try:
            stock = Stock.objects.get(id=stock_id, branch__distributor=request.user)
        except Stock.DoesNotExist:
            return Response({"error": "Stock not found or unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        StockHistory.objects.create(stock=stock, action="Deleted", quantity_changed=-stock.quantity)
        stock.delete()
        return Response({"message": "Stock deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class CreateOrderAPIView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        branch_id = kwargs.get("branch_id")

        # Ensure branch exists
        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return Response({"error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        product_name = data.get("product_name")
        quantity_requested = int(data.get("quantity"))

        # Ensure stock is available
        try:
            stock = Stock.objects.get(branch=branch, product_name=product_name)
            if stock.quantity < quantity_requested:
                return Response({"error": "Not enough stock available"}, status=status.HTTP_400_BAD_REQUEST)
        except Stock.DoesNotExist:
            return Response({"error": "Product not found in this branch"}, status=status.HTTP_404_NOT_FOUND)

        # Reduce stock
        stock.quantity -= quantity_requested
        stock.save()

        # Log stock history
        StockHistory.objects.create(
            stock=stock, action="Order Placed", quantity_changed=-quantity_requested
        )

        # Save order
        data["branch"] = branch.id
        data["distributor"] = branch.distributor.id  
        data["customer"] = request.user.id  

        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Order created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetStockHistoryAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StockHistorySerializer

    def get_queryset(self):
        stock_id = self.kwargs.get("stock_id")
        return StockHistory.objects.filter(stock__id=stock_id)

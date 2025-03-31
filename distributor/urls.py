from django.urls import path
from .views import(
AssignCustomerToDistributorAPIView, GetDistributorOrdersAPIView , 
GetDistributorCustomersAPIView , UpdateOrderStatusAPIView,
GetDistributorInvoicesAPIView,  GetDistributorPaymentsAPIView,
GetDistributorBranchesAPIView, GetBranchStockAPIView,
AddStockAPIView, UpdateStockAPIView, DeleteStockAPIView,
CreateOrderAPIView, GetBranchOrdersAPIView , GetStockHistoryAPIView
)
    

    
 



urlpatterns = [
    path("assign-customer/", AssignCustomerToDistributorAPIView.as_view(), name="assign-customer"),
    path("distributor-customers/", GetDistributorCustomersAPIView.as_view(), name="distributor-customers"),
    path("distributor-orders/", GetDistributorOrdersAPIView.as_view(), name="distributor-orders"),
    path("distributor-invoices/", GetDistributorInvoicesAPIView.as_view(), name="distributor-invoices"),
    path("distributor-payments/", GetDistributorPaymentsAPIView.as_view(), name="distributor-payments"),
    path("distributor-branches/", GetDistributorBranchesAPIView.as_view(), name="distributor-branches"),
    path("branch-stock/<int:branch_id>/", GetBranchStockAPIView.as_view(), name="branch-stock"),
    path("add-stock/<int:branch_id>/", AddStockAPIView.as_view(), name="add-stock"),
    path("update-stock/<int:stock_id>/", UpdateStockAPIView.as_view(), name="update-stock"),
    path("delete-stock/<int:stock_id>/", DeleteStockAPIView.as_view(), name="delete-stock"),
    path("create-order/<int:branch_id>/", CreateOrderAPIView.as_view(), name="create-order"),
    path("branch-orders/<int:branch_id>/", GetBranchOrdersAPIView.as_view(), name="branch-orders"),
    path("update-order/<int:order_id>/", UpdateOrderStatusAPIView.as_view(), name="update-order"),
    path("stock-history/<int:stock_id>/", GetStockHistoryAPIView.as_view(), name="stock-history"),
]


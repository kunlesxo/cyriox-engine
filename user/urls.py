from django.urls import path
from .google import GoogleAuthView
from . import views

urlpatterns = [
    # Google Authentication
    path('google/', GoogleAuthView.as_view(), name="google-auth"),

    # General Authentication
    path('login/', views.LoginView.as_view(), name="login"),
    path('profile/', views.UserProfileView.as_view(), name="user-profile"),
    path('distributor/customers/', views.DistributorCustomerListView.as_view(), name='distributor_customers'),


    # Role-Specific Signup
    path('api/admin/signup/', views.AdminSignupView.as_view(), name='admin-signup'),
    path('distributor/signup/', views.DistributorSignupView.as_view(), name="distributor-signup"),
    path('user/signup/', views.UserSignupView.as_view(), name="user-signup"),
    path('change-password/', views.ChangePasswordView.as_view(), name="change-password"),
]

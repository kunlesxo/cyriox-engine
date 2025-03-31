import random
from django.conf import settings
from django.core.mail import send_mail

def send_otp_email(request, email):
    otp = random.randint(100000, 999999)  
    request.session["create_account_email"] = email
    request.session["create_account_otp"] = str(otp)  
    send_mail(
        'Create account OTP for Noqnoq',
        f'Your OTP for creating an account is {otp}. This OTP is valid for 5 minutes.',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False
    )
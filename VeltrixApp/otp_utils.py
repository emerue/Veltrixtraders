# otp_utils.py
import random
import string
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import timedelta

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(user, otp):
    """Send OTP verification email"""
    subject = 'Verify Your Email - Veltrixtraders'
    
    context = {
        'user': user,
        'otp': otp,
        'site_url': settings.SITE_URL,
        'expiry_minutes': 10
    }
    
    html_message = render_to_string('emails/otp_verification.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

def is_otp_valid(user, otp):
    """Check if OTP is valid and not expired (10 minutes expiry)"""
    if not user.email_otp or not user.email_otp_created_at:
        return False
    
    # Check if OTP matches
    if user.email_otp != otp:
        return False
    
    # Check if OTP is expired (10 minutes)
    expiry_time = user.email_otp_created_at + timedelta(minutes=10)
    if timezone.now() > expiry_time:
        return False
    
    return True
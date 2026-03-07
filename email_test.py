#!/usr/bin/env python
import os
import sys
import django

sys.path.append('/home/dell/Programs/python/gigs/Veltrixtraders')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Initialize Django
django.setup()

# Now import Django utilities
from django.core.mail import send_mail
from django.conf import settings

print(f"Using EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"Using EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"Using EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"Using DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# Send the email
try:
    send_mail(
        'Welcome to Veltrix Traders',
        'Thank you for joining our platform.',
        settings.DEFAULT_FROM_EMAIL,
        ['gabrielnworah6@gmail.com'],
        fail_silently=False,
    )
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Error sending email: {e}")
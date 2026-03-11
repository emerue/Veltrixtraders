# email_utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_welcome_email(user):
    """Send welcome email to new user"""
    subject = 'Welcome to Veltrixtraders!'
    html_message = render_to_string('emails/welcome.html', {
        'user': user,
        'site_url': settings.SITE_URL,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_deposit_confirmation_email(deposit):
    """Send deposit confirmation email"""
    subject = 'Deposit Request Received - Veltrixtraders'
    html_message = render_to_string('emails/deposit_confirmation.html', {
        'deposit': deposit,
        'user': deposit.user,
        'site_url': settings.SITE_URL,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [deposit.user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_withdrawal_confirmation_email(withdrawal):
    """Send withdrawal confirmation email"""
    subject = 'Withdrawal Request Received - Veltrixtraders'
    html_message = render_to_string('emails/withdrawal_confirmation.html', {
        'withdrawal': withdrawal,
        'user': withdrawal.user,
        'site_url': settings.SITE_URL,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [withdrawal.user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_deposit_status_update_email(deposit, old_status=None):
    """Send deposit status update email"""
    subject = f'Deposit {deposit.status.title()} - Veltrixtraders'
    html_message = render_to_string('emails/deposit_status.html', {
        'deposit': deposit,
        'user': deposit.user,
        'old_status': old_status,
        'site_url': settings.SITE_URL,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [deposit.user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_withdrawal_status_update_email(withdrawal, old_status=None):
    """Send withdrawal status update email"""
    subject = f'Withdrawal {withdrawal.status.title()} - Veltrixtraders'
    html_message = render_to_string('emails/withdrawal_status.html', {
        'withdrawal': withdrawal,
        'user': withdrawal.user,
        'old_status': old_status,
        'site_url': settings.SITE_URL,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [withdrawal.user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_password_reset_email(user, reset_url):
    """Send password reset email"""
    subject = 'Reset Your Password - Veltrixtraders'
    html_message = render_to_string('emails/password_reset.html', {
        'user': user,
        'reset_url': reset_url,
        'site_url': settings.SITE_URL,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_password_changed_email(user):
    """Send password changed confirmation email"""
    subject = 'Password Changed Successfully - Veltrixtraders'
    html_message = render_to_string('emails/password_changed.html', {
        'user': user,
        'site_url': settings.SITE_URL,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )
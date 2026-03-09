from django.shortcuts import render
# Create your views here.

def home(request):
    return render(request, 'home.html')

def construction(request):
    return render(request, 'construction.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def about(request):
    return render(request, 'about.html')

def software(request):
    return render(request, 'software.html')

def insight(request):
    return render(request, 'insight.html')

def copy_trading(request):
    return render(request, 'option-copy-trading.html')

def advance_trading(request):
    return render(request, 'advance-trading.html')

def live_trading(request):
    return render(request, 'live-trading.html')

def swing_trading(request):
    return render(request, 'swing-trading.html')

def feature_trading(request):
    return render(request, 'futures.html')

def options_trading(request):
    return render(request, 'option-trading.html')

def oil_and_gas(request):
    return render(request, 'oil-and-gas.html')

def terms_and_conditions(request):
    return render(request, 'terms-and-conditions.html')

def privacy_policy(request):
    return render(request, 'privacy-policy.html')

def forgot_password(request):
    return render(request, 'forgot-password.html')

def setup_user_info(request):
    return render(request, 'setup-user-info.html')

def setup_contact(request):
    return render(request, 'setup-contact.html')

def setup_experience(request):
    return render(request, 'setup-experience.html')

def setup_earnings(request):
    return render(request, 'setup-earnings.html')

def setup_declaration(request):
    return render(request, 'setup-declaration.html')

def logout(request):
    # Implement logout logic here
    return render(request, 'index.html')

import json
import os
from django.conf import settings
from django.shortcuts import render

def dashboard(request):
    # Load traders from JSON file
    traders = []
    json_file_path = os.path.join(settings.BASE_DIR, 'traders.json')
    
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            traders = data.get('traders', [])
    except FileNotFoundError:
        # Handle file not found - you might want to log this
        traders = []
    except json.JSONDecodeError:
        # Handle invalid JSON
        traders = []
    
    context = {
        'traders': traders,
    }
    return render(request, 'user/dashboard.html', context)

def copy_trading(request):
    # Load traders from JSON file
    traders = []
    json_file_path = os.path.join(settings.BASE_DIR, 'traders.json')
    
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            traders = data.get('traders', [])
    except FileNotFoundError:
        # Handle file not found - you might want to log this
        traders = []
    except json.JSONDecodeError:
        # Handle invalid JSON
        traders = []
    
    context = {
        'traders': traders,
    }
    return render(request, 'user/copytrading.html', context)

def copy_traders(request):
    # Load traders from JSON file
    traders = []
    json_file_path = os.path.join(settings.BASE_DIR, 'traders.json')
    
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            traders = data.get('traders', [])
    except FileNotFoundError:
        # Handle file not found - you might want to log this
        traders = []
    except json.JSONDecodeError:
        # Handle invalid JSON
        traders = []
    
    context = {
        'traders': traders,
    }
    return render(request, 'user/copytraders.html', context)

def deposit(request):
    return render(request, 'user/deposit.html')

def withdrawal(request):
    return render(request, 'user/withdrawal.html')

def technical_insights(request):
    return render(request, 'user/technical-insights.html')

def economic_calendar(request):
    return render(request, 'user/economic-calendar.html')

def loyalty_status(request):
    return render(request, 'user/loyalty-status.html')

def deposit_confirmation(request):
    
    wallet_address = "0x1234567890abcdef1234567890abcdef12345678"  # Replace with actual wallet address
    context = {
        'wallet_address': wallet_address,
    }
    return render(request, 'user/deposit-confirmation.html', context)

def transactions(request):
    return render(request, 'user/transactions.html')

def verification(request):
    return render(request, 'user/verification.html')

def login_history(request):
    return render(request, 'user/login-history.html')

def profile(request):
    return render(request, 'user/profile.html')

def referral(request):
    return render(request, 'user/referral.html')

def password(request):
    return render(request, 'user/password.html')

def two_factor(request):
    return render(request, 'user/two-factor.html')

def copy_trading_history(request):
    return render(request, 'user/copytrading-history.html')

def demo_history(request):
    return render(request, 'user/demo-history.html')

def demo(request):
    return render(request, 'user/demo.html')


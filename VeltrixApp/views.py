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
from django.contrib import admin
from django.urls import path
import VeltrixApp.views as views

urlpatterns = [
    path('', views.home, name='home'),
    path('construction/', views.construction, name='construction'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('about/', views.about, name='about'),
    path('software/', views.software, name='software'),
    path('insight/', views.insight, name='insight'),
    path('option-copy-trading/', views.copy_trading, name='copy_trading'),
    path('advance-trading/', views.advance_trading, name='advance_trading'),
    path('live-trading/', views.live_trading, name='live_trading'),
    path('swing-trading/', views.swing_trading, name='swing_trading'),
    path('futures/', views.feature_trading, name='feature_trading'),
    path('option-trading/', views.options_trading, name='options_trading'),
    path('oil-and-gas/', views.oil_and_gas, name='oil_and_gas'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
]
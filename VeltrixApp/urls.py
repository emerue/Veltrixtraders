from django.contrib import admin
from django.urls import path
import VeltrixApp.views as views

urlpatterns = [
    path('', views.home, name='home'),
    path('construction/', views.construction, name='construction'),
]
from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'home.html')

def construction(request):
    return render(request, 'construction.html')
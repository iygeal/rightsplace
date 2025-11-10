from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    """Simple homepage view"""
    return HttpResponse("Welcome to RightsPlace! The backend is running successfully.")

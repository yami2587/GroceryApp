from django.http import JsonResponse
from django.contrib.auth import logout
from django.shortcuts import redirect

def home(request):
    return JsonResponse({"message": "Welcome to Grocery API!"})

def logout_view(request):
    logout(request)
    return redirect('home')

from django.urls import path, include
from .views import RegisterView, ProfileView, ToggleManagerView
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('profile/', ProfileView.as_view(), name='auth-profile'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('toggle-manager/', ToggleManagerView.as_view(), name='toggle-manager'),
]

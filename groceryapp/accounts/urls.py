from django.urls import path, include
from .views import RegisterView, ProfileView, ToggleManagerView
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('profile/', ProfileView.as_view(), name='auth-profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('toggle-manager/', ToggleManagerView.as_view(), name='toggle-manager'),
     # API
    path('api/register/', views.RegisterView.as_view(), name='api_register'),
    path('api/profile/', views.ProfileView.as_view(), name='api_profile'),
    path('api/toggle-manager/', views.ToggleManagerView.as_view(), name='api_toggle_manager'),
     path("manager/dashboard/", views.manager_dashboard, name="manager_dashboard"),
]

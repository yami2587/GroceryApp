from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})
class ProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# small convenience endpoint to flip manager role (protected)

class ToggleManagerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.user.is_superuser:
            return Response({"detail":"Only superuser can toggle roles."}, status=status.HTTP_403_FORBIDDEN)
        username = request.data.get("username")
        try:
            target = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"detail":"user not found"}, status=status.HTTP_404_NOT_FOUND)
        target.is_manager = not target.is_manager
        target.save()
        return Response({"username": target.username, "is_manager": target.is_manager})
    
def logout_view(request):
    logout(request)
    return redirect('login')


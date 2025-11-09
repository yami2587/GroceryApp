from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from .serializers import RegisterSerializer, UserSerializer
from .forms import RegisterForm  #my form
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from products.models import Product
from orders.models import Order
from django.shortcuts import get_object_or_404
from .models import Address

User = get_user_model()
# ---------------
class RegisterView(generics.CreateAPIView):
  
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class ProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ToggleManagerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.user.is_superuser:
            return Response({"detail": "Only superuser can toggle roles."}, status=status.HTTP_403_FORBIDDEN)
        username = request.data.get("username")
        try:
            target = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"Detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        target.role = "manager" if target.role != "manager" else "customer"
        target.save()
        return Response({"username": target.username, "role": target.role})
    
def is_manager(user):
    return user.is_authenticated and  user.role == 'manager'

@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):
    products = Product.objects.all()
    low_stock = products.filter(stock__lt=5)
    total_products = products.count()
    total_low_stock = low_stock.count()

    context = {
        "products": products,
        "low_stock": low_stock,
        "total_products": total_products,
        "total_low_stock": total_low_stock,
    }
    return render(request, "products/manager_dashboard.html", context)

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")

            # Redirect by role
            if user.role == 'manager':
                return redirect('manager_dashboard')
            else:
                return redirect('product_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.role == 'manager':
                return redirect('manager_dashboard')
            else:
                return redirect('product_list')
        else:
            messages.error(request, "Invalid credentials. Try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'accounts/address_list.html', {'addresses': addresses})

# @login_required
# def address_add(request):
#     if request.method == 'POST':
#         Address.objects.create(
#             user=request.user,
#             full_name=request.POST['full_name'],
#             phone=request.POST['phone'],
#             house_no=request.POST['house_no'],
#             street=request.POST['street'],
#             city=request.POST['city'],
#             state=request.POST['state'],
#             pincode=request.POST['pincode'],
#             landmark=request.POST.get('landmark', ''),
#             default=('default' in request.POST)
#         )
#         return redirect('address_list')
#     return render(request, 'accounts/address_form.html')
@login_required
def address_add(request):
    if request.method == 'POST':
        Address.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name', ''),
            phone=request.POST.get('phone', ''),
            house_no=request.POST.get('house_no', ''),
            street=request.POST.get('street', ''),
            city=request.POST.get('city', ''),
            state=request.POST.get('state', ''),
            pincode=request.POST.get('pincode', ''),
            landmark=request.POST.get('landmark', ''),
            default=('default' in request.POST)
        )
        return redirect('address_list')

    empty_addr = Address(
        full_name='',
        phone='',
        house_no='',
        street='',
        city='',
        state='',
        pincode='',
        landmark='',
    )
    return render(request, 'accounts/address_form.html', {'addr': empty_addr})


@login_required
def address_edit(request, pk):
    addr = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        addr.full_name = request.POST.get('full_name', '')
        addr.phone = request.POST.get('phone', '')
        addr.house_no = request.POST.get('house_no', '')
        addr.street = request.POST.get('street', '')
        addr.city = request.POST.get('city', '')
        addr.state = request.POST.get('state', '')
        addr.pincode = request.POST.get('pincode', '')
        addr.landmark = request.POST.get('landmark', '')
        addr.default = 'default' in request.POST
        addr.save()
        messages.success(request, "Address updated successfully.")
        return redirect('address_list')
    return render(request, 'accounts/address_form.html', {'addr': addr})


@login_required
def address_delete(request, pk):
    addr = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        addr.delete()
        messages.info(request, "Address deleted.")
        return redirect('address_list')
    return render(request, 'accounts/address_confirm_delete.html', {'addr': addr})

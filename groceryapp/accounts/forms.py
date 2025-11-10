from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Address
#form for address model
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'house_no', 'street', 'city', 'state', 'pincode', 'landmark', 'default']
#form for user registration
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

from django import forms
from .models import Product
#form for product model
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'stock', 'description', 'image','image_url']
        

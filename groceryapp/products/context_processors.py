from .models import Product

def product_categories(request):
    return {"CATEGORY_CHOICES": Product.CATEGORY_CHOICES}

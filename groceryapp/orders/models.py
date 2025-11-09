from django.db import models
from django.conf import settings
from products.models import Product
from django.utils import timezone
from django.core.validators import MinValueValidator

User = settings.AUTH_USER_MODEL

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','product')

    def __str__(self):
        return f"{self.user} - {self.product} x {self.quantity}"

class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','product')
        
class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30, blank=True)
    address_line1 = models.CharField(max_length=255)
    street = models.CharField(max_length=255,blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='India')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} • {self.address_line1}"
    
class PromoCode(models.Model):
    code = models.CharField(max_length=32, unique=True)
    discount_percent = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.active:
            return False
        if self.expires_at and now > self.expires_at:
            return False
        return True


    def __str__(self):
        return f"{self.code} - {self.discount_percent}%"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    shipping_address = models.ForeignKey(ShippingAddress, null=True, blank=True, on_delete=models.SET_NULL ,)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    promo_code = models.ForeignKey(PromoCode, null=True, blank=True, on_delete=models.SET_NULL)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_when_bought = models.DecimalField(max_digits=10, decimal_places=2)
    

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid = models.BooleanField(default=False)
    method = models.CharField(max_length=50, default='simulated')
    created_at = models.DateTimeField(auto_now_add=True)


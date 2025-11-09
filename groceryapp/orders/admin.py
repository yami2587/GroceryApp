from django.contrib import admin
from .models import CartItem, Order, OrderItem, WishlistItem , PromoCode, Payment

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user','product','quantity','added_at')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product','quantity','price_when_bought')
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','user','total_price','created_at')
    inlines = [OrderItemInline]

@admin.register(WishlistItem)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user','product','added_at')

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'active', 'expires_at')
    list_filter = ('active',)
    search_fields = ('code',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order','amount','paid','method','created_at')

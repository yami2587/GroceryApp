from rest_framework import serializers
from .models import CartItem, Order, OrderItem, WishlistItem
from products.serializers import ProductListSerializer
from products.models import Product
#cart item 
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, source='product')

    class Meta:
        model = CartItem
        fields = ('id','product','product_id','quantity','added_at')

# class WishlistSerializer(serializers.ModelSerializer):
#     product = ProductListSerializer(read_only=True)
#     product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, source='product')

#     class Meta:
#         model = WishlistItem
#         fields = ('id','product','product_id','added_at')
#order item return
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ('product','quantity','price_when_bought')
#order serializer
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ('id','total_price','created_at','items')

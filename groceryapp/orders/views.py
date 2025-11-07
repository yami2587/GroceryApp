from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404 , render, redirect
from .models import CartItem, Order, OrderItem, WishlistItem ,PromoCode, Payment
from .serializers import CartItemSerializer, OrderSerializer, WishlistSerializer
from products.models import Product
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.urls import reverse 



class CartListView(generics.ListAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related('product')

class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        qty = int(request.data.get('quantity', 1))
        product = get_object_or_404(Product, pk=product_id)
        if product.stock < qty:
            return Response({"detail":"Not enough stock"}, status=status.HTTP_400_BAD_REQUEST)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += qty
        else:
            cart_item.quantity = qty
        cart_item.save()
        return Response(CartItemSerializer(cart_item).data)

class RemoveFromCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        try:
            item = CartItem.objects.get(user=request.user, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response({"detail":"Item not found in cart"}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response({"detail":"removed"})

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
   
        promo_code_str = request.POST.get('promo_code') or request.data.get('promo_code')

        # your normal checkout flow logic here...
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=400)

        total_price = sum(item.product.price * item.quantity for item in cart_items)

        # Apply promo code discount
        discount = 0
        if promo_code_str:
            promo = PromoCode.objects.filter(code=promo_code_str, active=True).first()
            if promo:
                discount = (promo.discount_percent / 100) * total_price

        final_price = total_price - discount

        order = Order.objects.create(user=request.user, total_price=final_price)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_when_bought=item.product.price,
            )
            item.product.stock -= item.quantity
            item.product.save()
        cart_items.delete()

        return Response({
            "message": "Order placed successfully!",
            "total": total_price,
            "discount": discount,
            "final_price": final_price
        }, status=201)


# Wishlist
class WishlistListView(generics.ListAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user).select_related('product')

class AddWishlistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        obj, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
        return Response(WishlistSerializer(obj).data)

class RemoveWishlistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        try:
            obj = WishlistItem.objects.get(user=request.user, product_id=product_id)
            obj.delete()
            return Response({"detail":"removed"})
        except WishlistItem.DoesNotExist:
            return Response({"detail":"not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
 #     Cart page  
class CartPageView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
        }
        return render(request, 'orders/cart.html', context)

#     Add to cart via form (POST)  
class AddToCartViewUI(LoginRequiredMixin, View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        qty = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, pk=product_id)
        if product.stock < qty:
            messages.error(request, "Not enough stock for that product.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += qty
        else:
            cart_item.quantity = qty
        cart_item.save()
        messages.success(request, f"Added {product.name} (x{qty}) to cart.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

#     Remove item from cart (POST)  
class RemoveFromCartViewUI(LoginRequiredMixin, View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        try:
            item = CartItem.objects.get(user=request.user, product_id=product_id)
            item.delete()
            messages.success(request, "Removed item from cart.")
        except CartItem.DoesNotExist:
            messages.error(request, "Item not found in cart.")
        return redirect(reverse('cart-page'))

#     Checkout page (GET shows summary, POST performs checkout transaction)  
class CheckoutPageView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        if not cart_items.exists():
            messages.info(request, "Your cart is empty.")
            return redirect('/')
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
        }
        return render(request, 'orders/checkout.html', context)

    @transaction.atomic
    def post(self, request):
        user = request.user
        cart_items = CartItem.objects.select_for_update().filter(user=user).select_related('product')
        if not cart_items.exists():
            messages.error(request, "Cart empty.")
            return redirect('/')
        # validate stock
        for item in cart_items:
            if item.product.stock < item.quantity:
                messages.error(request, f"Product {item.product.name} out of stock or insufficient quantity.")
                return redirect('cart-page')

        total = sum(item.product.price * item.quantity for item in cart_items)
        order = Order.objects.create(user=user, total_price=total)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_when_bought=item.product.price
            )
            # update product stock and sold_count
            p = item.product
            p.stock = p.stock - item.quantity
            p.sold_count = p.sold_count + item.quantity
            p.save()
        cart_items.delete()
        messages.success(request, "Order placed successfully!")
        return redirect('order-success', pk=order.id)

#     Order success page  
class OrderSuccessView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        return render(request, 'orders/order_success.html', {'order': order})

class MyOrdersView(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'orders/my_orders.html', {'orders': orders})

class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        return render(request, 'orders/order_detail.html', {'order': order})

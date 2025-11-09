from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from .models import CartItem, Order, OrderItem, WishlistItem, PromoCode, Payment , ShippingAddress
# from .serializers import CartItemSerializer, OrderSerializer, WishlistSerializer
from .serializers import CartItemSerializer, OrderSerializer
from products.models import Product
from accounts.models import Address
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_GET
from django.http import JsonResponse


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
            return Response({"detail": "Not enough stock"}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        cart_item.quantity = cart_item.quantity + qty if not created else qty
        cart_item.save()
        return Response(CartItemSerializer(cart_item).data)


class RemoveFromCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        try:
            item = CartItem.objects.get(user=request.user, product_id=product_id)
            item.delete()
            return Response({"detail": "removed"})
        except CartItem.DoesNotExist:
            return Response({"detail": "Item not found"}, status=404)

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        promo_code_str = request.POST.get('promo_code') or request.data.get('promo_code')
        address_id = request.data.get('address_id')

        # address check
        if not address_id:
            return Response({'error': 'Address required'}, status=400)

        address = get_object_or_404(Address, pk=address_id, user=request.user)
        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items.exists():
            return Response({'error': 'Cart empty'}, status=400)

        total = sum(item.product.price * item.quantity for item in cart_items)
        discount = Decimal(0)

        if promo_code_str:
            promo = PromoCode.objects.filter(code__iexact=promo_code_str, active=True).first()
            if promo and promo.is_valid():
                discount = (promo.discount_percent / Decimal(100)) * total

        final_total = total - discount

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                total_price=final_total,
                address=address
            )

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
            "total": total,
            "discount": float(discount),
            "final_price": float(final_total),
        }, status=201)


# class WishlistListView(generics.ListAPIView):
#     serializer_class = WishlistSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return WishlistItem.objects.filter(user=self.request.user).select_related('product')


# class AddWishlistView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         product_id = request.data.get('product_id')
#         product = get_object_or_404(Product, pk=product_id)
#         obj, _ = WishlistItem.objects.get_or_create(user=request.user, product=product)
#         return Response(WishlistSerializer(obj).data)


# class RemoveWishlistView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         product_id = request.data.get('product_id')
#         try:
#             obj = WishlistItem.objects.get(user=request.user, product_id=product_id)
#             obj.delete()
#             return Response({"detail": "removed"})
#         except WishlistItem.DoesNotExist:
#             return Response({"detail": "not found"}, status=404)


class CartPageView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        return render(request, 'orders/cart.html', {'cart_items': cart_items, 'subtotal': subtotal})


class AddToCartViewUI(LoginRequiredMixin, View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        qty = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, pk=product_id)

        if product.stock < qty:
            messages.error(request, "Not enough stock for that product.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        cart_item.quantity = cart_item.quantity + qty if not created else qty
        cart_item.save()
        messages.success(request, f"Added {product.name} (x{qty}) to cart.")
        return redirect(request.META.get('HTTP_REFERER', '/'))


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



class CheckoutPageView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        addresses = Address.objects.filter(user=request.user)

        if not cart_items.exists():
            messages.info(request, "Your cart is empty.")
            return redirect('/')

        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        return render(request, 'orders/checkout.html', {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'addresses': addresses
        })

    @transaction.atomic
    def post(self, request):
        user = request.user
        address_id = request.POST.get('address_id')
        promo_code_str = request.POST.get('promo_code', '').strip()

        if not address_id:
            messages.error(request, "Please select a shipping address.")
            return redirect('checkout-page')

        address = get_object_or_404(Address, id=address_id, user=user)

        shipping_address = ShippingAddress.objects.create(
            user=user,
            full_name=address.full_name,
            phone=address.phone,
            street=address.street,
            city=address.city,
            state=address.state,
            postal_code=address.pincode,
            country=address.country
        )

        cart_items = CartItem.objects.select_for_update().filter(user=user).select_related('product')

        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('cart-page')

        # Stock validation
        for item in cart_items:
            if item.product.stock < item.quantity:
                messages.error(request, f"{item.product.name} out of stock.")
                return redirect('cart-page')

        total = sum(item.product.price * item.quantity for item in cart_items)
        discount = Decimal(0)
        if promo_code_str:
            promo = PromoCode.objects.filter(code__iexact=promo_code_str, active=True).first()
            if promo and promo.is_valid():
                discount = (promo.discount_percent / Decimal(100)) * total
                applied_promo = promo
            else:
                applied_promo = None
        else:
            applied_promo = None

        final_total = total - discount
        order = Order.objects.create(
            user=user,
            total_price=final_total,
            shipping_address=shipping_address,
            promo_code=applied_promo,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_when_bought=item.product.price
            )
            p = item.product
            p.stock -= item.quantity
            p.sold_count += item.quantity
            p.save()

        cart_items.delete()
        messages.success(request, "Order placed successfully!")
        return redirect('order-success', pk=order.id)

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


class PaymentView(LoginRequiredMixin, View):
    def post(self, request):
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, pk=order_id, user=request.user)

      
        payment = Payment.objects.create(
            order=order,
            amount=order.total_price,
            paid=True,
            method='Simulated'
        )

        order.status = 'PAID'
        order.save()

        messages.success(request, "Payment successful!")
        return redirect('order-success', pk=order.id)



@require_GET
def validate_promo(request):
    code = request.GET.get('code', '').strip()
    try:
        promo = PromoCode.objects.get(code__iexact=code)
        valid = promo.is_valid()
        return JsonResponse({'valid': valid, 'discount_percent': promo.discount_percent if valid else 0})
    except PromoCode.DoesNotExist:
        return JsonResponse({'valid': False, 'discount_percent': 0})

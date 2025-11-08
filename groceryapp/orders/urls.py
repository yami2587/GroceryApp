from django.urls import path
from .views import (
    CartListView, AddToCartView, RemoveFromCartView, CheckoutView,
    WishlistListView, AddWishlistView, RemoveWishlistView , validate_promo
)

urlpatterns = [
    path('cart/', CartListView.as_view(), name='cart-list'),
    path('cart/add/', AddToCartView.as_view(), name='cart-add'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='cart-remove'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),

    path('wishlist/', WishlistListView.as_view(), name='wishlist-list'),
    path('wishlist/add/', AddWishlistView.as_view(), name='wishlist-add'),
    path('wishlist/remove/', RemoveWishlistView.as_view(), name='wishlist-remove'),
    path('wishlist-ui/', WishlistListView.as_view(), name='wishlist-ui'),
path('wishlist/remove-ui/', RemoveWishlistView.as_view(), name='wishlist-remove'),
path('promo/validate/', validate_promo, name='promo-validate'),

]

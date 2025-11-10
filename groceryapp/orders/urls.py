from django.urls import path
from . import views
from .views import (
    CartListView, AddToCartView, RemoveFromCartView, CheckoutView,
validate_promo, CheckoutPageView, OrderSuccessView, MyOrdersView, OrderDetailView

)

urlpatterns = [
    # Cart and Checkout
    path('cart/', CartListView.as_view(), name='cart-list'),
    path('cart/add/', AddToCartView.as_view(), name='cart-add'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='cart-remove'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
 # Wishlist Management   
#     path('wishlist/', WishlistListView.as_view(), name='wishlist-list'),
#     path('wishlist/add/', AddWishlistView.as_view(), name='wishlist-add'),
#     path('wishlist/remove/', RemoveWishlistView.as_view(), name='wishlist-remove'),
#     path('wishlist-ui/', WishlistListView.as_view(), name='wishlist-ui'),
# path('wishlist/remove-ui/', RemoveWishlistView.as_view(), name='wishlist-remove'),

    # Order Success and User Orders
    path('order-success/<int:pk>/', OrderSuccessView.as_view(), name='order-success'),
    path('my-orders/', MyOrdersView.as_view(), name='my-orders'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('validate-promo/', views.validate_promo, name='validate-promo'),
    path('manager/sales-dashboard/', views.manager_sales_dashboard, name='manager-sales-dashboard'),
    path('manager/order/<int:order_id>/update/', views.update_order_status, name='update-order-status'),




]

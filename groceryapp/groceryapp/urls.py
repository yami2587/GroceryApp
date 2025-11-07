from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from products.views import home
from orders.views import CartPageView, AddToCartViewUI, RemoveFromCartViewUI, CheckoutPageView, OrderSuccessView
from groceryapp.views import logout_view
from products.views import product_detail
from orders.views import MyOrdersView, OrderDetailView
from products.views import low_stock_alert , product_increment_stock , sales_report

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', home, name='home'), 
    path('accounts/', include('accounts.urls')),
    path('logout/', logout_view, name='logout'),
    path('api/', include('products.urls')),
    
    path('api/auth/', include('rest_framework.urls')), 
    
    
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('product/<int:pk>/', product_detail, name='product-detail'),
    #cart items
    path('cart/', CartPageView.as_view(), name='cart-page'),
    path('cart/add/', AddToCartViewUI.as_view(), name='cart-add-ui'),
    path('cart/remove/', RemoveFromCartViewUI.as_view(), name='cart-remove-ui'),
    path('checkout/', CheckoutPageView.as_view(), name='checkout-page'),
    path('order/success/<int:pk>/', OrderSuccessView.as_view(), name='order-success'),
    
    path('my-orders/', MyOrdersView.as_view(), name='my-orders'),
path('my-orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),

    path('low-stock/', low_stock_alert, name='low-stock-alert'),
    path('product/<int:pk>/increment-stock/', product_increment_stock, name='product-increment-stock'),
    path('sales-report/', sales_report, name='sales-report'),




]


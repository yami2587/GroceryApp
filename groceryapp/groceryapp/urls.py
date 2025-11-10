from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from products.views import home
from orders.views import CartPageView, AddToCartViewUI, RemoveFromCartViewUI, CheckoutPageView, OrderSuccessView
from groceryapp.views import logout_view
from products.views import product_detail
from orders.views import MyOrdersView, OrderDetailView
from products.views import low_stock_alert , manager_product_restock , sales_report
from django.conf import settings
from django.conf.urls.static import static
from products import views as product_views


urlpatterns = [
    #admin site
    path('admin/', admin.site.urls),
     path('', product_views.home, name='product_list'),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path("products/", include("products.urls")),
    path('logout/', logout_view, name='logout'),
    path('orders/', include('orders.urls')), 
    
    # API endpoints 
    # path('api/', include('products.urls')),
    # path('api/products/', include('products.urls')),
    # path('api/orders/', include('orders.urls')),
    path('api/auth/', include('rest_framework.urls')), 
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    #cart items
    path('product/<int:pk>/', product_detail, name='product-detail'),
    path('cart/', CartPageView.as_view(), name='cart-page'),
    path('cart/add/', AddToCartViewUI.as_view(), name='cart-add-ui'),
    path('cart/remove/', RemoveFromCartViewUI.as_view(), name='cart-remove-ui'),
    path('checkout/', CheckoutPageView.as_view(), name='checkout-page'),
    path('order/success/<int:pk>/', OrderSuccessView.as_view(), name='order-success'),
    #user orders
    path('my-orders/', MyOrdersView.as_view(), name='my-orders'),
path('my-orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    #manager views
    path('low-stock/', low_stock_alert, name='low-stock-alert'),
    path('product/<int:pk>/increment-stock/', manager_product_restock, name='product-increment-stock'),
    
    #sales report
    path('sales-report/', sales_report, name='sales-report'),




]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from rest_framework.routers import DefaultRouter
from .views import ProductViewSet
from django.urls import path , include
from . import views
from products.views import sales_report
from products.views import low_stock_alert, manager_product_restock


router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
urlpatterns = router.urls

urlpatterns += [
    path('product/<int:pk>/', views.product_detail, name='product-detail'),
    path('', views.home, name='product_list'),

    # Manager 
    path('manager/products/', views.manager_product_list, name='manager-product-list'),
    path("manager/add/", views.manager_product_add, name="manager_product_add"),
    path("manager/<int:pk>/edit/", views.manager_product_edit, name="manager_product_edit"),
    path("manager/<int:pk>/delete/", views.manager_product_delete, name="manager_product_delete"),
    path("manager/<int:pk>/restock/", views.manager_product_restock, name="manager_product_restock"),

    # Alerts
    path('manager/low-stock/', views.low_stock_alert, name='low-stock-alert'),
    path('sales-report/', sales_report, name='sales-report'),
]

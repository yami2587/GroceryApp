from rest_framework.routers import DefaultRouter
from .views import ProductViewSet
from django.urls import path , include
from . import views

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
urlpatterns = router.urls

urlpatterns += [
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product-detail'),
    
    # Manager 
    
    path('manager/products/', views.manager_product_list, name='manager-product-list'),
 path("manager/add/", views.manager_product_add, name="manager_product_add"),
    path("manager/<int:pk>/edit/", views.manager_product_edit, name="manager_product_edit"),
    path("manager/<int:pk>/delete/", views.manager_product_delete, name="manager_product_delete"),
    path("manager/<int:pk>/restock/", views.manager_product_restock, name="manager_product_restock"),
    # path('manager/products/<int:pk>/edit/', views.manager_product_edit, name='manager-product-edit'),
    # path('manager/products/<int:pk>/delete/', views.manager_product_delete, name='manager-product-delete'),
    # path('manager/products/<int:pk>/restock/', views.manager_product_restock, name='manager-product-restock'),

    # alwrts
    path('manager/low-stock/', views.low_stock_alert, name='low-stock-alert'),
    path('manager/sales-report/', views.sales_report, name='sales-report'),

]
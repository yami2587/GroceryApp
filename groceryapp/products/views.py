from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django import forms
from django.db.models import Q, F, Sum, ProtectedError
from django.utils.timezone import now

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import ProductListSerializer, ProductDetailSerializer
from .permissions import IsManager
from products.models import Product
from orders.models import Order, OrderItem
from django.db.models.functions import TruncMonth



#is manager check
def is_manager(user):
    return user.is_authenticated and getattr(user, 'role', '') == 'manager'

#manager decorator
def manager_required(view_func):
    return user_passes_test(is_manager)(view_func)

#home view with search, filter, pagination
def home(request):
    qs = Product.objects.all()
    q = request.GET.get('q')
    category = request.GET.get('category')
    ordering = request.GET.get('ordering')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if category:
        qs = qs.filter(category=category)
    if min_price:
        try:
            qs = qs.filter(price__gte=float(min_price))
        except:
            pass
    if max_price:
        try:
            qs = qs.filter(price__lte=float(max_price))
        except:
            pass
    if ordering:
        qs = qs.order_by(ordering)

    paginator = Paginator(qs, 12)
    page = request.GET.get('page', 1)
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    return render(request, "products/list.html", {
        "products": products_page,
        "paginator": paginator,
        "page_obj": products_page,
    })

#product detail view
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(id=pk)[:4]
    return render(request, 'products/detail.html', {
        'product': product,
        'related_products': related_products
    })

#product view
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'sold_count', 'created_at']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ProductListSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManager()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def most_popular(self, request):
        top_n = int(request.query_params.get('n', 10))
        qs = Product.objects.all().order_by('-sold_count')[:top_n]
        serializer = ProductListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        cat = request.query_params.get('category')
        if not cat:
            return Response({"detail": "provide ?category=<category>"}, status=status.HTTP_400_BAD_REQUEST)
        qs = Product.objects.filter(category=cat)
        serializer = ProductListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def increment_stock(self, request, pk=None):
        user = request.user
        if not (user.is_authenticated and getattr(user, 'role', '') == 'manager'):
            return Response({"detail": "unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        amount = int(request.data.get('amount', 1))
        product = self.get_object()
        product.stock = F('stock') + amount
        product.save()
        product.refresh_from_db()
        return Response({"id": product.id, "stock": product.stock})

#product form 
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock', 'image_url', 'image']

#manager product list retun view
@manager_required
def manager_product_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'products/manager_all_products.html', {'products': products})

#manager product add view
@manager_required
def manager_product_add(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, " Product added successfully!")
            return redirect("manager-product-list")
    else:
        form = ProductForm()
    return render(request, "products/manager_add_product.html", {"form": form})

#product edit by manager
@manager_required
def manager_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, " Product updated successfully!")
            return redirect("manager-product-list")
    else:
        form = ProductForm(instance=product)
    return render(request, "products/manager_edit_product.html", {"form": form, "product": product})

#delete product manager
@manager_required
def manager_product_delete(request, pk):
    p = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        try:
            p.delete()
            messages.success(request, "Product deleted successfully.")
        except ProtectedError:
            messages.error(request, " Cannot delete: product linked to existing orders.")
        return redirect('manager-product-list')
    return render(request, 'products/manager_delete.html', {'product': p})

#product restock view
@manager_required
def manager_product_restock(request, pk):
    p = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        amount = int(request.POST.get('amount', 0))
        if amount > 0:
            p.stock += amount
            p.save()
            messages.success(request, f"📦 Restocked {p.name} by {amount} units.")
        return redirect('manager-product-list')
    return render(request, 'products/manager_restock.html', {'product': p})
#sales report view
@manager_required
def sales_report(request):
    filter_type = request.GET.get('filter', 'most_sold')
    report = Product.objects.annotate(total_sold=Sum('orderitem__quantity'))

    if filter_type == 'least_sold':
        report = report.order_by('total_sold')
    elif filter_type == 'category':
        report = report.order_by('category')
    else:  
        report = report.order_by('-total_sold')

    return render(request, 'reports/sales_report.html', {'report': report, 'filter': filter_type})
#low stock alert view
@manager_required
def low_stock_alert(request):
    low_products = Product.objects.filter(stock__lt=5).order_by('stock')
    return render(request, "products/low_stock.html", {"low_products": low_products})



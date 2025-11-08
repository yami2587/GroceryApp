from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import F, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django import forms
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import ProductListSerializer, ProductDetailSerializer
from .permissions import IsManager
from products.models import Product
from orders.models import Order




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


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(id=pk)[:4]
    return render(request, 'products/detail.html', {
        'product': product,
        'related_products': related_products
    })


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


def manager_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and getattr(u, 'role', '') == 'manager')(view_func)


@manager_required
def low_stock_alert(request):
    threshold = int(request.GET.get('threshold', 5))
    low_products = Product.objects.filter(stock__lte=threshold).order_by('stock')
    return render(request, 'products/low_stock.html', {'low_products': low_products, 'threshold': threshold})


@require_POST
@manager_required
def product_increment_stock(request, pk):
    amount = int(request.POST.get('amount', 1))
    p = get_object_or_404(Product, pk=pk)
    p.stock += amount
    p.save()
    return redirect('low-stock-alert')


@manager_required
def sales_report(request):
    order = request.GET.get('order', 'most')
    category = request.GET.get('category')
    qs = Product.objects.all()
    if category:
        qs = qs.filter(category=category)
    qs = qs.order_by('sold_count' if order == 'least' else '-sold_count')
    return render(request, 'products/sales_report.html', {'products': qs})



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock', 'image_url']


@manager_required
def manager_product_list(request):
    qs = Product.objects.all().order_by('-created_at')
    return render(request, 'products/manager_list.html', {'products': qs})


@manager_required
def manager_product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added")
            return redirect('manager-product-list')
    else:
        form = ProductForm()
    return render(request, 'products/manager_form.html', {'form': form, 'action': 'Add'})


@manager_required
def manager_product_edit(request, pk):
    p = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated")
            return redirect('manager-product-list')
    else:
        form = ProductForm(instance=p)
    return render(request, 'products/manager_form.html', {'form': form, 'action': 'Edit'})


@manager_required
def manager_product_delete(request, pk):
    p = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        p.delete()
        messages.success(request, "Product deleted")
        return redirect('manager-product-list')
    return render(request, 'products/manager_delete.html', {'product': p})


@manager_required
def manager_product_restock(request, pk):
    p = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        amount = int(request.POST.get('amount', 0))
        if amount > 0:
            p.stock += amount
            p.save()
            messages.success(request, f"Restocked {p.name} by {amount}")
        return redirect('manager-product-list')
    return render(request, 'products/manager_restock.html', {'product': p})

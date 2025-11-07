from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import F ,Q
from .models import Product
from django.contrib.auth.decorators import user_passes_test
from .serializers import ProductListSerializer, ProductDetailSerializer
from .permissions import IsManager
from rest_framework import status
from django.shortcuts import render, get_object_or_404 , redirect
from django.views.decorators.http import require_POST
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend

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
        try: qs = qs.filter(price__gte=float(min_price))
        except: pass
    if max_price:
        try: qs = qs.filter(price__lte=float(max_price))
        except: pass
    if ordering:
        qs = qs.order_by(ordering)

    products = qs[:60] 
    return render(request, "products/list.html", {"products": products, "products_model": Product})
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
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name','category']
    ordering_fields = ['price','sold_count','created_at']

    def get_serializer_class(self):
        if self.action in ['list','retrieve']:
            return ProductListSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        # create/update/delete -> manager only
        if self.action in ['create','update','partial_update','destroy']:
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
            return Response({"detail":"provide ?category=<category>"}, status=status.HTTP_400_BAD_REQUEST)
        qs = Product.objects.filter(category=cat)
        serializer = ProductListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def increment_stock(self, request, pk=None):
        # manager endpoint: increment stock
        if not (request.user.is_authenticated and request.user.is_manager):
            return Response({"detail":"unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        amount = int(request.data.get('amount', 1))
        product = self.get_object()
        product.stock = F('stock') + amount
        product.save()
        product.refresh_from_db()
        return Response({"id": product.id, "stock": product.stock})

def manager_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_manager)(view_func)

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
    # filters: most_sold / least_sold, by_category, date range optional
    order = request.GET.get('order', 'most')  # most or least
    category = request.GET.get('category')
    qs = Product.objects.all()
    if category:
        qs = qs.filter(category=category)
    # sold_count field exists; just order by that
    if order == 'least':
        qs = qs.order_by('sold_count')
    else:
        qs = qs.order_by('-sold_count')
    return render(request, 'products/sales_report.html', {'products': qs})
class ProductViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name','description']
    ordering_fields = ['price','sold_count','created_at']
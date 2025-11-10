from rest_framework import serializers
from .models import Product
#serializers for product model
class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id','name','category','price','stock','image_url','sold_count')
#detail serializer
class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

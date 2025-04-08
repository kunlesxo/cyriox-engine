from rest_framework import viewsets, permissions, status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import IntegrityError
from django_filters import rest_framework as filters
from rest_framework.decorators import api_view, permission_classes

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


# ✅ Custom filter for Category
class CategoryFilter(filters.FilterSet):
    distributor = filters.CharFilter(field_name='distributor__username', lookup_expr='icontains')

    class Meta:
        model = Category
        fields = ['distributor']


# ✅ ViewSet for Category (Only shows categories for the logged-in distributor)
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = CategoryFilter  # ✅ Corrected

    def get_queryset(self):
        return Category.objects.filter(distributor=self.request.user).order_by('created_at')

    def perform_create(self, serializer):
        try:
            serializer.save(distributor=self.request.user)
        except IntegrityError:
            raise serializers.ValidationError("Category with this name or slug already exists.")


# ✅ Product ViewSet (filtered by distributor and optionally by category)
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
import logging

# Set up logger
logger = logging.getLogger(__name__)

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Product.objects.all()

        distributor_id = self.request.query_params.get('distributor_id', None)
        if distributor_id:
            queryset = queryset.filter(distributor__id=distributor_id)

        category_id = self.request.query_params.get('category_id', None)
        if category_id:
            queryset = queryset.filter(category__id=category_id)

        return queryset.order_by('name')

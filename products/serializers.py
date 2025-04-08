from rest_framework import serializers
from .models import Category, Product


from rest_framework import serializers
from .models import Category  # Assuming the Category model is imported from models

class CategorySerializer(serializers.ModelSerializer):
    distributor_username = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'distributor_username']

    def get_distributor_username(self, obj):
        """
        Custom method to get the username of the distributor if it exists.
        """
        # Check if the 'distributor' related field is present, and if so, return the distributor's username
        if obj.distributor:
            return obj.distributor.username
        return None  # Fallback when no distributor is linked to the category

    def to_representation(self, instance):
        """
        Override the `to_representation` method if additional customizations are needed
        for the response format.
        """
        representation = super().to_representation(instance)
        # You can add more custom fields or manipulate data here if needed
        return representation




class ProductSerializer(serializers.ModelSerializer):
    # Flatten the category data and return only the category name
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)


    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock_quantity', 'distributor', 'category_id', 'category_name', 'image', 'created_at', 'updated_at']
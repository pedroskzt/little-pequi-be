from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.menu.menu_models import MenuItem, Category


class CategorySerializer(ModelSerializer):
    """Serializer for the category model"""

    # Slug should automatically set on instance creation and not changed after
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Category
        fields = '__all__'


class MenuItemSerializer(ModelSerializer):
    """Serializer for the menu item model"""

    class Meta:
        model = MenuItem
        fields = '__all__'

from rest_framework.serializers import ModelSerializer
from api.menu.menu_models import MenuItem


class MenuItemSerializer(ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'
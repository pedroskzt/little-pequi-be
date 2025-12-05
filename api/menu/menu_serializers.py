from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.menu.menu_models import MenuItem, Tag, Category
from core.CustomErrorManager.exception_handler import UpdateException, CreateException
import os

class TagSerializer(serializers.ModelSerializer):
    """Serializer for the tag model"""

    # Slug should automatically set on instance creation and not changed after
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Tag
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the category model"""

    # Slug should automatically set on instance creation and not changed after
    slug = serializers.SlugField(read_only=True)
    menu_items = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = '__all__'

    def get_menu_items(self, obj) -> list:
        if self.context.get('menu-items'):
            return list(MenuItemSerializer(obj.menu_items.all(), many=True).data)
        return list()

    def validate_display_order(self, value):
        bulk = self.context.get('bulk', False)
        model = self.Meta.model

        # If not bulk, validate display order (value) uniqueness
        if not bulk:
            try:
                UniqueValidator(queryset=model.objects.all())(value, self.fields['display_order'])
                return value
            except serializers.ValidationError as err:
                raise serializers.ValidationError(f"Display order must be unique. {err}")

        # If bulk, validation should be done in the view
        bulk_validated = self.context.get('display_order_unique')
        if bulk_validated is None:
            raise serializers.ValidationError(
                "For bulk validation, display_order must be validated outside the serializer.")

        if bulk_validated is False:
            raise serializers.ValidationError("Display order must be unique.")

        return value


class MenuItemSerializer(serializers.ModelSerializer):
    """Serializer for the menu item model"""
    tags = TagSerializer(many=True, required=False, read_only=True)
    category = CategorySerializer(read_only=True)
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = MenuItem
        fields = '__all__'

    def validate(self, data):
        tags_data = self.context.get('tags')
        category_id = self.context.get('category')

        # Category validation
        if category_id is None and self.partial is False:
            raise serializers.ValidationError(detail={'category': "This field is required."}, code='required')
        if category_id is not None:
            if not isinstance(category_id, int) :
                raise serializers.ValidationError(detail={'category': "Must be a valid integer."}, code='invalid')
            if not Category.objects.filter(pk=category_id).exists():
                raise serializers.ValidationError(detail={'category': "Invalid category id."}, code='invalid')

        # Tags validation
        if tags_data is not None:
            if not isinstance(tags_data, list):
                raise serializers.ValidationError(detail={'tags': "Must be a list of integers."}, code='invalid')
            if len(tags_data) > 0:
                for tag_id in tags_data:
                    if not isinstance(tag_id, int):
                        raise serializers.ValidationError(detail={'tags': "Must be a list of integers."}, code='invalid')
                    if not Tag.objects.filter(pk=tag_id).exists():
                        raise serializers.ValidationError(detail={'tags': "Invalid tag id."}, code='invalid')

        return super().validate(data)

    def create(self, validated_data):
        """Create a new menu item"""
        tags_data = self.context.get('tags')
        category_id = self.context.get('category')

        # If a category was sent, update the menu item category
        if category_id:
            category = Category.objects.filter(pk=category_id)
            if category.exists():
                validated_data['category'] = category[0]
            else:
                raise CreateException('Invalid category.')
        else:
            raise CreateException("Missing category")
            # TODO: Log change details (new category id, instance, etc)

        if tags_data:
            tags = Tag.objects.filter(pk__in=tags_data)
            if tags.exists() and tags.count() == len(tags_data):
                validated_data['tags'] = tags_data
            else:
                raise CreateException('Invalid tags.')
            # TODO: Log change details (new tags, instance, etc)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update a menu item"""

        tags_data = self.context.get('tags')
        category_id = self.context.get('category')
        # updated_instance = super().update(instance, validated_data)

        # If a category was sent, update the menu item category
        if category_id:
            category = Category.objects.filter(pk=category_id)
            if category.exists():
                validated_data['category'] = category[0]
            else:
                raise UpdateException('Invalid category.')
            # TODO: Log change details (new category id, instance, etc)

        # If tags were sent, replace existing tags with new ones
        if tags_data is not None:
            tags = Tag.objects.filter(pk__in=tags_data)
            if (tags.exists() and tags.count() == len(tags_data)) or tags_data == []:
                validated_data['tags'] = tags_data
            else:
                raise UpdateException('Invalid tags.')
            # TODO: Log change details (new tags, instance, etc)

        # Save the instance
        # updated_instance.save()

        return super().update(instance, validated_data)


class MenuItemImageSerializer(serializers.ModelSerializer):
    """Serializer for updating the image of a menu item"""

    class Meta:
        model = MenuItem
        fields = ('image',)
        extra_kwargs = {'image': {'required': True}}

    def validate_image(self, value):
        ext = os.path.splitext(value.name)[1]
        if ext not in settings.GS_ALLOWED_FORMATS:
            raise serializers.ValidationError(f"Invalid file type. Allowed formats: {settings.GS_ALLOWED_FORMATS}")
        return value

from django.db.models import F
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.menu import MenuItem, Tag, Category, MenuItemImageSerializer, CategorySerializer
from api.menu import MenuItemSerializer, TagSerializer
from core.BlobManager.BlobHandler.BlobHandler import BlobHandler
from core.CustomErrorManager.exception_handler import UpdateException


class TagViewSet(ModelViewSet):
    """
    Tag View set.

        ViewSet names and Access:
        tags-list:
            GET: List all tags - Allow Any
            POST: Create a new tag - Only Staff/Admin
        tags-detail:
            GET: Retrieve a tag instance - Allow Any
            PUT: Update a tag instance - Only Staff/Admin
            PATCH: Partial update a tag instance - Only Staff/Admin
            DELETE: Destroy a tag instance - Only Staff/Admin

    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filterset_fields = ('title', 'slug', 'id')

    def get_permissions(self):
        allow_any = ['list', 'retrieve']
        if self.action in allow_any:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class CategoryViewSet(ModelViewSet):
    """
    Category View set.

        ViewSet names and Access:
        category-list:
            GET: List all categories - Allow Any
            POST: Create a new category - Only Staff/Admin
        category-detail:
            GET: Retrieve a category instance - Allow Any
            PUT: Update a category instance - Only Staff/Admin
            PATCH: Partial update a category instance - Only Staff/Admin
            DELETE: Destroy a category instance - Only Staff/Admin

    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ('title', 'slug', 'id')

    def get_permissions(self):
        allow_any = ['list', 'retrieve', 'list_menu_items_by_category']
        if self.action in allow_any:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        destroyed_category = self.get_object()
        response = super().destroy(request, *args, **kwargs)

        if response.status_code == status.HTTP_204_NO_CONTENT:
            # Reduce display order of categories after the deleted one to avoid gaps
            self.get_queryset().filter(display_order__gt=destroyed_category.display_order).update(
                display_order=F('display_order') - 1)
        return response

    @action(detail=False, methods=['GET'], url_path='menu-items', url_name='menu-items')
    def list_menu_items_by_category(self, request):
        """List all menu items by tags"""
        try:
            serializer = self.get_serializer(self.get_queryset(), many=True, context={'menu-items': True})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['PUT'], url_path='bulk', url_name='bulk')
    def bulk_update(self, request, partial=False):
        request_data = request.data
        display_order_list = []
        pk_list = []
        for category in request_data:
            pk_list.append(int(category.get('id')))
            if 'display_order' in category:
                display_order_list.append(category.get('display_order'))

        try:
            context = {'bulk': True, 'display_order_unique': len(display_order_list) == len(set(display_order_list))}

            categories = self.get_queryset()
            if categories.exists() is False:
                raise UpdateException("No categories were found.")

            if categories.filter(pk__in=pk_list).count() != len(pk_list):
                raise UpdateException("Invalid categories.")

            serializer = self.get_serializer(data=request_data, many=True, partial=partial, context=context)
            if serializer.is_valid() is False:
                raise UpdateException(serializer.errors)

            display_order_list = dict((int(category['id']), category) for category in request_data)

            new_order = []
            objects_to_update = []
            fields_to_update = set()
            for category in categories:
                if category.pk in pk_list:
                    fields = display_order_list[category.pk]
                    for field in fields:
                        if field == 'id':
                            continue
                        setattr(category, field, fields[field])
                        fields_to_update.add(field)

                    pk_list.remove(category.pk)
                    objects_to_update.append(category)

                new_order.append(category.display_order)

            assert len(set(new_order)) == len(new_order), "Duplicate display orders found."
            categories.bulk_update(objects_to_update, fields=fields_to_update)

            serializer = self.get_serializer(instance=objects_to_update, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as err:
            raise UpdateException(err)

    @bulk_update.mapping.patch
    def bulk_partial_update(self, request):
        """Bulk partially update categories"""
        return self.bulk_update(request, partial=True)


class MenuItemViewSet(ModelViewSet):
    """
        Menu Item View set.

            ViewSet names and Access:
            menu-item-list:
                GET: List all categories - Allow Any
                POST: Create a new tags - Only Staff/Admin
            menu-item-detail:
                GET: Retrieve a tags instance - Allow Any
                PUT: Update a tags instance - Only Staff/Admin
                PATCH: Partial update a tags instance - Only Staff/Admin
                DELETE: Destroy a tags instance - Only Staff/Admin
            menu-item-update-image:
                POST: Update the image of a menu item - Only Staff/Admin

        """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        allow_any = ['list', 'retrieve']
        if self.action in allow_any:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        """Add tags to the serializer context"""
        context = super().get_serializer_context()
        context['tags'] = self.request.data.get('tags')
        context['category'] = self.request.data.get('category', None)
        return context

    def perform_destroy(self, instance):
        """Delete the image from storage when deleting a menu item"""
        if instance.image:
            BlobHandler.delete_blob(instance.image.name)
        return super().perform_destroy(instance)

    @action(detail=True, methods=['POST'], serializer_class=MenuItemImageSerializer, url_path='image', url_name='image', parser_classes=(MultiPartParser,))
    def update_image(self, request, pk=None):
        """
        Update the image of a menu item.
        If an image already exists, it will be deleted from storage before saving the new one.

        :param request: HTTP request containing the new image data
        :param pk: Primary key of the menu item to update
        :return: Response with updated menu item data or error messages
        """

        menu_item = self.get_object()
        if menu_item.image:
            BlobHandler.delete_blob(menu_item.image.name)

        serializer = self.get_serializer(menu_item, data=request.data)
        if serializer.is_valid() is False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.viewsets import ModelViewSet

from api.menu import MenuItem, Category
from api.menu import MenuItemSerializer, CategorySerializer


class CategoryViewSet(ModelViewSet):
    """
    Category View set.

        ViewSet names and Access:
        category-list: Allow Any
            GET: List all categories
            POST: Create a new category
        category-detail: Only Staff/Admin
            GET: Retrieve a category instance
            PUT: Update a category instance
            PATCH: Partial update a category instance
            DELETE: Destroy a category instance

    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class MenuItemViewSet(ModelViewSet):
    """
        Menu Item View set.

            ViewSet names and Access:
            category-list: Allow Any
                GET: List all categories
                POST: Create a new category
            category-detail: Only Staff/Admin
                GET: Retrieve a category instance
                PUT: Update a category instance
                PATCH: Partial update a category instance
                DELETE: Destroy a category instance

        """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

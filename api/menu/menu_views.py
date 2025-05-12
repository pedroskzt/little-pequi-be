from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from api.menu import MenuItem
from api.menu import MenuItemSerializer


class MenuItemViewSet(ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    # permission_classes  = [IsAdminUser]

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            # TODO: Fix error when trying to access with invalid token. Should be 100% public.
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

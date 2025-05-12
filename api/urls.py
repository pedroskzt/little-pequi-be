from django.urls import path
from rest_framework.routers import SimpleRouter

from api.menu import MenuItemViewSet

router = SimpleRouter(trailing_slash=False)
router.register('menu-items', MenuItemViewSet)

urlpatterns = [
]

urlpatterns += router.urls
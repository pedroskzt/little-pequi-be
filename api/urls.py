from rest_framework.routers import SimpleRouter

from api.menu import MenuItemViewSet, CategoryViewSet

router = SimpleRouter(trailing_slash=False)
router.register('category', CategoryViewSet, basename='category')
router.register('menu-item', MenuItemViewSet, basename='menu-item')

urlpatterns = [
]

urlpatterns += router.urls

from rest_framework.routers import SimpleRouter

from api.menu import MenuItemViewSet, TagViewSet, CategoryViewSet

router = SimpleRouter(trailing_slash=False)
router.register('tag', TagViewSet, basename='tag')
router.register('category', CategoryViewSet, basename='category')
router.register('menu-item', MenuItemViewSet, basename='menu-item')

urlpatterns = [
]

urlpatterns += router.urls

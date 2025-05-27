from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


# Create your views here.


class LoginViewSet(TokenObtainPairView):
    pass


class RefreshViewSet(TokenRefreshView):
    pass

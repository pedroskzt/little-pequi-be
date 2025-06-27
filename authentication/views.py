from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


# Create your views here.


class LoginViewSet(TokenObtainPairView):
    pass


class RefreshViewSet(TokenRefreshView):
    pass


class TokenVerifyViewSet(TokenVerifyView):
    pass

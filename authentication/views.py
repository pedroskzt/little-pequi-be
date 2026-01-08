from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


# Create your views here.


class LoginViewSet(TokenObtainPairView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)
        tokens = response.data
        response.data = {}
        response.set_cookie('access', tokens['access'], httponly=True, secure=True, samesite='Strict')
        response.set_cookie('refresh', tokens['refresh'], httponly=True, secure=True, samesite='Strict')
        print(response.data)
        return response


class RefreshViewSet(TokenRefreshView):
    pass


class TokenVerifyViewSet(TokenVerifyView):
    pass

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class SignInViewSet(TokenObtainPairView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Remove refresh token from body and send it as HTTPonly
        """

        response = super().post(request, *args, **kwargs)
        refresh_token = response.data.pop('refresh')
        response.set_cookie('refresh', refresh_token, httponly=True, secure=True, samesite='Strict', path='/auth/')
        return response


class RefreshViewSet(TokenRefreshView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Refresh token comes from HTTPOnly cookie. This method override simply extracts it from cookies and keeps the
        same behavior as the builtin method: validates the refresh token, rotates it and return a new pair.
        """
        refresh_token = request.COOKIES.get('refresh')

        if refresh_token is None:
            response = Response(data={"refresh": ["This cookie is required"]}, status=status.HTTP_400_BAD_REQUEST)
            response.set_cookie('refresh', "", httponly=True, secure=True, samesite='Strict', path='/auth/')
            return response

        request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data.pop('refresh')
        response.set_cookie('refresh', refresh_token, httponly=True, secure=True, samesite='Strict', path='/auth/')
        return response


class SignOutViewSet(TokenBlacklistView):
    """
        Refresh token comes from HTTPOnly cookie. This method override simply extracts it from cookies and blacklists it.
    """

    def post(self, request: Request, *args, **kwargs) -> Response:
        refresh_token = request.COOKIES.get('refresh')

        if refresh_token is None:
            response = Response({"refresh": ["This cookie is required"]}, status=status.HTTP_400_BAD_REQUEST)
        else:
            request.data['refresh'] = refresh_token
            response = super().post(request, *args, **kwargs)

        response.set_cookie('refresh', "", httponly=True, secure=True, samesite='Strict', path='/auth/')
        return response

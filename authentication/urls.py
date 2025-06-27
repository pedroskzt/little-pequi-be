from django.urls import path

from authentication.views import LoginViewSet, RefreshViewSet, TokenVerifyViewSet

urlpatterns = [
    path('sign-in/', LoginViewSet.as_view(), name='login'),
    path('refresh/', RefreshViewSet.as_view(), name='refresh'),
    path('verify/', TokenVerifyViewSet.as_view(), name='verify')
]

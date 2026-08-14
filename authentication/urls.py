from django.urls import path

from authentication.views import SignInViewSet, RefreshViewSet, SignOutViewSet

urlpatterns = [
    path('sign-in/', SignInViewSet.as_view(), name='signin'),
    path('sign-out/', SignOutViewSet.as_view(), name='signout'),
    path('refresh/', RefreshViewSet.as_view(), name='refresh'),
]

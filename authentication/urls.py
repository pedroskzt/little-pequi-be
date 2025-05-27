from django.urls import path

from . import views

urlpatterns = [
    path('sign-in/', views.LoginViewSet.as_view(), name='login'),
    path('refresh/', views.RefreshViewSet.as_view(), name='refresh')
]

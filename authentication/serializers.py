from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from djoser.conf import settings

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.USER_ID_FIELD,
            settings.LOGIN_FIELD) + (
                     "is_staff",)

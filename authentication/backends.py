from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.utils import timezone


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()

        if username is None:
            username = kwargs.get(user_model.USERNAME_FIELD, user_model.EMAIL_FIELD)
        if username is None or password is None:
            return
        try:
            user = user_model._default_manager.get(Q(username__iexact=username) | Q(email__iexact=username))
        except user_model.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            user_model().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                return user
        return None

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class EmailUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of username. It also sets username to be equal to email
     to be compatible with packages that use the default user model.
    """

    def create_user(self, email, password, first_name=None, last_name=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)
        extra_fields.setdefault('first_name', first_name)
        extra_fields.setdefault('last_name', last_name)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, first_name=None, last_name=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('first_name', first_name)
        extra_fields.setdefault('last_name', last_name)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)
        return self.create_user(email, password, **extra_fields)

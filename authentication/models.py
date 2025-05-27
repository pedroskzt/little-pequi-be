from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models

from authentication.manager import EmailUserManager


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = EmailUserManager()

    def __str__(self):
        return self.email

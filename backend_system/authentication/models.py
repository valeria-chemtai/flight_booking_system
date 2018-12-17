from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from authentication.managers import UserManager


class User(AbstractBaseUser):
    email = models.EmailField(unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=30, null=False, blank=False)
    last_name = models.CharField(max_length=30, null=False, blank=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    avatar = models. ImageField(upload_to='avatars/', height_field=None,
                                width_field=None, max_length=250, null=True, blank=True)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = ('User')
        verbose_name_plural = ('Users')

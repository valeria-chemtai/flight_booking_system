import binascii
import os

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models, transaction
from django.utils import timezone

from authentication import exceptions
from common.models import SoftDeleteModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    @transaction.atomic
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        Token.objects.create(user=user)
        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email=email, password=password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email=email, password=password, **extra_fields)


class User(AbstractBaseUser, SoftDeleteModel):
    email = models.EmailField(unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=30, null=False, blank=False)
    last_name = models.CharField(max_length=30, null=False, blank=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    passport_photo = models.ImageField(upload_to='passports', null=True, blank=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = ('User')
        verbose_name_plural = ('Users')


class Token(models.Model):
    """
    Custom Token model.
    Must haves:
        key: string identifying token
        user: user to which the token belongs.
    """
    key = models.CharField(max_length=2048, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='auth_token')
    expires_on = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
            current_time = timezone.now()
            password_duration = settings.PASSWORD_VALIDITY_IN_HOURS
            self.expires_on = (
                current_time + timezone.timedelta(hours=password_duration))
        super().save(*args, **kwargs)

    def generate_key(self, *args, **kwargs):
        return binascii.hexlify(os.urandom(20)).decode()

    def validate(self):
        if self.expires_on <= timezone.now():
            self.delete()
            raise exceptions.AuthenticationFailedTokenExpired

    def __str__(self):
        return self.key

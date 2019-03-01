from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from authentication.models import Token

UserModel = get_user_model()


class AuthenticationBackend():
    """
    Authenticate against our extended user model i.e. settings.AUTH_USER_MODEL.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Check the username/password and return a user.
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # password verification here helps mitigate timing attacks
            # https://code.djangoproject.com/ticket/20760
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def get_user(self, user_id):
        try:
            return UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None


class CustomTokenAuthentication(TokenAuthentication):
    keyword = 'Token'

    def authenticate_credentials(self, key):
        try:
            token = Token.objects.select_related('user').get(key=key)
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid Token.'))
        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive, contact customer care.'))
        return (token.user, token)

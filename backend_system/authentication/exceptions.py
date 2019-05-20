from rest_framework.exceptions import AuthenticationFailed


class AuthenticationFailedTokenExpired(AuthenticationFailed):
    default_detail = 'Token Expired, Login to get new token.'

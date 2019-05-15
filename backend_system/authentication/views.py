import os
import binascii

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from authentication.models import User, Token
from authentication.serializers import (
    UserChangePasswordSerializer,
    UserSerializer,
    UserSignInSerializer,
    UserSignupSerializer,
)
from permissions import IsAuthenticatedUser


class UserSignupViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data={"message": "User successfully registered."},
                        status=status.HTTP_201_CREATED)


class UserSignInView(APIView):
    serializer_class = UserSignInSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key,
                        'user': UserSerializer(user, context={'request': request}).data},
                        status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
    serializer_class = UserChangePasswordSerializer
    permission_classes = (IsAuthenticatedUser,)

    def post(self, request):
        serializer = UserChangePasswordSerializer(
            data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        # update the token
        new_token = binascii.hexlify(os.urandom(20)).decode()
        Token.objects.filter(user=request.user).update(key=new_token)

        return Response(data={'token': new_token}, status=status.HTTP_200_OK)


class UserProfileViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedUser,)

    def get_queryset(self):
        return super().get_queryset()


class UserResetPassword(viewsets.ModelViewSet):
    pass

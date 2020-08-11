from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from authentication.models import User


class BasicUserSerializer(serializers.Serializer):
    """User serializer to be used in model relations."""
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(
        max_length=30, allow_null=False, allow_blank=False, required=True)
    last_name = serializers.CharField(
        max_length=30, allow_null=False, allow_blank=False, required=True)

    class Meta:
        fields = ('first_name', 'last_name')


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(),
                                    message='A user with this email address exists')])
    first_name = serializers.CharField(
        max_length=30, allow_null=False, allow_blank=False, required=True)
    last_name = serializers.CharField(
        max_length=30, allow_null=False, allow_blank=False, required=True)
    passport_photo = serializers.ImageField(allow_null=True)
    tracking_emails = serializers.ListField(child=serializers.EmailField())

    class Meta:
        model = User
        fields = ('pk', 'email', 'first_name', 'last_name', 'date_joined',
                  'is_active', 'is_staff', 'is_superuser', 'passport_photo', 'tracking_emails')
        read_only_fields = ('pk', 'date_joined')
    # TODO: customize update to patch instead of put


class UserSignupSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all(),
                                    message='A user with this email address exists')])
    first_name = serializers.CharField(
        max_length=30, allow_null=False, allow_blank=True, required=True)
    last_name = serializers.CharField(
        max_length=30, allow_null=False, allow_blank=True, required=True)
    passport_photo = serializers.ImageField(allow_null=True, required=False)
    password = serializers.CharField(required=True)
    # tracking_emails = MultiEmailField(allow_null=True, required=False)
    tracking_emails = serializers.ListField(child=serializers.EmailField())

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data.pop('email'),
            password=validated_data.pop('password'),
            **validated_data)
        return user


class UserSignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("User not registered. Please signup first.")

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password,
            )
            if not user:
                raise serializers.ValidationError("Invalid email/password Combination.")
        else:
            raise serializers.ValidationError('Make sure you include "username" and "password".')

        attrs['user'] = user
        return attrs


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=256, required=True)
    new_password = serializers.CharField(max_length=256, required=True)
    confirm_new_password = serializers.CharField(max_length=256, required=True)

    def validate_old_password(self, value):
        user = self.context['user']
        if not user.check_password(value):
            raise serializers.ValidationError('Incorrect password.')
        return value

    def validate(self, data):
        if not data.get('new_password') or not data.get('confirm_new_password'):
            raise serializers.ValidationError("Please enter a new password and "
                                              "confirm it.")

        if data.get('new_password') != data.get('confirm_new_password'):
            raise serializers.ValidationError("Passwords do not match.")

        return data


class UserResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=256, required=False)

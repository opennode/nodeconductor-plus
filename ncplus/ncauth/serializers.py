from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate_username(self, attrs, attr_name):
        username = attrs[attr_name]
        if get_user_model().objects.filter(username=username).exists():
            raise serializers.ValidationError('User with such username already exists')
        return attrs

    def restore_object(self, attrs, instance=None):
        get_user_model().objects.create_user(username=attrs['username'], password=attrs['password'])
        return authenticate(username=attrs['username'], password=attrs['password'])


class SigninSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    # TODO

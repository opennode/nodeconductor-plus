from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers


from .utils import send_email


User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'password')
        write_only_fields = ('password',)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ActivationSerializer(serializers.Serializer):
    user_uuid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        try:
            self.user = User.objects.get(uuid=attrs['user_uuid'], is_active=False)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid user UUID')

        if not default_token_generator.check_token(self.user, attrs['token']):
            raise serializers.ValidationError('Invalid token')
        return attrs

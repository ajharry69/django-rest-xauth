from django.contrib.auth import get_user_model
from rest_framework import serializers

from xauth.serializers.profile import request_serializer_class


class RequestSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        return validated_data

    def create(self, validated_data):
        return validated_data


class AuthTokenOnlySerializer(serializers.HyperlinkedModelSerializer):
    normal = serializers.CharField(source='token.tokens.normal', read_only=True, )
    encrypted = serializers.CharField(source='token.tokens.encrypted', read_only=True, )

    class Meta:
        model = get_user_model()
        fields = 'normal', 'encrypted',


class AuthSerializer(request_serializer_class):
    token = serializers.DictField(source='token.tokens', read_only=True, )

    class Meta(request_serializer_class.Meta):
        fields = tuple(request_serializer_class.Meta.fields) + ('token',)

    def validate(self, attrs):
        return super().validate(attrs)

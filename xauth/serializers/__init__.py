from django.contrib.auth import get_user_model
from rest_framework import serializers

from xauth.serializers import profile
from xauth.utils import get_class
from xauth.utils.settings import PROFILE_REQUEST_SERIALIZER


class AuthTokenOnlySerializer(serializers.HyperlinkedModelSerializer):
    normal = serializers.CharField(source='token.tokens.normal', read_only=True, )
    encrypted = serializers.CharField(source='token.tokens.encrypted', read_only=True, )

    class Meta:
        model = get_user_model()
        fields = 'normal', 'encrypted',


class AuthSerializer(get_class(PROFILE_REQUEST_SERIALIZER, profile.ProfileSerializer)):
    token = serializers.DictField(source='token.tokens', read_only=True, )

    class Meta(get_class(PROFILE_REQUEST_SERIALIZER, profile.ProfileSerializer).Meta):
        fields = tuple(get_class(PROFILE_REQUEST_SERIALIZER, profile.ProfileSerializer).Meta.fields) + ('token',)

    def validate(self, attrs):
        return super().validate(attrs)

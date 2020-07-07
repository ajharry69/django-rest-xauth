from django.contrib.auth import get_user_model
from rest_framework import serializers

from xauth.utils import get_class
from xauth.utils.settings import USER_LOOKUP_FIELD, USER_PROFILE_SERIALIZER


class ProfileSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='xauth:profile', lookup_field=USER_LOOKUP_FIELD, )

    # groups = serializers.HyperlinkedRelatedField(view_name='group-detail', many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = tuple(get_user_model().PUBLIC_READ_WRITE_FIELDS) + ('url',)
        read_only_fields = tuple(get_user_model().READ_ONLY_FIELDS)


profile_serializer_class = get_class(USER_PROFILE_SERIALIZER, ProfileSerializer)


class AuthTokenOnlySerializer(serializers.HyperlinkedModelSerializer):
    normal = serializers.CharField(source='token.tokens.normal', read_only=True, )
    encrypted = serializers.CharField(source='token.tokens.encrypted', read_only=True, )

    class Meta:
        model = get_user_model()
        fields = 'normal', 'encrypted',


class AuthSerializer(profile_serializer_class):
    token = serializers.DictField(source='token.tokens', read_only=True, )

    class Meta(profile_serializer_class.Meta):
        fields = tuple(profile_serializer_class.Meta.fields) + ('token',)

    def validate(self, attrs):
        return super().validate(attrs)

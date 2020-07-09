from django.contrib.auth import get_user_model
from rest_framework import serializers

from xauth.serializers import AuthSerializer
from xauth.utils import get_class
from xauth.utils.settings import SIGNUP_REQUEST_SERIALIZER, SIGNUP_RESPONSE_SERIALIZER


class SignUpSerializer(AuthSerializer):
    password = serializers.CharField(
        write_only=True, allow_null=True, allow_blank=True,
        style={'input_type': 'password'},
    )

    class Meta(AuthSerializer.Meta):
        fields = tuple(AuthSerializer.Meta.fields) + tuple(get_user_model().WRITE_ONLY_FIELDS)

    def create(self, validated_data):
        # saves password in plain text
        user = super().create(validated_data)
        if user.has_usable_password():
            # hash and re-save password
            user.password = user.get_hashed(user.password)
            user.save()
        return user


request_serializer_class = get_class(SIGNUP_REQUEST_SERIALIZER, SignUpSerializer)
response_serializer_class = get_class(SIGNUP_RESPONSE_SERIALIZER, SignUpSerializer)

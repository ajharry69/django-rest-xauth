from django.contrib.auth import get_user_model
from rest_framework import serializers

from rest_framework.fields import empty

__all__ = ["ProfileSerializer", "PasswordResetSerializer"]


class ProfileSerializer(serializers.ModelSerializer):
    token = serializers.JSONField(source="token.tokens", read_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        for field in self.Meta.model.WRITE_ONLY_FIELDS:
            self.fields[field].write_only = True

    class Meta:
        model = get_user_model()
        fields = model.serializable_fields() + ("token",)
        read_only_fields = model.READ_ONLY_FIELDS


class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    is_change = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        fields = ("old_password", "new_password", "is_change")

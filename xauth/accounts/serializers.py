from django.apps import apps
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import empty

from xauth.internal_settings import AUTH_APP_LABEL

__all__ = [
    "ProfileSerializer",
    "PasswordResetSerializer",
    "SecurityQuestionSerializer",
    "AccountVerificationSerializer",
    "AccountActivationSerializer",
    "AddSecurityQuestionSerializer",
]


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    token = serializers.JSONField(source="token.tokens", read_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        for field in self.Meta.model.WRITE_ONLY_FIELDS:
            self.fields[field].write_only = True

        remove_fields = kwargs.pop("context", {}).get("remove_fields")
        if isinstance(remove_fields, str):
            if remove_fields != "__all__":
                raise ValueError("'remove_fields' value can either be an iterable of field names or '__all__'")
            self.fields.clear()
        else:
            for field in set(remove_fields or []):
                del self.fields[field]

    class Meta:
        model = get_user_model()
        fields = model.serializable_fields() + ("token", "url")
        read_only_fields = model.READ_ONLY_FIELDS
        extra_kwargs = {
            "password": dict(style={"input_type": "password"}),
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        instance = super().create(validated_data)
        instance.set_password(password)
        instance.save(update_fields=["password"])
        return instance


class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    is_change = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        fields = ("old_password", "new_password", "is_change")


class AccountVerificationSerializer(serializers.Serializer):
    code = serializers.CharField(
        write_only=True,
        min_length=get_user_model().VERIFICATION_CODE_LENGTH,
        max_length=get_user_model().VERIFICATION_CODE_LENGTH,
    )


class AccountActivationSerializer(serializers.Serializer):
    security_question_answer = serializers.CharField(write_only=True)


class SecurityQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model(AUTH_APP_LABEL, "SecurityQuestion")
        fields = ["question"]


class AddSecurityQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model(AUTH_APP_LABEL, "Security")
        fields = ["security_question", "security_question_answer"]
        extra_kwargs = {
            "security_question_answer": {
                "write_only": True,
                "style": {"input_type": "password"},
            },
        }

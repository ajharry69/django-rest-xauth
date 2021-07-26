from django.apps import apps
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import empty

__all__ = [
    "ProfileSerializer",
    "PasswordResetSerializer",
    "SecurityQuestionSerializer",
    "AccountVerificationSerializer",
    "AddSecurityQuestionSerializer",
]


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    token = serializers.JSONField(source="token.tokens", read_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        for field in self.Meta.model.WRITE_ONLY_FIELDS:
            self.fields[field].write_only = True

        for field in kwargs.pop("context", {}).get("remove_fields") or []:
            del self.fields[field]

    class Meta:
        model = get_user_model()
        fields = model.serializable_fields() + ("token", "url")
        read_only_fields = model.READ_ONLY_FIELDS


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


class SecurityQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model("accounts", "SecurityQuestion")
        fields = ["question"]


class AddSecurityQuestionSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.fields["security_question_answer"].write_only = True

    class Meta:
        model = apps.get_model("accounts", "Security")
        fields = ["security_question", "security_question_answer"]

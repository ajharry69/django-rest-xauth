from django.contrib.auth import get_user_model
from rest_framework import serializers

__all__ = ["ProfileSerializer"]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = "__all__"

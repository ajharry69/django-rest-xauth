from django.utils.translation import gettext as _
from rest_framework import exceptions
from rest_framework.decorators import action

from xauth.accounts.serializers import AccountActivationSerializer

__all__ = ["ActivateAccountViewSetMixin"]


class ActivateAccountViewSetMixin:
    @action(methods=["POST"], detail=True, url_path="activate-account", serializer_class=AccountActivationSerializer)
    def activate_account(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True) and request.user.activate_account(**serializer.validated_data):
                return self.retrieve(request, *args, **kwargs)
        except AttributeError:
            raise AttributeError("Make sure you applied `models.ActivityStatusMixin` to your `settings.AUTH_USER_MODEL`")
        return exceptions.ValidationError(_("Wrong security question answer"))

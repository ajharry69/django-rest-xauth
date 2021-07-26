from rest_framework.decorators import action
from rest_framework.response import Response

__all__ = ["ActivateAccountViewSetMixin"]


class ActivateAccountViewSetMixin:
    @action(methods=["POST"], detail=True, url_path="activate-account")
    def activate_account(self, request, *args, **kwargs):
        return Response()

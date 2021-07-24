from django.contrib.auth import get_user_model
from rest_framework import viewsets, response, permissions
from rest_framework.decorators import action

from xauth.accounts.mixins import ViewSetBasenameMixin
from xauth.accounts.permissions import IsOwner
from xauth.accounts.serializers import ProfileSerializer

__all__ = ["AccountViewSet"]


class AccountViewSet(ViewSetBasenameMixin, viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return get_user_model().objects.filter(pk=self.request.user.pk)

    @action(methods=["POST"], detail=False, permission_classes=[permissions.AllowAny])
    def signup(self, request, *args, **kwargs):
        return response.Response()

    @action(methods=["POST"], detail=False, permission_classes=[permissions.AllowAny])
    def signin(self, request, *args, **kwargs):
        return response.Response()

    @action(detail=True)
    def request_verification_code(self, request, *args, **kwargs):
        return response.Response()

    @action(methods=["POST"], detail=True)
    def verify_account(self, request, *args, **kwargs):
        return response.Response()

    @action(detail=True)
    def request_temporary_password(self, request, *args, **kwargs):
        return response.Response()

    @action(methods=["POST"], detail=True)
    def reset_password(self, request, *args, **kwargs):
        return response.Response()

    @action(methods=["POST"], detail=True)
    def set_security_question(self, request, *args, **kwargs):
        return response.Response()

    @action(methods=["POST"], detail=True)
    def activate_account(self, request, *args, **kwargs):
        return response.Response()

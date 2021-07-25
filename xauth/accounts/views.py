from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import viewsets, permissions, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response

from xauth.accounts.mixins import ViewSetBasenameMixin
from xauth.accounts.permissions import IsOwner
from xauth.accounts.serializers import ProfileSerializer, PasswordResetSerializer

__all__ = ["AccountViewSet"]


class AccountViewSet(ViewSetBasenameMixin, viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsOwner]
    url_name_basename = "account"

    def get_queryset(self):
        return get_user_model().objects.filter(pk=self.request.user.pk)

    def get_object(self):
        lookup_key = self.lookup_url_kwarg or self.lookup_field
        if lookup_key not in self.kwargs or self.action == "request_temporary_password":
            obj = self.request.user
            self.check_object_permissions(self.request, obj)
        else:
            obj = super().get_object()
        return obj

    @action(methods=["POST"], detail=False, permission_classes=[permissions.AllowAny])
    def signup(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @action(methods=["POST"], detail=False)
    def signin(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @action(detail=True, url_path="request-verification-code")
    def request_verification_code(self, request, *args, **kwargs):
        request.user.request_verification(send_mail=True)
        return self.retrieve(request, *args, **kwargs)

    @action(methods=["POST"], detail=True, url_path="verify-account")
    def verify_account(self, request, *args, **kwargs):
        if self.request.user.verify(request.data["code"]):
            return self.retrieve(request, *args, **kwargs)
        raise exceptions.ValidationError(_("Invalid verification code."))

    @action(detail=True, url_path="request-temporary-password")
    def request_temporary_password(self, request, *args, **kwargs):
        request.user.request_password_reset(send_mail=True)
        response = self.retrieve(request, *args, **kwargs)
        request.user.unflag_password_reset()
        return response

    @action(methods=["POST"], detail=True, url_path="reset-password", serializer_class=PasswordResetSerializer)
    def reset_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        if serializer.is_valid(raise_exception=True) and self.request.user.reset_password(**serializer.validated_data):
            return self.retrieve(request, *args, **kwargs)
        is_change = serializer.validated_data["is_change"]
        raise exceptions.ValidationError(_(f"Invalid {'old' if is_change else 'temporary'} password."))

    @action(methods=["POST"], detail=True, url_path="set-security-question")
    def set_security_question(self, request, *args, **kwargs):
        return Response()

    @action(methods=["POST"], detail=True, url_path="activate-account")
    def activate_account(self, request, *args, **kwargs):
        return Response()
from django.apps import apps
from django.contrib.auth import get_user_model, login, logout
from django.utils.translation import gettext as _
from rest_framework import viewsets, permissions, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from xently.core.loading import get_classes, get_class

from xauth.internal_settings import AUTH_APP_LABEL

IsOwner = get_class(f"{AUTH_APP_LABEL}.permissions", "IsOwner")
(
    SecurityQuestionSerializer,
    ProfileSerializer,
    AccountVerificationSerializer,
    PasswordResetSerializer,
    AddSecurityQuestionSerializer,
    AccountActivationSerializer,
) = get_classes(
    f"{AUTH_APP_LABEL}.serializers",
    [
        "SecurityQuestionSerializer",
        "ProfileSerializer",
        "AccountVerificationSerializer",
        "PasswordResetSerializer",
        "AddSecurityQuestionSerializer",
        "AccountActivationSerializer",
    ],
)

__all__ = ["AccountViewSet", "SecurityQuestionViewSet"]


class SecurityQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = SecurityQuestionSerializer
    queryset = apps.get_model(AUTH_APP_LABEL, "SecurityQuestion").objects.all()
    permission_classes = [permissions.IsAdminUser]  # TODO: consider superuser only


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsOwner]
    queryset = get_user_model().objects.all()

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

    def get_serializer_context(self):
        context = super().get_serializer_context().copy()
        remove_fields = []
        if self.action in ["update", "partial_update"]:
            # Password should not be updated using this action. Use `reset_password` instead
            remove_fields += ["password", "token"]
        elif self.action in ["set_security_question", "retrieve", "list"]:
            remove_fields.append("token")
        elif self.action == "signout":
            remove_fields = "__all__"
        context["remove_fields"] = remove_fields
        return context

    def retrieve(self, request, *args, **kwargs):
        # We need response to return data as per class declared serializer class
        self.serializer_class = self.__class__.serializer_class
        return super().retrieve(request, *args, **kwargs)

    @action(methods=["POST"], detail=False, permission_classes=[permissions.AllowAny])
    def signup(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @action(methods=["POST"], detail=False)
    def signin(self, request, *args, **kwargs):
        login(request, request.user)
        return self.retrieve(request, *args, **kwargs)

    @action(methods=["POST"], detail=True)
    def signout(self, request, *args, **kwargs):
        logout(request)
        return Response()

    def do_request_verification_code(self, user):
        user.request_verification(send_mail=True, request=self.request)

    @action(detail=True, url_path="request-verification-code", serializer_class=None)
    def request_verification_code(self, request, *args, **kwargs):
        self.do_request_verification_code(request.user)
        return self.retrieve(request, *args, **kwargs)

    @action(methods=["POST"], detail=True, url_path="verify-account", serializer_class=AccountVerificationSerializer)
    def verify_account(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True) and self.request.user.verify(**serializer.validated_data):
            return self.retrieve(request, *args, **kwargs)
        raise exceptions.ValidationError(_("Invalid verification code."))

    def do_request_temporary_password(self, user):
        user.request_password_reset(send_mail=True, request=self.request)

    @action(detail=True, url_path="request-temporary-password", serializer_class=None)
    def request_temporary_password(self, request, *args, **kwargs):
        self.do_request_temporary_password(request.user)
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

    @action(
        methods=["POST"], detail=True, url_path="set-security-question", serializer_class=AddSecurityQuestionSerializer
    )
    def set_security_question(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.request.user.add_security_question(**serializer.validated_data)
            return Response()
        raise exceptions.ValidationError(_("Invalid security question"))

    @action(methods=["POST"], detail=True, url_path="activate-account", serializer_class=AccountActivationSerializer)
    def activate_account(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True) and request.user.activate_account(**serializer.validated_data):
                return self.retrieve(request, *args, **kwargs)
        except AttributeError:
            raise AttributeError("Make sure you applied `models.UserActivationMixin` to your `settings.AUTH_USER_MODEL`")
        return exceptions.ValidationError(_("Wrong security question answer"))

from django.apps import apps
from django.contrib.auth import get_user_model, login, logout
from django.utils.translation import gettext as _
from rest_framework import viewsets, permissions, exceptions, routers, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from xently.core.loading import get_classes

from xauth.accounts.permissions import IsSuperuser, IsOwner
from xauth.authentication import PasswordResetRequestAuthentication
from xauth.internal_settings import AUTH_APP_LABEL

(
    SecurityQuestionSerializer,
    ProfileSerializer,
    AccountVerificationSerializer,
    PasswordResetSerializer,
    PasswordResetRequestSerializer,
    AddSecurityQuestionSerializer,
    AccountActivationSerializer,
) = get_classes(
    f"{AUTH_APP_LABEL}.serializers",
    [
        "SecurityQuestionSerializer",
        "ProfileSerializer",
        "AccountVerificationSerializer",
        "PasswordResetSerializer",
        "PasswordResetRequestSerializer",
        "AddSecurityQuestionSerializer",
        "AccountActivationSerializer",
    ],
)

__all__ = ["AccountViewSet", "SecurityQuestionViewSet"]


class SecurityQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = SecurityQuestionSerializer
    queryset = apps.get_model(AUTH_APP_LABEL, "SecurityQuestion").objects.all()
    permission_classes = [IsSuperuser]


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsOwner]
    queryset = get_user_model().objects.all()

    def __init__(self, *args, **kwargs):
        # This can ease calling `view.reverse_action(...)`; where view is an instance of `ViewSet` created
        # using constructor e.g. `ViewSet(...)`
        kwargs.setdefault("basename", routers.SimpleRouter().get_default_basename(self.__class__))
        super().__init__(*args, **kwargs)

    def perform_create(self, serializer):
        obj = serializer.save()
        if self.action == "signup" and not obj.is_verified:
            self.do_request_verification_code(obj)

    def get_queryset(self):
        if self.action == "request_verification_code":
            # When requesting for a verification code the authentication credentials (token) may expire. And given
            # the essence of the request is to renew the token while getting a new code in the process, we need to
            # allow for a user object to be retrieved from the request URL without requiring any form of
            # authentication prior.
            return super().get_queryset()
        return get_user_model().objects.filter(pk=self.request.user.pk)

    def get_object(self):
        lookup_key = self.lookup_url_kwarg or self.lookup_field
        if lookup_key not in self.kwargs or self.action == "request_temporary_password":
            # When requesting a temporary password, a persisted (i.e. references the same) user instance is
            # required to signal the generation of the password reset token. Therefore, our best bet is on
            # the user object from the request
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

    @action(
        detail=False,
        methods=["POST"],
        authentication_classes=[],
        permission_classes=[permissions.AllowAny],
    )
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
        """This can be overridden to by projects to for example send SMS and/or email"""
        user.request_verification(send_email=True, request=self.request)

    @action(
        detail=True,
        authentication_classes=[],
        permission_classes=[AllowAny],
        url_path="request-verification-code",
    )
    def request_verification_code(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_verified:
            return Response(status=status.HTTP_208_ALREADY_REPORTED)
        self.do_request_verification_code(user)
        return self.retrieve(request, *args, **kwargs)

    @action(methods=["POST"], detail=True, url_path="verify-account", serializer_class=AccountVerificationSerializer)
    def verify_account(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True) and self.request.user.verify(**serializer.validated_data):
            return self.retrieve(request, *args, **kwargs)
        raise exceptions.ValidationError(_("Invalid verification code."))

    def do_request_temporary_password(self, user):
        """This can be overridden to by projects to for example send SMS and/or email"""
        user.request_password_reset(send_email=True, request=self.request)

    @action(
        detail=False,
        methods=["POST"],
        url_path="request-temporary-password",
        serializer_class=PasswordResetRequestSerializer,
        authentication_classes=[PasswordResetRequestAuthentication],
    )
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
        error_message = _(f"Invalid {'old' if is_change else 'temporary'} password.")
        raise exceptions.ValidationError({"old_password": [error_message]})

    @action(
        detail=True,
        methods=["POST"],
        url_path="set-security-question",
        serializer_class=AddSecurityQuestionSerializer,
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
        except AttributeError as e:
            raise AttributeError(
                "Make sure you applied `models.UserActivationMixin` to your `settings.AUTH_USER_MODEL`"
            ) from e
        return exceptions.ValidationError(_("Wrong security question answer"))

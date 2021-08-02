from django.apps import apps
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.password_validation import validate_password
from django.core import signing
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from xently.core.loading import get_class

from xauth.accounts import signing_salt
from xauth.internal_settings import (
    ENFORCE_ACCOUNT_VERIFICATION,
    AUTH_APP_LABEL,
    ACCESS_TOKEN_EXPIRY,
    VERIFICATION_CODE_EXPIRY,
    TEMPORARY_PASSWORD_EXPIRY,
    PASSWORD_RESET_REQUEST_SUBJECT,
    VERIFICATION_REQUEST_SUBJECT,
)

Token = get_class(f"{AUTH_APP_LABEL}.token.generator", "Token")
UserManager = get_class(f"{AUTH_APP_LABEL}.managers", "UserManager")
Mail = get_class(f"{AUTH_APP_LABEL}.mail", "Mail")

__all__ = [
    "AbstractUser",
    "AbstractSecurity",
    "AbstractSecurityQuestion",
    "AbstractFailedSignInAttempt",
    "AbstractPasswordResetLog",
    "default_is_verified",
]


def default_is_verified():
    return not ENFORCE_ACCOUNT_VERIFICATION


class AbstractUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(db_index=True, max_length=150, blank=False, unique=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=default_is_verified)

    objects = UserManager()

    USERNAME_FIELD = EMAIL_FIELD = "email"  # returned by get_email_field_name()

    # all the fields listed here(including the USERNAME_FIELD and password) are
    # expected as part of parameters in `objects`(UserManager).create_superuser
    # REQUIRED_FIELDS = ["email"]

    # Contains a tuple of fields that are "safe" to access publicly with proper
    # caution taken for modification
    READ_ONLY_FIELDS = ("is_superuser", "is_staff", "is_verified")

    WRITE_ONLY_FIELDS = ("password",)

    VERIFICATION_CODE_LENGTH = 6

    TEMPORARY_PASSWORD_LENGTH = 8

    _PASSWORD_RESET_REQUEST_FLAG_ATTR = "requested_password_reset"

    class Meta:
        abstract = True
        app_label = AUTH_APP_LABEL

    @classmethod
    def serializable_fields(cls):
        return ("email",) + cls.WRITE_ONLY_FIELDS + cls.READ_ONLY_FIELDS

    @classmethod
    def admin_panel_fields(cls):
        return ("email",)

    @property
    def token(self):
        if self.is_verified:
            if hasattr(self, self.__class__._PASSWORD_RESET_REQUEST_FLAG_ATTR):
                return self.password_reset_token
            return Token(self.token_payload, expiry_period=ACCESS_TOKEN_EXPIRY)
        return self.verification_token

    @property
    def signed_id(self):
        return signing.Signer(salt=signing_salt).sign(self.pk)

    @classmethod
    def from_signed_id(cls, signed_id):
        try:
            unsigned_id = signing.Signer(salt=signing_salt).unsign(signed_id)
        except signing.BadSignature:
            pass
        else:
            return cls.objects.get(pk=unsigned_id)

    @property
    def verification_token(self):
        return Token(self.token_payload, expiry_period=VERIFICATION_CODE_EXPIRY, subject="verification")

    @property
    def password_reset_token(self):
        return Token(self.token_payload, expiry_period=TEMPORARY_PASSWORD_EXPIRY, subject="password-reset")

    def _flag_password_reset(self):
        assert not hasattr(self, self.__class__._PASSWORD_RESET_REQUEST_FLAG_ATTR), "Cannot modify an existing attribute"
        setattr(self, self.__class__._PASSWORD_RESET_REQUEST_FLAG_ATTR, True)

    def unflag_password_reset(self):
        try:
            delattr(self, self.__class__._PASSWORD_RESET_REQUEST_FLAG_ATTR)
        except AttributeError:
            return False
        return True

    def request_password_reset(self, **kwargs):
        password = self.__class__.objects.make_random_password(self.__class__.TEMPORARY_PASSWORD_LENGTH)

        apps.get_model(AUTH_APP_LABEL, "Security").objects.update_or_create(
            user=self,
            defaults={"temporary_password": make_password(password), "temporary_password_generation_time": timezone.now},
        )

        self._flag_password_reset()

        if kwargs.copy().pop("send_email", False):
            kwargs.setdefault("subject", PASSWORD_RESET_REQUEST_SUBJECT)
            self._send_email("email-request-password-reset", {"password": password}, **kwargs)
        return password

    request_password_reset.alters_data = True

    def request_verification(self, **kwargs):
        if self.is_verified:
            return

        code = self.__class__.objects.make_random_password(self.__class__.VERIFICATION_CODE_LENGTH, "23456789")

        apps.get_model(AUTH_APP_LABEL, "Security").objects.update_or_create(
            user=self,
            defaults={"verification_code": make_password(code), "verification_code_generation_time": timezone.now},
        )

        if kwargs.copy().pop("send_email", False):
            kwargs.setdefault("subject", VERIFICATION_REQUEST_SUBJECT)
            self._send_email("email-request-verification", {"code": code}, **kwargs)
        return code

    request_verification.alters_data = True

    def set_password(self, raw_password):
        validate_password(raw_password, user=self)
        super().set_password(raw_password)

    def reset_password(self, old_password, new_password, is_change=False):
        try:
            matched = check_password(old_password, self.password if is_change else self.security.temporary_password)
        except ObjectDoesNotExist:
            return False
        else:
            if matched:
                self.set_password(new_password)
                self.save(update_fields=["password"])
            return matched

    reset_password.alters_data = True

    def verify(self, code):
        try:
            matched = check_password(code, self.security.verification_code)
        except ObjectDoesNotExist:
            return False
        else:
            if matched:
                self.is_verified = True
                self.save(update_fields=["is_verified"])
            return matched

    verify.alters_data = True

    def add_security_question(self, security_question, security_question_answer):
        encrypted_answer = make_password(security_question_answer)
        apps.get_model(AUTH_APP_LABEL, "Security").objects.update_or_create(
            user=self,
            defaults={
                "security_question": security_question,
                "security_question_answer": encrypted_answer,
            },
        )

    add_security_question.alters_data = True

    def _send_email(self, template_name, context=None, subject=None, **kwargs):
        context = context if context else {}
        context["user"] = self
        Mail(subject=subject).add_recipient(self.email).send(template_name=template_name, context=context, **kwargs)

    @cached_property
    def token_payload(self):
        return {"id": self.signed_id}


class AbstractSecurityQuestion(models.Model):
    question = models.CharField(max_length=255, blank=False, null=False, unique=True)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        app_label = AUTH_APP_LABEL

    def __str__(self):
        return self.question


class AbstractSecurity(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="security", on_delete=models.CASCADE, primary_key=True
    )
    security_question = models.ForeignKey("accounts.SecurityQuestion", on_delete=models.SET_NULL, null=True, blank=True)
    security_question_answer = models.CharField(max_length=150, null=True)
    temporary_password = models.CharField(max_length=128, blank=False, null=True)
    verification_code = models.CharField(max_length=128, blank=False, null=True)
    temporary_password_generation_time = models.DateTimeField(blank=True, null=True)
    verification_code_generation_time = models.DateTimeField(blank=True, null=True)
    account_deactivation_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True
        app_label = AUTH_APP_LABEL
        unique_together = ("user", "security_question")


class AbstractPasswordResetLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="password_reset", on_delete=models.CASCADE)
    type = models.CharField(choices=[("Reset", 1), ("Change", 2)], max_length=10, default=2)
    request_ip = models.GenericIPAddressField(db_index=True, unpack_ipv4=True, blank=True, null=True)
    change_ip = models.GenericIPAddressField(db_index=True, unpack_ipv4=True, blank=True, null=True)
    request_time = models.DateTimeField(default=timezone.now)
    change_time = models.DateTimeField(blank=False, null=True)

    class Meta:
        abstract = True
        app_label = AUTH_APP_LABEL


class AbstractFailedSignInAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="signin_attempts", on_delete=models.CASCADE)
    device_ip = models.GenericIPAddressField(db_index=True, unpack_ipv4=True, blank=True, null=True)
    attempt_date = models.DateField(default=timezone.now)
    attempt_count = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        app_label = AUTH_APP_LABEL

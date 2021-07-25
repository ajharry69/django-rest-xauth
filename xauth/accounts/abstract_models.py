from django.apps import apps
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core import signing
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property

from xauth.accounts import signing_salt
from xauth.accounts.mail import Mail
from xauth.accounts.managers import UserManager
from xauth.accounts.token import Token
from xauth.internal_settings import *  # noqa

__all__ = [
    "AbstractUser",
    "AbstractSecurity",
    "AbstractSecurityQuestion",
    "AbstractFailedSignInAttempt",
    "AbstractPasswordResetLog",
]


class AbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    Guidelines: https://docs.djangoproject.com/en/3.0/topics/auth/customizing/
    """

    email = models.EmailField(db_index=True, max_length=150, blank=False, unique=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=not XAUTH_ENFORCE_ACCOUNT_VERIFICATION)

    objects = UserManager()

    USERNAME_FIELD = EMAIL_FIELD = "email"  # returned by get_email_field_name()

    # all the fields listed here(including the USERNAME_FIELD and password) are
    # expected as part of parameters in `objects`(UserManager).create_superuser
    # REQUIRED_FIELDS = ["email"]

    # Contains a tuple of fields that are "safe" to access publicly with proper
    # caution taken for modification
    READ_ONLY_FIELDS = ("is_superuser", "is_staff", "is_verified")

    WRITE_ONLY_FIELDS = ("password",)

    class Meta:
        abstract = True
        app_label = "accounts"

    @classmethod
    def serializable_fields(cls):
        return ("email",) + cls.WRITE_ONLY_FIELDS + cls.READ_ONLY_FIELDS

    @property
    def token(self):
        return (
            self.verification_token if self.is_verified else Token(self.token_payload, expiry_period=ACCESS_TOKEN_EXPIRY)
        )

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

    def request_password_reset(self, send_mail=False):
        password = self.__class__.objects.make_random_password(8)

        from xauth.accounts.models import Security

        Security.objects.update_or_create(
            user=self,
            defaults={"temporary_password": make_password(password), "temporary_password_generation_time": timezone.now},
        )

        if send_mail:
            self.send_email("request-password-reset", {"password": password})
        return password

    def request_verification(self, send_mail=False):
        if self.is_verified:
            return

        code = self.__class__.objects.make_random_password(6, "23456789")

        from xauth.accounts.models import Security

        Security.objects.update_or_create(
            user=self,
            defaults={"verification_code": make_password(code), "verification_code_generation_time": timezone.now},
        )

        if send_mail:
            self.send_email("request-verification", {"code": code})
        return code

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

    def activate_account(self, security_question_answer):
        pass

    def add_security_question(self, question, answer):
        metadata, created = apps.get_model("accounts", "Metadata").objects.get_or_create(user=self)
        metadata.security_question = question
        metadata.security_question_answer = answer
        metadata.save(update_fields=["security_question", "security_question_answer"])

    def send_email(self, template_name, context=None):
        context = context if context else {}
        context["user"] = self
        address = Mail.Address(self.email, reply_to=REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES)
        Mail.send(address=address, template_name=template_name, context=context)

    @cached_property
    def token_payload(self):
        return {"id": self.signed_id}


class AbstractSecurityQuestion(models.Model):
    question = models.CharField(max_length=255, blank=False, null=False, unique=True)
    added_on = models.DateTimeField(auto_now_add=True)
    usable = models.BooleanField(default=True)

    class Meta:
        abstract = True
        app_label = "accounts"

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
        app_label = "accounts"
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
        app_label = "accounts"


class AbstractFailedSignInAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="signin_attempts", on_delete=models.CASCADE)
    device_ip = models.GenericIPAddressField(db_index=True, unpack_ipv4=True, blank=True, null=True)
    attempt_date = models.DateField(default=timezone.now)
    attempt_count = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        app_label = "accounts"

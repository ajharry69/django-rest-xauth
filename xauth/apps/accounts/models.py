from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from xauth.apps.accounts.abstract_models import AbstractUser
from xauth.utils import enums, is_valid_str
from xauth.utils.settings import *  # noqa

__all__ = [
    "default_security_question",
    "User",
    "SecurityQuestion",
    "Metadata",
    "AccessLog",
    "PasswordResetLog",
    "FailedSignInAttempt",
]


def default_security_question():
    SecurityQuestion.objects.get_or_create(question="Default", usable=False)
    return SecurityQuestion.objects.order_by("id").first()


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"
        app_label = "accounts"


class SecurityQuestion(models.Model):
    question = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        unique=True,
    )
    added_on = models.DateTimeField(
        auto_now_add=True,
    )
    usable = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ("added_on",)
        app_label = "accounts"

    def __str__(self):
        return self.question


class Metadata(models.Model):
    """
    Contains additional data used for user account 'house-keeping'

    :cvar temporary_password hashed short-live password expected to be used for password reset

    :cvar verification_code hashed short-live code expected to be used for account verification
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    security_question = models.ForeignKey(
        "accounts.SecurityQuestion",
        on_delete=models.SET_DEFAULT,
        default=default_security_question,
    )
    security_question_answer = models.CharField(max_length=PASSWORD_LENGTH, blank=False, null=True)
    temporary_password = models.CharField(max_length=PASSWORD_LENGTH, blank=False, null=True)
    verification_code = models.CharField(max_length=PASSWORD_LENGTH, blank=False, null=True)
    tp_gen_time = models.DateTimeField(_("temporary password generation time"), blank=True, null=True)
    vc_gen_time = models.DateTimeField(_("verification code generation time"), blank=True, null=True)
    deactivation_time = models.DateTimeField(_("user account's deactivation time"), blank=True, null=True)

    class Meta:
        app_label = "accounts"

    def save(self, *args, **kwargs):
        raw_code = self.verification_code
        raw_password = self.temporary_password
        if is_valid_str(raw_code):
            self.verification_code = self._get_hashed(raw_code)
        if is_valid_str(raw_password):
            self.temporary_password = self._get_hashed(raw_password)
        self.__reinitialize_security_answer()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.security_question}"

    @property
    def is_verification_code_expired(self):
        time = self.vc_gen_time
        return (time + VERIFICATION_CODE_EXPIRY) <= timezone.now() if time else False

    @property
    def is_temporary_password_expired(self):
        time = self.tp_gen_time
        return (time + TEMPORARY_PASSWORD_EXPIRY) <= timezone.now() if time else False

    def check_temporary_password(self, raw_password) -> bool:
        """:returns True if `raw_password` matches `self.temporary_password`"""
        return self.__verify_this_against_other_code(self.temporary_password, raw_password)

    def check_verification_code(self, raw_code) -> bool:
        """:returns True if `raw_code` matches `self.verification_code`"""
        return self.__verify_this_against_other_code(self.verification_code, raw_code)

    def check_security_question_answer(self, raw_answer) -> bool:
        """:returns True if `raw_answer` matches `self.security_question_answer`"""
        return self.__verify_this_against_other_code(self.security_question_answer, raw_answer)

    # noinspection PyUnresolvedReferences
    def is_usable_code(self, hash_code) -> bool:
        """
        :param hash_code: string that should be checked for password usability
        :return: True if `hash_code` evaluates to a usable `password` according to
        `{user-model}.has_usable_password()`
        """
        user = self.user
        user.password = hash_code
        return user.has_usable_password()

    # noinspection PyUnresolvedReferences,PyProtectedMember
    def _get_hashed(self, raw):
        return self.user.get_hashed(raw)

    # noinspection PyUnresolvedReferences
    def __verify_this_against_other_code(self, this, other):
        user = self.user
        user.password = this
        return user.check_password(other)

    # noinspection PyUnresolvedReferences
    def __reinitialize_security_answer(self):
        hashed_answer = self._get_hashed(self.security_question_answer)
        meta = self.user.metadata
        if meta.security_question.usable:
            # providing an answer only makes sense if the question being answered
            # is ready to receive answers
            if meta.security_question_answer != hashed_answer:
                # answer was changed. Update
                self.security_question_answer = hashed_answer
        else:
            # question is unusable
            if not is_valid_str(self.security_question_answer):
                # set an un-usable password for an unusable account
                self.security_question_answer = hashed_answer


class AccessLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sign_in_ip = models.GenericIPAddressField(db_index=True, unpack_ipv4=True, blank=True, null=True)
    sign_out_ip = models.GenericIPAddressField(db_index=True, unpack_ipv4=True, blank=True, null=True)
    sign_in_time = models.DateTimeField(blank=True, null=True)
    sign_out_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        app_label = "accounts"
        ordering = (
            "-sign_in_ip",
            "-sign_out_ip",
            "-sign_in_time",
            "-sign_out_time",
        )

    def save(self, *args, **kwargs):
        """
        Saves access-log without the ambiguity of an access-log being recorded with sign_in and
        sign_out data in the same tuple/row(in a database table) since the two are mutually
        exclusive events
        """
        super().save(*args, **kwargs)


class PasswordResetLog(models.Model):
    __RESET_TYPES = [(k, k) for k, _ in enums.PasswordResetType.__members__.items()]
    __DEFAULT_RESET_TYPE = enums.PasswordResetType.RESET.name
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(choices=__RESET_TYPES, max_length=10, default=__DEFAULT_RESET_TYPE)
    request_ip = models.GenericIPAddressField(db_index=True, unpack_ipv4=True, blank=True, null=True)
    change_ip = models.GenericIPAddressField(db_index=True, unpack_ipv4=True, blank=True, null=True)
    request_time = models.DateTimeField(default=timezone.now)
    change_time = models.DateTimeField(blank=False, null=True)

    class Meta:
        app_label = "accounts"
        ordering = (
            "-request_time",
            "-change_time",
            "-request_ip",
            "-change_ip",
        )


class FailedSignInAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    device_ip = models.GenericIPAddressField(db_index=True, unpack_ipv4=True, blank=True, null=True)
    attempt_date = models.DateField(default=timezone.now)
    attempt_count = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounts"
        ordering = ("-attempt_date",)

    @property
    def remaining(self):
        """
        Calculates and returns the remaining signing attempts as guided by `XAUTH.MAXIMUM_SIGN_IN_ATTEMPTS`
        setting

        :return: remaining sign-in attempts. -1 could either mean attempts are not metered or record
        was not found
        """
        max_attempts, metered = max_sign_in_attempts()
        if metered:
            rem = int(max_attempts - self.attempt_count)
            if rem < 1:
                # maximum attempts reached. deactivate account
                self.user.is_active = False
                # noinspection PyUnresolvedReferences
                self.user.save()
            return rem
        return -1

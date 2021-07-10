import re
from datetime import datetime, date

import timeago
from django.apps import apps
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils import timezone
from django.utils.datetime_safe import date as dj_date, datetime as dj_datetime

from xauth.apps.accounts.managers import UserManager
from xauth.utils import enums, reset_empty_nullable_to_null
from xauth.utils import is_valid_str
from xauth.utils.mail import Mail
from xauth.utils.settings import *  # noqa
from xauth.utils.token import Token

__all__ = ["AbstractUser"]


class AbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    Guidelines: https://docs.djangoproject.com/en/3.0/topics/auth/customizing/
    """

    __DEVICE_IP = None
    __PROVIDERS = [(k, k) for k, _ in enums.AuthProvider.__members__.items()]
    __DEFAULT_PROVIDER = enums.AuthProvider.EMAIL.name
    username = models.CharField(db_index=True, max_length=150, unique=True)
    email = models.EmailField(db_index=True, max_length=150, blank=False, unique=True)
    surname = models.CharField(db_index=True, max_length=50, blank=True, null=True)
    first_name = models.CharField(db_index=True, max_length=50, blank=True, null=True)
    last_name = models.CharField(db_index=True, max_length=50, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    provider = models.CharField(choices=__PROVIDERS, max_length=20, default=__DEFAULT_PROVIDER)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    # if ENFORCE == True; then every new user account should be unverified(False) by default else otherwise
    is_verified = models.BooleanField(default=not ENFORCE_ACCOUNT_VERIFICATION)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"  # returned by get_email_field_name()

    # all the fields listed here(including the USERNAME_FIELD and password) are
    # expected as part of parameters in `objects`(UserManager).create_superuser
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    # Contains a tuple of fields that are "safe" to access publicly with proper
    # caution taken for modification
    READ_ONLY_FIELDS = ("id", "is_superuser", "is_staff", "is_verified")

    WRITE_ONLY_FIELDS = ("password",)

    # Contains a tuple of fields that are likely to have a null(None) value
    NULLABLE_FIELDS = ("surname", "first_name", "last_name", "mobile_number", "date_of_birth")

    # Contains a tuple of fields that are "safe" to access publicly
    PUBLIC_READ_WRITE_FIELDS = ("username", "email", "provider") + NULLABLE_FIELDS + READ_ONLY_FIELDS

    class Meta:
        ordering = ("created_at", "updated_at", "username")
        abstract = True

    def __str__(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        # TODO: split name if contains space to surname, firstname, lastname
        self.provider = self.provider if is_valid_str(self.provider) else self.__DEFAULT_PROVIDER
        _username = self.username
        self.username = self.normalize_username(_username if _username and len(_username) > 0 else self.email)
        if not is_valid_str(self.password):
            # do not store a null(None) password
            self.set_unusable_password()
        self.is_verified = self.__get_ascertained_verification_status()
        reset_empty_nullable_to_null(self, self.NULLABLE_FIELDS)
        super().save(*args, **kwargs)

    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically this would be the user's first and last name. Since we do
        not store the user's real name, we return their username instead.
        """
        s_name = self.surname.strip().capitalize() if self.surname else ""
        f_name = self.first_name.strip().capitalize() if self.first_name else ""
        l_name = self.last_name.strip().capitalize() if self.last_name else ""
        # trim off spaces at the start and/or end
        name = f"{s_name} {f_name} {l_name}".strip()
        if len(name) < 1:
            # name is empty, use username instead
            name = self.username
        return name if name and is_valid_str(name) else None

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        name = self.get_full_name()
        if is_valid_str(name):
            return name.split()[0] if " " in name else name
        return name

    def is_newbie(self, period: timedelta = NEWBIE_VALIDITY_PERIOD):
        period = timedelta(seconds=15) if period is None else period
        now = timezone.now()
        return now >= self.created_at >= (now - period)

    # Used in django admin site
    is_newbie.admin_order_field = "created_at"
    is_newbie.boolean = True
    is_newbie.short_description = "Newbie?"

    def age(self, unit="y"):
        """
        Calculates user's **APPROXIMATE** age from `self.date_of_birth`

        :param unit: (case-insensitive)unit of return age. Use value that starts with 'y'=years,
        'm'=months, 'w'=weeks, 'd'=days. An invalid(not amongst listed before) will default to
        'd'=days
        :return: int(rounded down to the nearest value) of calculated approximate age in `unit`
         if date_of_birth is not None
        """
        if self.date_of_birth is None:
            return 0
        from datetime import datetime

        unit = unit.lower() if is_valid_str(unit) else "y"
        days = (datetime.now().date() - datetime.strptime(self.date_of_birth, DATE_INPUT_FORMAT).date()).days
        _age = days
        if re.match("^y+", unit):
            _age = int(days / 365)
        elif re.match("^m+", unit):
            _age = int(days / 30)
        elif re.match("^w+", unit):
            _age = int(days / 7)
        elif re.match("^d+", unit):
            _age = days
        return _age

    @property
    def name(self):
        return self.get_full_name()

    @property
    def device_ip(self):
        return self.__DEVICE_IP

    @device_ip.setter
    def device_ip(self, value):
        self.__DEVICE_IP = value

    @property
    def requires_verification(self) -> bool:
        return not self.is_verified and ENFORCE_ACCOUNT_VERIFICATION

    @property
    def token(self):
        if not self.is_active:
            return self.activation_token
        return (
            self.verification_token
            if self.requires_verification
            else Token(self.token_payload(), expiry_period=TOKEN_EXPIRY)
        )

    @property
    def password_reset_token(self):
        return Token(self.token_payload(), expiry_period=TEMPORARY_PASSWORD_EXPIRY, subject="password-reset")

    @property
    def verification_token(self):
        return Token(self.token_payload(), expiry_period=VERIFICATION_CODE_EXPIRY, subject="verification")

    @property
    def activation_token(self):
        return Token(self.token_payload(), expiry_period=ACCOUNT_ACTIVATION_TOKEN_EXPIRY, subject="activation")

    def request_password_reset(self, send_mail: bool = True):
        # random temporary password of `length`
        password = self.get_random_code(length=TEMPORARY_PASSWORD_LENGTH)

        if send_mail:
            # send user email
            self.send_email("password-reset-request", {"password": password})

        # store the verification request data to database
        metadata = apps.get_model("accounts", "Metadata").objects.get_or_create(user_id=self.id)[0]
        metadata.temporary_password = password
        metadata.tp_gen_time = timezone.now()
        metadata.save()

        # create a new password reset log
        self.update_or_create_password_reset_log(force_create=True)
        return self.password_reset_token, password

    def request_verification(self, send_mail: bool = True):
        if self.is_verified:
            return self.token, None
        # random verification code of `length`
        code = self.get_random_code(alpha_numeric=False, length=VERIFICATION_CODE_LENGTH)

        # get or create a metadata object for the `user`
        metadata, created = apps.get_model("accounts", "Metadata").objects.get_or_create(user_id=self.id)

        if send_mail:
            # send user email
            # show welcome if the user is new and and is just created a metadata object in db
            show_welcome = self.is_newbie() and created  # noqa
            self.send_email("verification-request", {"code": code})

        # store the verification request data to database
        metadata.verification_code = code
        metadata.vc_gen_time = timezone.now()
        metadata.save()
        return self.verification_token, code

    def reset_password(self, temporary_password, new_password):
        metadata = apps.get_model("accounts", "Metadata").objects.get_or_create(pk=self.id)[0]
        if metadata.is_temporary_password_expired:
            return None, "expired"
        if metadata.check_temporary_password(raw_password=temporary_password):
            # temporary password matched(correct)
            # update user's password
            self.password = self.get_hashed(new_password)
            # prevent hashing of other irrelevant table column(s)
            self.save(update_fields=["password"])
            # reset temporary password & password generation time to None
            metadata.temporary_password = None
            metadata.tp_gen_time = None
            # prevent hashing of other irrelevant table column(s)
            metadata.save(update_fields=["temporary_password", "tp_gen_time"])
            # reflect the change to the logs
            self.update_or_create_password_reset_log()
            return self.token, None
        else:
            # temporary password mismatched(incorrect)
            return None, "incorrect"

    def verify(self, code):
        if self.is_verified:
            # no need of repeating the task
            return self.token, None
        metadata = apps.get_model("accounts", "Metadata").objects.get_or_create(pk=self.id)[0]
        if metadata.is_verification_code_expired:
            return None, "expired"
        if metadata.check_verification_code(raw_code=code):
            # verification code matched(correct)
            # update user's verification status
            self.is_verified = True
            # prevent's automatic hashing of irrelevant password
            self.save(update_fields=["is_verified"])
            # reset verification code & code generation time to None
            metadata.verification_code = None
            metadata.vc_gen_time = None
            # prevent hashing of other irrelevant table column(s)
            metadata.save(update_fields=["verification_code", "vc_gen_time"])
            # user is assumed to have just signed-in since he/she can now access resources
            self.update_or_create_access_log(force_create=True)
            return self.token, None
        else:
            # verification code mismatched(incorrect)
            return None, "incorrect"

    def activate_account(self, security_question_answer):
        """
        :param security_question_answer: raw answer to user's security question to be verified against
        database's answer for correctness (match)
        :return: tuple (Token, message) if user's account was activated successfully (Token, None) else
        (Token, Non-None-message)
        """
        if self.is_active:
            return self.token, None
        metadata = apps.get_model("accounts", "Metadata").objects.get_or_create(pk=self.id)[0]
        if metadata.check_security_question_answer(raw_answer=security_question_answer):
            # answer was correct, activate account
            self.is_active = True
            self.save(update_fields=["is_active"])
            return self.token, None
        else:
            # wrong answer
            return None, "incorrect"

    def add_security_question(self, question, answer):
        """
        Adds a security question to user's account

        :param question: instance of `SecurityQuestion`
        :param answer: answer to the question
        :return: bool. True if question was added successfully and False otherwise
        """
        metadata, created = apps.get_model("accounts", "Metadata").objects.get_or_create(user=self)
        metadata.security_question = question
        metadata.security_question_answer = answer
        metadata.save(
            update_fields=[
                "security_question",
                "security_question_answer",
            ]
        )
        return True

    def send_email(self, template_name: str, context=None):
        context = context if context else {}
        context["user"] = self
        address = Mail.Address(self.email, reply_to=REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES)
        Mail.send(address=address, template_name=template_name, context=context)

    def update_or_create_password_reset_log(self, force_create=False, type=enums.PasswordResetType.RESET):
        """
        :return: tuple (object, created), where created is a boolean specifying whether
         an object was created.
        """
        _type = type.name if isinstance(type, enums.PasswordResetType) else type
        objects = apps.get_model("accounts", "PasswordResetLog").objects

        def create(user):
            return objects.create(
                user=user,
                request_ip=user.device_ip,
                request_time=timezone.now(),
                change_ip=user.device_ip,
                change_time=timezone.now(),
                type=_type,
            )

        created = force_create
        if force_create is True:
            log = create(self)
        else:
            log = objects.filter(user=self, request_ip=self.device_ip, type=_type).order_by("-request_time").first()
            if log:
                log.change_ip = self.device_ip
                log.change_time = timezone.now()
                log.save()
                created = False
            else:
                log = create(self)
                created = True
        return log, created

    def update_or_create_access_log(self, force_create=False):
        """
        :return: tuple (object, created), where created is a boolean specifying whether
         an object was created.
        """
        objects = apps.get_model("accounts", "AccessLog").objects

        def create(user):
            return objects.create(
                user=user,
                sign_in_ip=user.device_ip,
                sign_in_time=timezone.now(),
                sign_out_ip=user.device_ip,
                sign_out_time=timezone.now(),
            )

        created = force_create
        if force_create is True:
            log = create(self)
        else:
            log = objects.filter(user=self, sign_in_ip=self.device_ip).order_by("-sign_in_time").first()
            if log:
                log.sign_out_ip = self.device_ip
                log.sign_out_time = timezone.now()
                log.save()
                created = False
            else:
                log = create(self)
                created = True
        return log, created

    def get_last_password_change_message(self, locale: str = "en"):
        """
        Gets the duration that's passed since the last time a password reset was logged
        :param locale the locale in which the response is to be returned. Default is english(en)
        :return: message of duration passed in the format "3 months ago"
        """
        locale = locale if is_valid_str(locale) else "en"
        password_reset = (
            apps.get_model("accounts", "PasswordResetLog")
            .objects.filter(user=self, change_time__isnull=False)
            .order_by("-change_time")
            .first()
        )
        if password_reset:
            change_time = password_reset.change_time
            tz = change_time.tzinfo
            return timeago.format(change_time, datetime.now(tz=tz), locale)
        return None

    def get_remaining_signin_attempts(self):
        """
        :return: number of sign-in attempts left until account is deactivated
        """
        attempt = (
            apps.get_model("accounts", "FailedSignInAttempt").objects.filter(user=self).order_by("-updated_at").first()
        )
        return self.__remaining_attempts(attempt)

    def update_signin_attempts(self, failed: bool):
        """
        :param failed if `True` a failed sign-in attempt count is incremented by one(+1) which will in turn translate
        to a minus one(-1) remaining attempts. If `False` failed attempts are reset to zero (0) and the remaining
        attempts are set to -1.
        :return: number of sign-in attempts left until account is deactivated
        """
        metered = max_sign_in_attempts()[1]
        attempt, created = apps.get_model("accounts", "FailedSignInAttempt").objects.get_or_create(user=self)

        count_attr = "attempt_count"
        zero_attempts_count = models.F(count_attr) - models.F(count_attr)
        if created:
            # new record was created
            if failed:
                attempt_count = attempt.attempt_count
            else:
                # sign-in was considered successful. Reset attempt count to 0
                attempt_count = zero_attempts_count
        else:
            # existing record was found
            if failed:
                attempt_count = models.F(count_attr) + 1
            else:
                # sign-in was considered successful. Reset attempt count to 0
                attempt_count = zero_attempts_count
        attempt.device_ip = self.device_ip
        attempt.attempt_date = dj_date.today()
        # if attempts are metered, use the latest attempt count otherwise
        # maintain it to zero i.e. assume there hasn't been a failed attempt
        attempt.attempt_count = attempt_count if metered else 0
        attempt.save()
        attempt.refresh_from_db()
        return self.__remaining_attempts(attempt) if failed else attempt.attempt_count - 1

    def get_random_code(self, alpha_numeric: bool = True, length=None):
        """
        Generates and returns random code of `length`
        :param alpha_numeric: if `True`, include letters and numbers in the generated code
        otherwise return only numbers
        :param length: length of the code. Random number between 8 & 10 will be used if not
        provided
        :return: random code
        """
        import random

        length = random.randint(8, 10) if length is None or not isinstance(length, int) else length
        rand = None
        if alpha_numeric:
            rand = self.__class__.objects.make_random_password(length=length)
        else:
            rand = self.__class__.objects.make_random_password(length=length, allowed_chars="23456789")
        return rand

    def token_payload(self) -> dict:
        """
        :return: dict of data that is attached to JWT token as payload
        """
        payload = {}
        for field in self.PUBLIC_READ_WRITE_FIELDS:
            val = getattr(self, field, None)
            if isinstance(val, dj_date) or isinstance(val, date):
                payload[field] = val.isoformat()
            elif isinstance(val, dj_datetime) or isinstance(val, datetime):
                payload[field] = val.isoformat()
            else:
                payload[field] = val
        return payload

    def get_hashed(self, raw):
        """
        Uses `settings.PASSWORD_HASHERS` to create and return a hashed `code` just like creating a hashed
        password

        :param raw: data to be hashed. Provide None to set an unusable hash code(password)
        :return: hashed version of `code`
        """
        # temporarily hold the user's password
        acc_password = self.password
        # hash the code. will reinitialize the password
        self.set_password(raw) if is_valid_str(raw) else self.set_unusable_password()
        code = self.password  # hashed code retrieved from password
        # re-[instate|initialize] user's password to it's previous value
        self.password = acc_password
        return code

    def __get_ascertained_verification_status(self):
        """
        :returns correct verification status based on 'user type'(superuser/staff) and `self.provider`
        """
        verified = self.is_verified
        if not verified:
            # check if it might have been a false-alarm on verification status
            if self.provider not in [enums.AuthProvider.EMAIL.name, enums.AuthProvider.PHONE.name]:
                # credentials must have already been verified by the auth provider
                verified = True
            if self.is_superuser or self.is_staff:
                # probably a known user already
                verified = True
        return verified

    @staticmethod
    def __remaining_attempts(attempt_log):
        return -1 if attempt_log is None else attempt_log.remaining

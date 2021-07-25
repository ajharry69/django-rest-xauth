import re

from django.conf import settings
from django.db import models
from django.utils.datetime_safe import datetime
from django.utils.functional import cached_property

from xauth.accounts.token import Token
from xauth.internal_settings import *  # noqa
from xauth.utils import is_valid_str

__all__ = [
    "ActivityStatusMixin",
    "AuthProviderMixin",
    "DateOfBirthMixin",
    "NameMixin",
]


def auth_providers():
    return getattr(settings, "XAUTH_PROVIDER_CHOICES", [(1, "Email")])


class ActivityStatusMixin(models.Model):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    @property
    def activation_token(self):
        return Token(self.token_payload, expiry_period=ACCOUNT_ACTIVATION_TOKEN_EXPIRY, subject="activation")

    @property
    def token(self):
        if not self.is_active:
            return self.activation_token
        return super().token

    def activate_account(self, security_question_answer):
        pass


class NameMixin(models.Model):
    surname = models.CharField(db_index=True, max_length=50, blank=True, null=True)
    first_name = models.CharField(db_index=True, max_length=50, blank=True, null=True)
    last_name = models.CharField(db_index=True, max_length=50, blank=True, null=True)

    class Meta:
        abstract = True

    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically this would be the user's first and last name. Since we do
        not store the user's real name, we return their username instead.
        """
        s_name = self.surname.strip().capitalize() if self.surname else ""
        f_name = self.first_name.strip().capitalize() if self.first_name else ""
        l_name = self.last_name.strip().capitalize() if self.last_name else ""

        name = f"{s_name} {f_name} {l_name}".strip()
        if not name and hasattr(self, "username"):
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

    @property
    def name(self):
        return self.get_full_name()

    def __str__(self):
        return self.name


class DateOfBirthMixin(models.Model):
    date_of_birth = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True

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

        unit = unit.lower() if is_valid_str(unit) else "y"
        days = (datetime.now().date() - datetime.strptime(self.date_of_birth, DATE_INPUT_FORMAT).date()).days
        age = days
        if re.match("^y+", unit):
            age = int(days / 365)
        elif re.match("^m+", unit):
            age = int(days / 30)
        elif re.match("^w+", unit):
            age = int(days / 7)
        elif re.match("^d+", unit):
            age = days
        return age


class AuthProviderMixin(models.Model):
    provider = models.IntegerField(choices=auth_providers, default=1)

    class Meta:
        abstract = True

    @cached_property
    def provider_name(self):
        return dict(auth_providers())[self.provider]

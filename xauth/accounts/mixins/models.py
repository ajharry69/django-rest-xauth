from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from xently.core.loading import get_class

from xauth.internal_settings import ACCOUNT_ACTIVATION_TOKEN_EXPIRY, AUTH_APP_LABEL

Token = get_class(f"{AUTH_APP_LABEL}.token.generator", "Token")

__all__ = ["UserActivationMixin", "NameMixin"]


class UserActivationMixin(models.Model):
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
        if self.is_active:
            return

        try:
            matched = check_password(security_question_answer, self.security.security_question_answer)
        except ObjectDoesNotExist:
            return False
        else:
            if matched:
                self.is_active = True
                self.save(update_fields=["is_active"])
            return matched


class NameMixin(models.Model):
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
        first_name = self.first_name.strip().capitalize() if self.first_name else ""
        last_name = self.last_name.strip().capitalize() if self.last_name else ""

        name = f"{first_name} {last_name}".strip()
        if not name and hasattr(self, "username"):
            # name is empty, use username instead
            name = self.username
        return name if name else None

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        name = self.get_full_name()
        if name:
            return name.split()[0] if " " in name else name
        return name

    @property
    def name(self):
        return self.get_full_name()

    def __str__(self):
        return self.name

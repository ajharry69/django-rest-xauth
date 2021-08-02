from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.utils.translation import gettext_lazy as _

__all__ = [
    "ENFORCE_ACCOUNT_VERIFICATION",
    "ACCESS_TOKEN_EXPIRY",
    "TOKEN_EXPIRY",
    "VERIFICATION_CODE_EXPIRY",
    "TEMPORARY_PASSWORD_EXPIRY",
    "REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES",
    "ACCOUNT_ACTIVATION_TOKEN_EXPIRY",
    "REQUEST_TOKEN_ENCRYPTED",
    "SENDER_ADDRESS",
    "SENDER_ADDRESS_PASSWORD",
    "APP_NAME",
    "PASSWORD_RESET_REQUEST_SUBJECT",
    "VERIFICATION_REQUEST_SUBJECT",
    "AUTH_APP_LABEL",
    "KEYS_DIR",
    "JWT_SIG_ALG",
    "MAKE_KEY_DIRS",
]

AUTH_APP_LABEL = getattr(settings, "XAUTH_AUTH_APP_LABEL", "accounts")
APP_NAME = getattr(settings, "XAUTH_EMAIL_APP_NAME", "")
PASSWORD_RESET_REQUEST_SUBJECT = getattr(settings, "XAUTH_PASSWORD_RESET_REQUEST_SUBJECT", _("Password Reset Request"))
VERIFICATION_REQUEST_SUBJECT = getattr(settings, "XAUTH_VERIFICATION_REQUEST_SUBJECT", _("Account Verification"))
ENFORCE_ACCOUNT_VERIFICATION = getattr(settings, "XAUTH_ENFORCE_ACCOUNT_VERIFICATION", True)
ACCESS_TOKEN_EXPIRY = TOKEN_EXPIRY = getattr(settings, "XAUTH_ACCESS_TOKEN_EXPIRY", timedelta(days=1))
VERIFICATION_CODE_EXPIRY = getattr(settings, "XAUTH_VERIFICATION_CODE_EXPIRY", timedelta(minutes=30))
TEMPORARY_PASSWORD_EXPIRY = getattr(settings, "XAUTH_TEMPORARY_PASSWORD_EXPIRY", timedelta(minutes=30))
ACCOUNT_ACTIVATION_TOKEN_EXPIRY = getattr(settings, "XAUTH_ACCOUNT_ACTIVATION_TOKEN_EXPIRY", timedelta(minutes=30))
SENDER_ADDRESS = getattr(settings, "XAUTH_SENDER_ADDRESS", settings.EMAIL_HOST_USER)
SENDER_ADDRESS_PASSWORD = getattr(settings, "XAUTH_SENDER_ADDRESS_PASSWORD", settings.EMAIL_HOST_PASSWORD)
REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES = getattr(settings, "XAUTH_REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES", None)
REQUEST_TOKEN_ENCRYPTED = getattr(settings, "XAUTH_GENERATE_ENCRYPTED_TOKENS", True)
# Create a folder in the root directory of the project to hold generated keys
# This directory should not be committed to version control
KEYS_DIR = str(getattr(settings, "XAUTH_KEYS_DIR", Path(settings.BASE_DIR).parent / ".secrets"))
JWT_SIG_ALG = getattr(settings, "XAUTH_JWT_SIG_ALG", "RS256")
MAKE_KEY_DIRS = getattr(settings, "XAUTH_MAKE_KEY_DIRS", True)

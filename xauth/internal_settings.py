from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from xauth.accounts import DEFAULT_AUTH_APP_LABEL

__all__ = [
    "ENFORCE_ACCOUNT_VERIFICATION",
    "ACCESS_TOKEN_EXPIRY",
    "TOKEN_EXPIRY",
    "ACCOUNT_VERIFICATION_TOKEN_EXPIRY",
    "PASSWORD_RESET_TOKEN_EXPIRY",
    "REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES",
    "ACCOUNT_ACTIVATION_TOKEN_EXPIRY",
    "VERIFY_ENCRYPTED_TOKEN",
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

AUTH_APP_LABEL = getattr(settings, "XAUTH_AUTH_APP_LABEL", DEFAULT_AUTH_APP_LABEL)
APP_NAME = getattr(settings, "XAUTH_EMAIL_APP_NAME", "")
PASSWORD_RESET_REQUEST_SUBJECT = getattr(settings, "XAUTH_PASSWORD_RESET_REQUEST_SUBJECT", _("Password Reset Request"))
VERIFICATION_REQUEST_SUBJECT = getattr(settings, "XAUTH_VERIFICATION_REQUEST_SUBJECT", _("Account Verification"))
ENFORCE_ACCOUNT_VERIFICATION = getattr(settings, "XAUTH_ENFORCE_ACCOUNT_VERIFICATION", True)
ACCESS_TOKEN_EXPIRY = TOKEN_EXPIRY = getattr(settings, "XAUTH_ACCESS_TOKEN_EXPIRY", timedelta(days=1))
ACCOUNT_VERIFICATION_TOKEN_EXPIRY = getattr(settings, "XAUTH_ACCOUNT_VERIFICATION_TOKEN_EXPIRY", timedelta(minutes=30))
PASSWORD_RESET_TOKEN_EXPIRY = getattr(settings, "XAUTH_PASSWORD_RESET_TOKEN_EXPIRY", timedelta(minutes=30))
ACCOUNT_ACTIVATION_TOKEN_EXPIRY = getattr(settings, "XAUTH_ACCOUNT_ACTIVATION_TOKEN_EXPIRY", timedelta(minutes=30))
SENDER_ADDRESS = getattr(settings, "XAUTH_SENDER_ADDRESS", settings.EMAIL_HOST_USER)
SENDER_ADDRESS_PASSWORD = getattr(settings, "XAUTH_SENDER_ADDRESS_PASSWORD", settings.EMAIL_HOST_PASSWORD)
REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES = getattr(settings, "XAUTH_REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES", None)
VERIFY_ENCRYPTED_TOKEN = getattr(settings, "XAUTH_VERIFY_ENCRYPTED_TOKEN", True)
# Create a folder in the root directory of the project to hold generated keys
# This directory should not be committed to version control
KEYS_DIR = str(getattr(settings, "XAUTH_KEYS_DIR", Path(settings.BASE_DIR) / ".secrets"))
JWT_SIG_ALG = getattr(settings, "XAUTH_JWT_SIG_ALG", "RS256")
MAKE_KEY_DIRS = getattr(settings, "XAUTH_MAKE_KEY_DIRS", True)

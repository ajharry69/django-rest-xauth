from pathlib import Path

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from xauth.accounts import DEFAULT_AUTH_APP_LABEL

__all__ = [
    "ENFORCE_ACCOUNT_VERIFICATION",
    "TOKEN_EXPIRY",
    "REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES",
    "VERIFY_ENCRYPTED_TOKEN",
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
TOKEN_EXPIRY = getattr(settings, "XAUTH_TOKEN_EXPIRY", None) or {}
REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES = getattr(settings, "XAUTH_REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES", None)
VERIFY_ENCRYPTED_TOKEN = getattr(settings, "XAUTH_VERIFY_ENCRYPTED_TOKEN", True)
# Create a folder in the root directory of the project to hold generated keys
# This directory should not be committed to version control
KEYS_DIR = str(getattr(settings, "XAUTH_KEYS_DIR", Path(settings.BASE_DIR) / ".secrets"))
JWT_SIG_ALG = getattr(settings, "XAUTH_JWT_SIG_ALG", "RS256")
MAKE_KEY_DIRS = getattr(settings, "XAUTH_MAKE_KEY_DIRS", True)

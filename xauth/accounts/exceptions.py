from django.utils.translation import gettext_lazy as _


class XauthException(Exception):
    pass


class PasswordResetError(XauthException):
    message = _("Password reset failed")


class AccountActivationError(XauthException):
    message = _("Account activation failed")


class AccountVerificationError(XauthException):
    message = _("Account verification failed")

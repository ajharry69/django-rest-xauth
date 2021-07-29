from xauth.accounts.abstract_models import *  # noqa

__all__ = [
    "User",
    "SecurityQuestion",
    "Security",
    "PasswordResetLog",
    "FailedSignInAttempt",
]


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


class SecurityQuestion(AbstractSecurityQuestion):
    pass


class Security(AbstractSecurity):
    pass


class PasswordResetLog(AbstractPasswordResetLog):
    pass


class FailedSignInAttempt(AbstractFailedSignInAttempt):
    pass

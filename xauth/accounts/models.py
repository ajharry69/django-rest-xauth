from xently.core.loading import is_model_registered

from xauth.accounts.abstract_models import (
    AbstractUser,
    AbstractSecurityQuestion,
    AbstractSecurity,
    AbstractPasswordResetLog,
    AbstractFailedSignInAttempt,
)
from xauth.internal_settings import AUTH_APP_LABEL

__all__ = []

if not is_model_registered("xauth", "User"):

    class User(AbstractUser):
        class Meta(AbstractUser.Meta):
            swappable = "AUTH_USER_MODEL"
            app_label = "xauth"

    __all__.append("User")

if not is_model_registered(AUTH_APP_LABEL, "SecurityQuestion"):

    class SecurityQuestion(AbstractSecurityQuestion):
        pass

    __all__.append("SecurityQuestion")

if not is_model_registered(AUTH_APP_LABEL, "Security"):

    class Security(AbstractSecurity):
        pass

    __all__.append("Security")

if not is_model_registered(AUTH_APP_LABEL, "PasswordResetLog"):

    class PasswordResetLog(AbstractPasswordResetLog):
        pass

    __all__.append("PasswordResetLog")

if not is_model_registered(AUTH_APP_LABEL, "FailedSignInAttempt"):

    class FailedSignInAttempt(AbstractFailedSignInAttempt):
        pass

    __all__.append("FailedSignInAttempt")

from xauth.accounts.abstract_models import *  # noqa

from xauth.utils import is_model_registered

__all__ = []

if not is_model_registered("xauth", "User"):

    class User(AbstractUser):
        class Meta(AbstractUser.Meta):
            swappable = "AUTH_USER_MODEL"
            app_label = "xauth"

    __all__ += ["User"]

if not is_model_registered("accounts", "SecurityQuestion"):

    class SecurityQuestion(AbstractSecurityQuestion):
        pass

    __all__ += ["SecurityQuestion"]

if not is_model_registered("accounts", "Security"):

    class Security(AbstractSecurity):
        pass

    __all__ += ["Security"]

if not is_model_registered("accounts", "PasswordResetLog"):

    class PasswordResetLog(AbstractPasswordResetLog):
        pass

    __all__ += ["PasswordResetLog"]

if not is_model_registered("accounts", "FailedSignInAttempt"):

    class FailedSignInAttempt(AbstractFailedSignInAttempt):
        pass

    __all__ += ["FailedSignInAttempt"]

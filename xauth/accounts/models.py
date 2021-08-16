from django.db import models
from xently.core.loading import is_model_registered

from xauth.accounts.abstract_models import (
    AbstractUser,
    AbstractSecurityQuestion,
    AbstractSecurity,
)
from xauth.internal_settings import AUTH_APP_LABEL

__all__ = []

if not is_model_registered(AUTH_APP_LABEL, "User"):

    class User(AbstractUser):
        class Meta(AbstractUser.Meta):
            swappable = "AUTH_USER_MODEL"

        email = models.EmailField(db_index=True, max_length=150, blank=False, unique=True)

        USERNAME_FIELD = EMAIL_FIELD = "email"  # returned by get_email_field_name()

        @classmethod
        def serializable_fields(cls):
            return ("email",) + super().serializable_fields()

        @classmethod
        def admin_panel_fields(cls):
            return ("email",) + super().admin_panel_fields()

    __all__.append("User")

if not is_model_registered(AUTH_APP_LABEL, "SecurityQuestion"):

    class SecurityQuestion(AbstractSecurityQuestion):
        pass

    __all__.append("SecurityQuestion")

if not is_model_registered(AUTH_APP_LABEL, "Security"):

    class Security(AbstractSecurity):
        pass

    __all__.append("Security")

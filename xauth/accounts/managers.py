from django.contrib.auth.base_user import BaseUserManager

from xauth.utils import is_valid_str

__all__ = ["UserManager"]


class UserManager(BaseUserManager):
    def create_user(self, email, **kwargs):
        if not is_valid_str(email):
            raise ValueError("email is required")

        password = kwargs.pop("password", None)
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        if not is_valid_str(password):
            raise ValueError("superuser password is required")

        user = self.create_user(email, password=password, **kwargs)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.save(using=self._db)
        return user

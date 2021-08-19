from django.contrib.auth.base_user import BaseUserManager

__all__ = ["UserManager"]


class UserManager(BaseUserManager):
    def create_user(self, **kwargs):
        username = kwargs.get(self.model.USERNAME_FIELD)
        if not username:
            raise ValueError(f"{self.model.USERNAME_FIELD} is required")

        commit = kwargs.pop("save_record", True)
        password = kwargs.pop("password", None)
        if self.model.USERNAME_FIELD == self.model.get_email_field_name():
            username = self.normalize_email(username)
        else:
            username = self.model.normalize_username(username)
            email = kwargs.get(self.model.get_email_field_name())
            if email is not None:
                kwargs[self.model.get_email_field_name()] = self.normalize_email(email)
        kwargs[self.model.USERNAME_FIELD] = username

        user = self.model(**kwargs)
        user.set_password(password)
        if commit:
            user.save(using=self._db)
        return user

    def create_superuser(self, password, **kwargs):
        if not password:
            raise ValueError("superuser password is required")

        commit = kwargs.pop("save_record", True)
        user = self.create_user(password=password, save_record=False, **kwargs)
        user.is_superuser = True
        user.is_verified = True
        if commit:
            user.save(using=self._db)
        return user

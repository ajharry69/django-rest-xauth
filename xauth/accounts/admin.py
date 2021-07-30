from django import forms
from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext as _

from xauth.internal_settings import AUTH_APP_LABEL

__all__ = ["UserCreationForm", "UserUpdateForm", "UserAdmin", "SecurityQuestionAdmin"]


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = model.admin_panel_fields()

    def clean_password2(self):
        """check that two password entries match"""
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_("Passwords do not match"), code="password_mismatch")

        return p2

    def save(self, commit=True):
        """save the user and provided password in hashed format"""
        user = super().save(commit=False)  # `commit=False` Helps avoid double database writes
        user.set_password(self.cleaned_data.get("password2"))

        if commit:
            user.save()

        return user


class UserUpdateForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    password = ReadOnlyPasswordHashField

    class Meta:
        model = get_user_model()
        fields = model.serializable_fields()

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get("password")


class UserAdmin(BaseUserAdmin):
    form = UserUpdateForm
    add_form = UserCreationForm

    ordering = (get_user_model().USERNAME_FIELD,)
    list_display = get_user_model().admin_panel_fields() + get_user_model().READ_ONLY_FIELDS
    list_filter = get_user_model().READ_ONLY_FIELDS
    fieldsets = [
        (None, {"fields": get_user_model().admin_panel_fields() + ("password",)}),
        ("Permissions", {"fields": get_user_model().READ_ONLY_FIELDS}),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],  # Class for applying styling
                "fields": get_user_model().admin_panel_fields() + ("password1", "password2"),
            },
        )
    ]
    filter_horizontal = ()


class SecurityQuestionAdmin(admin.ModelAdmin):
    list_display = ("question", "added_on")


admin.site.register(get_user_model(), UserAdmin)
admin.site.register(apps.get_model(AUTH_APP_LABEL, "SecurityQuestion"), SecurityQuestionAdmin)

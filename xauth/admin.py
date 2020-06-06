from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _

from .models import User, SecurityQuestion, Metadata


class MetadataInline(admin.StackedInline):
    model = Metadata
    fields = ('security_question',)
    readonly_fields = ('security_question',)


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'surname', 'first_name', 'last_name', 'date_of_birth', 'mobile_number',)

    def clean_password2(self):
        """check that two password entries match"""
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_("passwords do not match"), code='password_mismatch')

        return p2

    def save(self, commit=True):
        """save the user and provided password in hashed format"""
        user = super().save(commit=False)  # `commit=False` Helps avoid double database writes
        user.set_password(self.cleaned_data.get('password2'))

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
        model = User
        fields = ('username', 'email', 'surname', 'first_name', 'last_name', 'date_of_birth', 'mobile_number',
                  'provider', 'is_superuser', 'is_staff', 'is_verified', 'is_active', 'password',)

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get('password')


class UserAdmin(BaseUserAdmin):
    form = UserUpdateForm
    add_form = UserCreationForm

    list_display = ('surname', 'first_name', 'last_name', 'date_of_birth', 'mobile_number', 'username', 'email',
                    'provider', 'created_at', 'is_verified', 'is_staff', 'is_newbie',)
    list_filter = ('provider', 'is_verified', 'is_staff',)
    # readonly_fields = ('provider', 'is_verified', 'is_staff', 'created_at',)
    search_fields = ('surname', 'first_name', 'last_name', 'email', 'mobile_number',)
    ordering = ('surname', 'first_name', 'last_name', 'email', 'mobile_number', 'created_at',)
    fieldsets = [
        (None, {
            'fields': ('provider', 'username', 'email', 'password',)
        }),
        (
            'Personal info', {
                'fields': ('surname', 'first_name', 'last_name', 'mobile_number', 'date_of_birth',),
            },
        ),
        (
            'Permissions', {
                'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser',),
            },
        ),
    ]
    add_fieldsets = [
        (
            None, {
                'classes': ['wide', ],  # Class for applying styling
                'fields': ('surname', 'first_name', 'last_name', 'mobile_number', 'date_of_birth', 'username', 'email',
                           'password1', 'password2',),
            },
        )
    ]
    inlines = (MetadataInline,)
    filter_horizontal = ()


class SecurityQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'usable', 'added_on')


admin.site.register(SecurityQuestion, SecurityQuestionAdmin)

admin.site.register(User, UserAdmin)

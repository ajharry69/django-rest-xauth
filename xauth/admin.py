from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User, SecurityQuestion, Metadata


class MetadataInline(admin.StackedInline):
    model = Metadata
    fields = ('security_question',)
    readonly_fields = ('security_question',)


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'surname', 'first_name', 'last_name', 'date_of_birth', 'mobile_number',)

    def clean_password2(self, ):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match")

        return p2

    def save(self, commit=True):
        user = super().save(commit=False)  # `commit=False` Helps avoid double database writes
        user.set_password(self.cleaned_data.get('password2'))

        if commit:
            user.save()

        return user


class UserUpdateForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField

    class Meta:
        model = User
        fields = ('username', 'email', 'surname', 'first_name', 'last_name', 'date_of_birth', 'mobile_number',
                  'provider', 'is_superuser', 'is_staff', 'is_verified', 'is_active', 'password',)

    def clean_password(self):
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

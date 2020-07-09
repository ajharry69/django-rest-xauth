from django.urls import include, re_path
from rest_framework import routers

from xauth.utils.settings import *
from xauth.views import sign_in, sign_out, signup, verification, activation, password, profile
from xauth.views.security_question import admin, AddSecurityQuestionView

__router = routers.DefaultRouter()
__router.register(r'security-questions', admin.SecurityQuestionView)

app_name = 'xauth'
urlpatterns = [
    re_path(r'^', include(__router.urls)),
    re_path(
        r'^signout/',
        view=sign_out.SignOutView.as_view(),
        name='signout',
    ),
    re_path(
        r'^signin/',
        view=sign_in.SignInView.as_view(),
        name='signin',
    ),
    re_path(
        r'^signup/',
        view=signup.SignUpView.as_view(),
        name='signup',
    ),
    re_path(
        r'^%s' % PROFILE_ENDPOINT,
        view=profile.ProfileView.as_view(),
        name='profile',
    ),
    re_path(
        r'^verification/request/',
        view=verification.VerificationRequestView.as_view(),
        name='verification-request',
    ),
    re_path(
        r'^%s' % VERIFICATION_ENDPOINT,
        view=verification.VerificationConfirmView.as_view(),
        name='verification-confirm',
    ),
    re_path(
        r'^password/reset/request/',
        view=password.PasswordResetRequestView.as_view(),
        name='password-reset-request',
    ),
    re_path(
        r'^%s' % PASSWORD_RESET_ENDPOINT,
        view=password.PasswordResetConfirmView.as_view(),
        name='password-reset-confirm',
    ),
    re_path(
        r'^activation/request/',
        view=activation.ActivationRequestView.as_view(),
        name='activation-request',
    ),
    re_path(
        r'^%s' % ACTIVATION_ENDPOINT,
        view=activation.ActivationConfirmView.as_view(),
        name='activation-confirm',
    ),
    re_path(
        r'^security-question/add/',
        view=AddSecurityQuestionView.as_view(),
        name='security-question-add',
    ),
]

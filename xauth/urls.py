from django.urls import include, re_path
from rest_framework import routers

from xauth import views
from xauth.utils.settings import *

__router = routers.DefaultRouter()
__router.register(r'security-questions', views.SecurityQuestionView)

app_name = 'xauth'
urlpatterns = [
    re_path(r'^', include(__router.urls)),
    re_path(
        r'^signout/',
        view=views.SignOutView.as_view(),
        name='signout',
    ),
    re_path(
        r'^signin/',
        view=views.SignInView.as_view(),
        name='signin',
    ),
    re_path(
        r'^signup/',
        view=views.SignUpView.as_view(),
        name='signup',
    ),
    re_path(
        r'^%s' % PROFILE_ENDPOINT,
        view=views.ProfileView.as_view(),
        name='profile',
    ),
    re_path(
        r'^verification/request/',
        view=views.VerificationRequestView.as_view(),
        name='verification-request',
    ),
    re_path(
        r'^%s' % VERIFICATION_ENDPOINT,
        view=views.VerificationConfirmView.as_view(),
        name='verification-confirm',
    ),
    re_path(
        r'^password/reset/request/',
        view=views.PasswordResetRequestView.as_view(),
        name='password-reset-request',
    ),
    re_path(
        r'^%s' % PASSWORD_RESET_ENDPOINT,
        view=views.PasswordResetConfirmView.as_view(),
        name='password-reset-confirm',
    ),
    re_path(
        r'^activation/request/',
        view=views.ActivationRequestView.as_view(),
        name='activation-request',
    ),
    re_path(
        r'^%s' % ACTIVATION_ENDPOINT,
        view=views.ActivationConfirmView.as_view(),
        name='activation-confirm',
    ),
    re_path(
        r'^security-question/add/',
        view=views.AddSecurityQuestionView.as_view(),
        name='security-question-add',
    ),
]

from django.urls import path, include
from rest_framework import routers

from xauth import views
from xauth.utils.settings import *

router = routers.DefaultRouter()
router.register(r'security-questions', views.SecurityQuestionView)

verification_ep = str(XAUTH.get('ACTIVATION_ENDPOINT', 'activation/activate/'))
password_reset_ep = str(XAUTH.get('PASSWORD_RESET_ENDPOINT', 'password-reset/verify/'))
activation_ep = str(XAUTH.get('VERIFICATION_ENDPOINT', 'verification-code/verify/'))

app_name = 'xauth'
urlpatterns = [
    path('', include(router.urls)),
    path('signout/', view=views.SignOutView.as_view(), name='signout'),
    path('signin/', view=views.SignInView.as_view(), name='signin'),
    path('signup/', view=views.SignUpView.as_view(), name='signup'),
    path('profile/<int:pk>/', view=views.ProfileView.as_view(), name='profile'),
    path(verification_ep, view=views.VerificationCodeVerifyView.as_view(), name='verification-code-verify'),
    path('verification-code/request/', view=views.VerificationCodeRequestView.as_view(), name='verification-code-send'),
    path(password_reset_ep, view=views.PasswordResetView.as_view(), name='password-reset-verify'),
    path('password-reset/request/', view=views.PasswordResetRequestView.as_view(), name='password-reset-send'),
    path('security-question/add/', view=views.AddSecurityQuestionView.as_view(), name='security-question-add'),
    path('activation/request/', view=views.AccountActivationRequestView.as_view(), name='activation-request'),
    path(activation_ep, view=views.AccountActivationView.as_view(), name='activation-activate'),
]

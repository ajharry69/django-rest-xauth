from django.conf import settings

XAUTH, DATE_INPUT_FORMAT = {}, '%Y-%m-%d'
try:
    XAUTH = settings.XAUTH
    DATE_INPUT_FORMAT = settings.DATE_INPUT_FORMATS[0]
except (AttributeError, IndexError):
    pass
USER_LOOKUP_FIELD = XAUTH.get('USER_LOOKUP_FIELD', 'pk')
ACTIVATION_ENDPOINT = str(XAUTH.get('ACTIVATION_ENDPOINT', 'activation/confirm/'))
VERIFICATION_ENDPOINT = str(XAUTH.get('VERIFICATION_ENDPOINT', 'verification/confirm/'))
PASSWORD_RESET_ENDPOINT = str(XAUTH.get('PASSWORD_RESET_ENDPOINT', 'password/reset/confirm/'))
PROFILE_ENDPOINT = str(XAUTH.get('PROFILE_ENDPOINT', r'profile/(?P<pk>[0-9]+)/'))

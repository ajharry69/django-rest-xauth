from datetime import timedelta

from django.conf import settings
from django.utils.encoding import force_str

XAUTH, DATE_INPUT_FORMAT = {}, '%Y-%m-%d'
try:
    XAUTH = settings.XAUTH
    DATE_INPUT_FORMAT = settings.DATE_INPUT_FORMATS[0]
except (AttributeError, IndexError):
    pass
APP_NAME = XAUTH.get('APP_NAME', settings.ROOT_URLCONF.split('.', 1)[0].capitalize())
TOKEN_KEY = XAUTH.get('TOKEN_KEY', force_str(settings.SECRET_KEY))
USER_LOOKUP_FIELD = XAUTH.get('USER_LOOKUP_FIELD', 'pk')
ACTIVATION_ENDPOINT = str(XAUTH.get('ACTIVATION_ENDPOINT', 'activation/confirm/'))
VERIFICATION_ENDPOINT = str(XAUTH.get('VERIFICATION_ENDPOINT', 'verification/confirm/'))
PASSWORD_RESET_ENDPOINT = str(XAUTH.get('PASSWORD_RESET_ENDPOINT', 'password/reset/confirm/'))
PROFILE_ENDPOINT = str(XAUTH.get('PROFILE_ENDPOINT', r'profile/(?P<pk>[0-9]+)/'))
ACCOUNTS_EMAIL = str(XAUTH.get('ACCOUNTS_EMAIL', settings.EMAIL_HOST_USER))
REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES = list(XAUTH.get('REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES', [ACCOUNTS_EMAIL]))
ENFORCE_ACCOUNT_VERIFICATION = XAUTH.get('ENFORCE_ACCOUNT_VERIFICATION', True)
NEWBIE_VALIDITY_PERIOD = XAUTH.get('NEWBIE_VALIDITY_PERIOD', timedelta(days=1))
TOKEN_EXPIRY = XAUTH.get('TOKEN_EXPIRY', timedelta(days=60))
ACCOUNT_ACTIVATION_TOKEN_EXPIRY = XAUTH.get('ACCOUNT_ACTIVATION_TOKEN_EXPIRY', timedelta(days=1))
VERIFICATION_CODE_EXPIRY = XAUTH.get('VERIFICATION_CODE_EXPIRY', timedelta(hours=1))
TEMPORARY_PASSWORD_EXPIRY = XAUTH.get('TEMPORARY_PASSWORD_EXPIRY', timedelta(minutes=30))
VERIFICATION_CODE_LENGTH = XAUTH.get('VERIFICATION_CODE_LENGTH', 6)
TEMPORARY_PASSWORD_LENGTH = XAUTH.get('TEMPORARY_PASSWORD_LENGTH', 8)
REQUEST_TOKEN_ENCRYPTED = XAUTH.get('REQUEST_TOKEN_ENCRYPTED', True)
POST_REQUEST_USERNAME_FIELD = XAUTH.get('POST_REQUEST_USERNAME_FIELD', 'username')
POST_REQUEST_PASSWORD_FIELD = XAUTH.get('POST_REQUEST_PASSWORD_FIELD', 'password')
EMAIL_TEMPLATES_DIRECTORY = XAUTH.get('EMAIL_TEMPLATES_DIRECTORY', 'xauth/mails/')
EMAIL_TEMPLATE_SUFFIX = XAUTH.get('EMAIL_TEMPLATE_SUFFIX', 'html')
PASSWORD_LENGTH = 128
_SERIALIZERS = XAUTH.get('SERIALIZER_CLASSES', {
    'PROFILE': {
        'REQUEST': None,
        'RESPONSE': None,
    },
    'SIGNUP': {
        'REQUEST': None,
        'RESPONSE': None,
    },
})
_PROFILE_SERIALIZERS = XAUTH.get('PROFILE', {})
PROFILE_REQUEST_SERIALIZER = _PROFILE_SERIALIZERS.get('REQUEST', None)
PROFILE_RESPONSE_SERIALIZER = _PROFILE_SERIALIZERS.get('RESPONSE', None)
_SIGNUP_SERIALIZERS = XAUTH.get('SIGNUP', {})
SIGNUP_REQUEST_SERIALIZER = _SIGNUP_SERIALIZERS.get('REQUEST', None)
SIGNUP_RESPONSE_SERIALIZER = _SIGNUP_SERIALIZERS.get('RESPONSE', None)


def max_sign_in_attempts():
    """
    Gets and returns maximum sign-in attempts as defined in settings
    :return: tuple(max-attempts, metered). 2nd is a bool indicating
    whether sign-in attempts are metered or not
    """
    try:
        max_attempts = settings.XAUTH.get('MAXIMUM_SIGN_IN_ATTEMPTS', 0)
    except AttributeError:
        max_attempts = XAUTH.get('MAXIMUM_SIGN_IN_ATTEMPTS', 0)
    return max_attempts, max_attempts > 0

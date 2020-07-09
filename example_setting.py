from datetime import timedelta

XAUTH = {
    'APP_NAME': 'Demo App',
    'TOKEN_KEY': 'secretkey',
    'USER_LOOKUP_FIELD': 'pk',
    'ACTIVATION_ENDPOINT': 'activation/confirm/',
    'VERIFICATION_ENDPOINT': 'verification/confirm/',
    'PASSWORD_RESET_ENDPOINT': 'password/reset/confirm/',
    'PROFILE_ENDPOINT': r'profile/(?P<pk>[0-9]+)/',
    'ACCOUNTS_EMAIL': 'Accounts<accounts@mail.com>',
    'REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES': [],
    'ENFORCE_ACCOUNT_VERIFICATION': True,
    'NEWBIE_VALIDITY_PERIOD': timedelta(days=1),
    'TOKEN_EXPIRY': timedelta(days=60),
    'ACCOUNT_ACTIVATION_TOKEN_EXPIRY': timedelta(days=1),
    'VERIFICATION_CODE_EXPIRY': timedelta(hours=1),
    'TEMPORARY_PASSWORD_EXPIRY': timedelta(minutes=30),
    'VERIFICATION_CODE_LENGTH': 6,
    'TEMPORARY_PASSWORD_LENGTH': 8,
    'REQUEST_TOKEN_ENCRYPTED': True,
    'POST_REQUEST_USERNAME_FIELD': 'username',
    'POST_REQUEST_PASSWORD_FIELD': 'password',
    'EMAIL_TEMPLATES_DIRECTORY': 'xauth/mails/',
    'EMAIL_TEMPLATE_SUFFIX': 'html',
    'SERIALIZER_CLASSES': {
        'PROFILE': {
            'REQUEST': None,
            'RESPONSE': None,
        },
        'SIGN_UP': {
            'REQUEST': None,
            'RESPONSE': None,
        },
    },
}

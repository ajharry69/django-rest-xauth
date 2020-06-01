# Welcome to django-rest-xauth

[![Build Status](https://travis-ci.com/ajharry69/polarity.svg?branch=master)](https://travis-ci.com/ajharry69/polarity)
[![Coverage Status](https://coveralls.io/repos/github/ajharry69/polarity/badge.svg?branch=master)](https://coveralls.io/github/ajharry69/polarity?branch=master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/26f09088f70f46eda61633306b2147de)](https://app.codacy.com/manual/ajharry69/polarity?utm_source=github.com&utm_medium=referral&utm_content=ajharry69/polarity&utm_campaign=Badge_Grade_Dashboard)
[![Documentation Status](https://readthedocs.org/projects/polarity/badge/?version=latest)](https://polarity.readthedocs.io/en/latest/?badge=latest)

A [custom user model](https://docs.djangoproject.com/en/dev/topics/auth/customizing/) 
based package that offers numerous features from JWT and Basic authentication to REST API end-points for signup,signin,
email verification, password resetting and account activation.
 
Email verification and password resetting are based on hashed verification-code and temporary password respectively. And 
account activation is based on a combination of user selected security question(provided through the admin portal by site 
administrator(superuser)) and an answer. For example, a user could configure **what is your favorite color?** security 
question and provide **white** as an answer then in case a users account was deactivate he/she will be required to provide 
the same answer to the same question to re-activate a his/her account.

## Classes dependency structure

`TokenKey` > `Token` > `User` > `AuthenticationBackend` > `Serializer` > `View` > `url_patterns`

Most of the package's features are designed to be independently usable and customizable to suit most needs.

>**NOTE:** the  closer the dependency(use) get to the `url_patterns` the harder it becomes to extend and customize the 
>classes and features before it's predecessor. For example, modifying a `Serializer` without modifying it's dependant 
>`View` and still using unmodified `url_patterns` would most likely result in unexpected behaviour. But on the other 
>hand an extension to the `User` class without a dependency on it's dependant classes(`AuthenticationBackend` e.t.c) 
>will most likely work as expected.

## What makes django-rest-xauth different?

- Custom user class provides most common **optional** fields with reasonable complementary-helper methods e.g. 
`date_of_birth` field that also comes with an age-calculation helper method to help estimate users age
- Access logging(IP-address should be provided as a `X-Forwarded-For` header)
- Failed Sign-in attempts logging(IP-address should be provided as a `X-Forwarded-For` header)
- Password-reset logging(IP-address should be provided as a `X-Forwarded-For` header)
- Encrypted JWT tokens
- Security question based account activation in-case account was deactivated
- Mobile apps friendly:
    - temporary password based user password reset
    - verification code based user account activation.

>**N/B:** _temporary passwords_ and _verification codes_ are both generated and returned from the `User` model hence 
>opting to SMS based sending of the _verification codes_ and _temporary passwords_ should be as easy as extending the 
>`User` model, overriding a single method(that also generates and returns the code) and finally changing django's 
>`AUTH_USER_MODEL` to your model name as [explained here](https://docs.djangoproject.com/en/dev/topics/auth/customizing/).

## Getting started
Add the following to your Django project's `settings.py` file

```python
AUTH_USER_MODEL = 'xauth.User'

INSTALLED_APPS = [
'xauth'
]

XAUTH = {
    # occasionally included in emails sent by the API to your users for familiarity
    'APP_NAME': 'Xently',
    'TOKEN_KEY': force_str(SECRET_KEY),
    'TOKEN_EXPIRY': timedelta(days=60),
    # string. Email addresses to which account / auth-related replies are to be sent.
    # Also permitted: "Name <email-address>"
    'REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES': [
        settings.EMAIL_HOST_USER
    ],
    # string. Email used to send verification code.
    # Also permitted: "Name <email-address>"
    'ACCOUNTS_EMAIL': settings.EMAIL_HOST_USER,
    'ACCOUNTS_EMAIL_PASSWORD': settings.EMAIL_HOST_PASSWORD,
    'VERIFICATION_CODE_LENGTH': 6,
    'TEMPORARY_PASSWORD_LENGTH': 8,
    'VERIFICATION_CODE_EXPIRY': timedelta(hours=1),
    'TEMPORARY_PASSWORD_EXPIRY': timedelta(minutes=30),
    'ACCOUNT_ACTIVATION_TOKEN_EXPIRY': timedelta(days=1),
    # period within which a user is considered new since account creation date
    'NEWBIE_VALIDITY_PERIOD': timedelta(days=1),
    'AUTO_HASH_PASSWORD_ON_SAVE': True,
    'WRAP_DRF_RESPONSE': True,
    'REQUEST_TOKEN_ENCRYPTED': True,
    'POST_REQUEST_USERNAME_FIELD': 'username',
    'POST_REQUEST_PASSWORD_FIELD': 'password',
    'ENFORCE_ACCOUNT_VERIFICATION': True,
    # attempts upon which account is to be deactivated after failed sign-in attempts is reached.
    # 0 or less means no limit
    'MAXIMUM_SIGN_IN_ATTEMPTS': 0,
    'VERIFICATION_ENDPOINT': 'verification-code/verify/',
    'PASSWORD_RESET_ENDPOINT': 'password-reset/verify/',
    'ACTIVATION_ENDPOINT': 'activation/activate/',
    # 0 = both(encrypted&non-encrypted),1 = encrypted only, 2 = non-encrypted only
    'RETURN_TOKEN_TYPE': 0,  
}
```
# Settings
You can customize the `django-rest-xauth` default behaviour by providing `XAUTH` setting in your django project's 
`settings.py` file like below.

```python
XAUTH = {
    'TOKEN_EXPIRY': timedelta(days=60),
    'AUTO_HASH_PASSWORD_ON_SAVE': True,
    'ENFORCE_ACCOUNT_VERIFICATION': True,
    ...,
}
```

**NOTE:** All `XAUTH` setting names must be written in **capital letters(uppercase)** for a setting to take effect.

## APP_NAME
**Type**: `str`

**Default**: ''

**Usage**: occasionally included in emails sent by the API to your users as a source identity

## TOKEN_KEY
**Type**: `str`

**Default**: `SECRET_KEY` provided by django during project creation

**Usage**: for token signing

## TOKEN_EXPIRY
**Type**: `timedelta`

**Default**: `timedelta(days=60)`

**Usage**: period within which a resource-access token should be considered valid

## VERIFICATION_CODE_EXPIRY
**Type**: `timedelta`

**Default**: `timedelta(hours=1)`

**Usage**: period within which an account verification code and token(verification) should be considered valid.

**Note:** if you have `xauth.authentication.BasicTokenAuthentication` as the first option in `REST_FRAMEWORK`'s 
`DEFAULT_AUTHENTICATION_CLASSES` in your settings, this token will not be usable for any other purpose other than account verification 
through the endpoint provided by `VERIFICATION_ENDPOINT` in `XAUTH` settings.

## TEMPORARY_PASSWORD_EXPIRY
**Type**: `timedelta`

**Default**: `timedelta(minutes=30)`

**Usage**: period within which a password-reset temporary password and token(generated when password reset is requested)
 should be considered valid.
 
**Note:** if you have `xauth.authentication.BasicTokenAuthentication` as the first option in `REST_FRAMEWORK`'s 
`DEFAULT_AUTHENTICATION_CLASSES` in your settings, this token will not be usable for any other purpose other than password-reset through the 
endpoint provided by `PASSWORD_RESET_ENDPOINT` in `XAUTH` settings.

## ACCOUNT_ACTIVATION_TOKEN_EXPIRY
**Type**: `timedelta`

**Default**: `timedelta(days=1)`

**Usage**: period within which an account activation token(generated when account activation is requested after 
deactivation) should be considered valid.

**Note:** if you have `xauth.authentication.BasicTokenAuthentication` as the first option in `REST_FRAMEWORK`'s 
`DEFAULT_AUTHENTICATION_CLASSES` in your settings, this token will not be usable for any other purpose other than 
account activation through the endpoint provided by `ACTIVATION_ENDPOINT` in `XAUTH` settings.

## REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES
**Type**: `list`

**Default**: `[ settings.EMAIL_HOST_USER, ]`. `settings` is from `django.conf.setting` module

**Usage**: email address(es) to which replies of emails sent(account verification and password reset) to users through 
the `django-rest-xauth` should be channelled.

## ACCOUNTS_EMAIL
**Type**: `str`

**Default**: `settings.EMAIL_HOST_USER`. `settings` is from `django.conf.setting` module

**Usage**: email address for sending (verification codes and temporary password e.t.c.) from `django-rest-xauth`.

## VERIFICATION_CODE_LENGTH
**Type**: `int`

**Default**: 6

**Usage**: determines the length of the generated verification code(sent to user) to be used for account verification.

## TEMPORARY_PASSWORD_LENGTH
**Type**: `int`

**Default**: 8

**Usage**: determines the length of the generated temporary password(sent to user) to be used for password reset.

## NEWBIE_VALIDITY_PERIOD
**Type**: `timedelta`

**Default**: `timedelta(days=1)`

**Usage**: period within which a user will be considered new from the time of account creation.

## AUTO_HASH_PASSWORD_ON_SAVE
**Type**: `bool`

**Default**: `True`

**Usage**: if `True` user's password will be hashed whenever save method is called

## WRAP_DRF_RESPONSE
**Type**: `bool`

**Default**: `False`

**Usage**: if `True` json responses will be in the format illustrated
```json
{
  "is_error": true,
  "status_code": 200,
  "message": "message",
  "debug_message": "debug message",
  "payload": ...,
  "metadata": ...,
}
```
`payload` key will now contain the data that would otherwise been shown before setting to `True`

## POST_REQUEST_USERNAME_FIELD
**Type**: `str`

**Default**: 'username'

**Usage**: used to retrieve `username` from a POST request sign-in/login.

## POST_REQUEST_PASSWORD_FIELD
**Type**: `str`

**Default**: 'password'

**Usage**: used to retrieve `password` from a POST request sign-in/login. 

## ENFORCE_ACCOUNT_VERIFICATION
**Type**: `bool`

**Default**: `True`

**Usage**: determines whether users should be forced to verify their accounts after account creation(registration/signup).

## MAXIMUM_SIGN_IN_ATTEMPTS
**Type**: `int`

**Default**: 0

**Usage**: attempts upon which account is to be deactivated after failed sign-in attempts is reached. Value of `0` or 
less means no limit should be enforced hence no account deactivation due to sign-in attempts limit.

## VERIFICATION_ENDPOINT
**Type**: `str`

**Default**: 'verification-code/verify/'

**Usage**: used to create a url through which account verification code should be verified/validated for correctness 
before account is considered verified.

## PASSWORD_RESET_ENDPOINT
**Type**: `str`

**Default**: 'password-reset/verify/'

**Usage**: used to create a url through which password-reset temporary password should be verified/validated for 
correctness before user's password is changed to a new one(provided through a **POST** request in the same url).

## ACTIVATION_ENDPOINT
**Type**: `str`

**Default**: 'activation/activate/'

**Usage**: used to create a url through which user's security question's answer will be verified/validated for 
correctness before account is considered activated.

[basic-auth-scheme]: https://www.wikipedia.com/
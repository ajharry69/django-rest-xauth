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

## USER_PROFILE_SERIALIZER
**Type:** `str`

**Default:** 'xauth.serializers.ProfileSerializer'

**Usage:** Serializers allow complex data such as querysets and model instances to be converted to native Python data 
types that can then be easily rendered into JSON, XML or other content types. More on serializers can be found 
[here][drf-serializer-url] or [here][drf-serializer-tutorial-url].

**Note:** `fields` declared in this serializer will be inherited by `xauth.serializer.SignUpSerializer` with addition 
of `password` field that is only relevant for sign-up.

### Guidelines
`django-rest-xauth` makes the following assumptions of the serializer class it expects from this setting:

 1. It is a direct or indirect subclass of `rest_framework.serializers.Serializer`.
 2. It contains a nested `Meta` class which contains a `model` and `fields` properties.

**Consider an example of this default serializer class**
```python
from rest_framework import serializers
from django.contrib.auth import get_user_model

class ProfileSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='xauth:profile')

    class Meta:
        model = get_user_model()
        fields = tuple(get_user_model().PUBLIC_READ_WRITE_FIELDS) + ('url',)
        read_only_fields = tuple(get_user_model().READ_ONLY_FIELDS)
```

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

**Default**: `6`

**Usage**: determines the length of the generated verification code(sent to user) to be used for account verification.

## TEMPORARY_PASSWORD_LENGTH
**Type**: `int`

**Default**: `8`

**Usage**: determines the length of the generated temporary password(sent to user) to be used for password reset.

## NEWBIE_VALIDITY_PERIOD
**Type**: `timedelta`

**Default**: `timedelta(days=1)`

**Usage**: period within which a user will be considered new from the time of account creation.

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

**Default**: `username`

**Usage**: used to retrieve `username` from a POST request sign-in/login.

## POST_REQUEST_PASSWORD_FIELD
**Type**: `str`

**Default**: `password`

**Usage**: used to retrieve `password` from a POST request sign-in/login. 

## ENFORCE_ACCOUNT_VERIFICATION
**Type**: `bool`

**Default**: `True`

**Usage**: determines whether users should be forced to verify their accounts after account creation(registration/signup).

## MAXIMUM_SIGN_IN_ATTEMPTS
**Type**: `int`

**Default**: `0`

**Usage**: attempts upon which account is to be deactivated after failed sign-in attempts is reached. Value of `0` or 
less means no limit should be enforced hence no account deactivation due to sign-in attempts limit.

## USER_LOOKUP_FIELD
**Type**: `str`

**Default**: `pk`. Should be one of `xauth.models.User` **unique** [fields][user-model-fields-url] e.g. 'pk', 'id', 
'username' e.t.c

**Usage**: used together with [PROFILE_ENDPOINT][profile-endpoint-setting-url] setting to build up a single user profile
hence a change to either setting would require a change on the other as they are mutually inclusive.

## PROFILE_ENDPOINT
**Type**: `str`

**Default**: `profile/(?P<pk>[0-9]+)/`

**Usage**: used together with [USER_LOOKUP_FIELD][user-lookup-field-setting-url] setting to build up a single user profile
hence a change to either setting would require a change on the other as they are mutually inclusive.

## VERIFICATION_ENDPOINT
**Type**: `str`

**Default**: `verification/confirm/`

**Usage**: used to create a url through which account verification code should be verified/validated for correctness 
before account is considered verified.

## PASSWORD_RESET_ENDPOINT
**Type**: `str`

**Default**: `password/reset/confirm/`

**Usage**: used to create a url through which password-reset temporary password should be verified/validated for 
correctness before user's password is changed to a new one(provided through a **POST** request in the same url).

## ACTIVATION_ENDPOINT
**Type**: `str`

**Default**: `activation/confirm/`

**Usage**: used to create a url through which user's security question's answer will be verified/validated for 
correctness before account is considered activated.

[basic-auth-scheme]: https://en.wikipedia.org/wiki/Basic_access_authentication
[drf-serializer-url]: https://www.django-rest-framework.org/api-guide/serializers/
[drf-serializer-tutorial-url]: https://www.django-rest-framework.org/tutorial/1-serialization/
[user-model-fields-url]: https://django-rest-xauth.readthedocs.io/en/latest/api-guide/classes/user/properties/
[user-lookup-field-setting-url]: https://django-rest-xauth.readthedocs.io/en/latest/api-guide/settings/#USER_LOOKUP_FIELD
[profile-endpoint-setting-url]: https://django-rest-xauth.readthedocs.io/en/latest/api-guide/settings/#PROFILE_ENDPOINT
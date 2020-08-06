# Welcome to django-rest-xauth

[![Build Status](https://travis-ci.com/ajharry69/django-rest-xauth.svg?branch=master)](https://travis-ci.com/ajharry69/django-rest-xauth)
[![Coverage Status](https://coveralls.io/repos/github/ajharry69/django-rest-xauth/badge.svg?branch=master)](https://coveralls.io/github/ajharry69/django-rest-xauth?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/5c5b5dbbe3204b3bae605d6b81800d73)](https://www.codacy.com/manual/ajharry69/django-rest-xauth?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ajharry69/django-rest-xauth&amp;utm_campaign=Badge_Grade)
[![Documentation Status](https://readthedocs.org/projects/django-rest-xauth/badge/?version=latest)](https://django-rest-xauth.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/django-rest-xauth.svg)](https://badge.fury.io/py/django-rest-xauth)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-rest-xauth)

A [custom user model][django-customizing-user-model-url] based django-package to implement [JWT][jwt-url] and 
[Basic][basic-auth-url] authentication and authorization flow in a few simple steps.

The package provides ready to use JSON formatted REST API end-points for signup, sign-in, email verification, password 
reset and account activation.
 
Email verification and password reset are based on hashed, short-lived verification-code and temporary password. 
Account activation is based on a combination of user selected security question(provided through the admin portal by 
site administrator(superuser)) and an answer that is hashed and stored in the database.

By design, the logic for requesting and confirming password reset, account verification and activation is implemented in 
the `AbstractUser` model class to make it easy to customize every step. For example, instead of sending verification codes 
to users via email(default), you could opt to use SMS by overriding `request_verification(...)` method in the abstract 
class or using the returned code in your views.

## What makes django-rest-xauth different

- Custom user class provides some common **optional** fields with reasonable complementary helper methods. For example, 
`date_of_birth` field that also comes with an age calculation helper method
- Access logging(IP-address should be provided as a `X-Forwarded-For` header)
- Failed Sign-in attempts logging(IP-address should be provided as a `X-Forwarded-For` header)
- Password-reset logging(IP-address should be provided as a `X-Forwarded-For` header)
- Encrypted JWT tokens
- Security question based account activation in-case account was deactivated
- Temporary password based user password reset
- Verification code based user account activation.

## Quick start
- Install package `pip install django-rest-xauth`

### Modify your Django project's `settings.py` file

- Add **xauth** to your `INSTALLED_APPS` setting like this
```python
INSTALLED_APPS = [
    ...,
    'xauth',
    'rest_framework',
]
```
- Add/modify your `AUTH_USER_MODEL` setting to
```python
# Can also be a (modified) direct subclass of `xauth.models.AbstractUser`
AUTH_USER_MODEL = 'xauth.User'
```
- Add/modify your `REST_FRAMEWORK` setting to
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'xauth.authentication.BasicTokenAuthentication',
        ...,
    ],
    'EXCEPTION_HANDLER': 'xauth.utils.exceptions.exception_handler',
}
```
- Include the xauth URLconf in your project `urls.py` like this
```python
urlpatterns = [
    path('accounts/', include('xauth.urls', namespace='xauth')),
    ...,
]
```
- Run `python manage.py migrate` to create the xauth models.
- Run `python manage.py createsuperuser` to create a superuser account.
- Run `python manage.py runserver` to start the development server.
- Visit `http://127.0.0.1:8000/accounts/signup/` to register a new account.

## API endpoints
Read more [here][documentation-endpoints-url].

## Documentation and support
Full documentation for the project is available [here][documentation-url].

## Contributing
Please be sure to review [contributing guidelines](docs/about/contributing.md) to learn how to help the project.

## Postman Team
[Join][postman-team-join-url] postman team.

[jwt-url]: https://jwt.io/
[basic-auth-url]: https://en.wikipedia.org/wiki/Basic_access_authentication
[postman-team-join-url]: https://app.getpostman.com/join-team?invite_code=b3ee38bf5dc02c6e7be11bd2e2e15573&ws=5e9ffb87-2dc7-4778-aece-4c8230419340
[django-auth-user-model-setting-url]: https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
[django-customizing-user-model-url]: https://docs.djangoproject.com/en/dev/topics/auth/customizing/
[documentation-url]: https://django-rest-xauth.readthedocs.io/en/latest/
[documentation-endpoints-url]: https://django-rest-xauth.readthedocs.io/en/latest/api-guide/endpoints/

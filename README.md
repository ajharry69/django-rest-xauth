# Welcome to django-rest-xauth

[![Build Status](https://travis-ci.com/ajharry69/django-rest-xauth.svg?branch=master)](https://travis-ci.com/ajharry69/django-rest-xauth)
[![Coverage Status](https://coveralls.io/repos/github/ajharry69/django-rest-xauth/badge.svg?branch=master)](https://coveralls.io/github/ajharry69/django-rest-xauth?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/5c5b5dbbe3204b3bae605d6b81800d73)](https://www.codacy.com/manual/ajharry69/django-rest-xauth?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ajharry69/django-rest-xauth&amp;utm_campaign=Badge_Grade)
[![Documentation Status](https://readthedocs.org/projects/django-rest-xauth/badge/?version=latest)](https://django-rest-xauth.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/django-rest-xauth.svg)](https://badge.fury.io/py/django-rest-xauth)

A [custom user model](https://docs.djangoproject.com/en/dev/topics/auth/customizing/) 
based package with features ranging from JWT and Basic authentication to REST API end-points for signup,signin,
email verification, password resetting and account activation.
 
Email verification and password resetting are based on hashed verification-code and temporary password respectively. And 
account activation is based on a combination of user selected security question(provided through the admin portal by site 
administrator(superuser)) and an answer.

## Classes dependency structure

`TokenKey` > `Token` > `User` > `AuthenticationBackend` > `Serializer` > `View` > `url_patterns`

Most of the package's features are designed to be independently usable and customizable to suit most needs.

>**NOTE:** the  closer the dependency(use) get to the `url_patterns` the harder it becomes to extend and customize the 
>classes and features before it's predecessor. For example, modifying a `Serializer` without modifying it's dependant 
>`View` and still using unmodified `url_patterns` would most likely result in unexpected behaviour. But on the other 
>hand an extension to the `User` class without a dependency on it's dependant classes(`AuthenticationBackend` e.t.c) 
>will most likely work as expected.

## What makes django-rest-xauth different

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

## Quick start
Add the following to your Django project's `settings.py` file

- Install package `pip install django-rest-xauth`
- Add **xauth** to your `INSTALLED_APPS` setting like this
```python
INSTALLED_APPS = [
    ...,
    'xauth',
]
```
- Add/modify your `AUTH_USER_MODEL` setting to
```python
AUTH_USER_MODEL = 'xauth.User'
```
- Add/modify your `REST_FRAMEWORK` setting to
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'xauth.authentication.BasicTokenAuthentication',
        ...,
    ],
    'EXCEPTION_HANDLER': 'xauth.utils.exceptions.xauth_exception_handler',
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
- Start the development server and visit http://127.0.0.1:8000/accounts/signup/ to register a new account.

## API endpoints
| Endpoint | Purpose | Method | Content-Type |
| ---- | ------ | --- | ---- |
| signup/ | User registration | POST | application/json |
| signin/ | User login | POST | application/x-www-form-urlencoded |
| signout/ | User logout | POST | application/x-www-form-urlencoded |
| profile/{id}/ | Profile access(read)/update/delete | GET/PUT/PATCH/DELETE | application/json |
| verification-code/request/ | Requesting new verification code | POST | application/x-www-form-urlencoded |
| verification-code/verify/ | Verifying verification code | POST | application/x-www-form-urlencoded |
| password-reset/request/ | Requesting new temporary password for password reset | POST | application/x-www-form-urlencoded |
| password-reset/verify/ | Verifying temporary password | POST | application/x-www-form-urlencoded |
| activation/request/ | Requesting account activation. | POST | application/x-www-form-urlencoded |
| activation/verify/ | Verifying security question's answer | POST | application/x-www-form-urlencoded |
| security-question/add/ | Adding/attaching security question and answer to user account | POST | application/x-www-form-urlencoded |
| security-questions/ | Retrieving a list of security questions | GET | application/x-www-form-urlencoded |

## Documentation and support
Full documentation for the project is available [here](http://django-rext-xauth.readthedocs.io/)

## Contributing
Please be sure to review [contributing guidelines](CONTRIBUTING.md) to learn how to help the project.

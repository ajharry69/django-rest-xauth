# Welcome to django-rest-xauth

A [custom user model][django-customizing-user-model-url] based django-package that implements [JWT][jwt-url]
authentication and authorization flow in a few simple steps.

The package provides ready to use JSON formatted REST API end-points for signup, signin, (email) verification, password
reset e.t.c.

(Email) verification and password reset features are both based on hashed short-lived verification code and temporary
passwords, respectively. The account activation feature is based on a combination of the user's previously selected
security question (provided through the admin portal by the site administrator) and an arbitrary answer that will be
hashed and stored in the database.

By design, the logic for requesting and confirming password reset, account verification and activation is implemented in
the `AbstractUser` model class to make it easy to customize every step. For example, instead of sending verification
codes to users via email (default), you could opt to use SMS by overriding `request_verification(...)` method in the
abstract class or using the returned code in your views.

## Quick start

- Install package `pip install django-rest-xauth`

- **Optionally** create a new django app in which you'll have
  your [custom user model][django-customizing-user-model-url] that extends `xauth.accounts.abstract_models.AbstractUser`

### Modify project's `settings.py` file

- Add **<path to your new app's `AppConfig`>** to your `INSTALLED_APPS` setting like this

```python
INSTALLED_APPS = [
    ...,
    "xauth.accounts.apps.AppConfig",  # TODO: Should replace with <path to your new app's `AppConfig`>
    "rest_framework",
]
```

- Add/modify your `AUTH_USER_MODEL` setting to

```python
# Can also be a (modified) direct subclass of `xauth.accounts.models.AbstractUser`
AUTH_USER_MODEL = "xauth.User"  # TODO: Should replace with your `<new app's label>.<new app's custom user model>`
```

- Add/modify your `REST_FRAMEWORK` setting to

```python
from xauth import settings

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"],
}
```

- Include the xauth URLconf in your project `urls.py` like this

```djangourlpath
urlpatterns = [
    path("", include('xauth.urls', namespace='xauth')),
    ...,
]
```

OR, register your own URLs from the `ViewSet`(s) in `xauth.accounts.views` module.

- Run `python manage.py migrate` to create the xauth models.
- Run `python manage.py createsuperuser` to create a superuser account.
- Run `python manage.py runserver` to start the development server.
- Visit `http://127.0.0.1:8000/accounts/signup/` to register a new account.

[jwt-url]: https://jwt.io/

[django-customizing-user-model-url]: https://docs.djangoproject.com/en/dev/topics/auth/customizing/

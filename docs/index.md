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

- Install package `pip install django-rest-xauth`.
- Add `xauth.apps.AppConfig` to `INSTALLED_APPS` setting. This will expose the management command used in next step - it
  will not be necessary after that. Therefore, it can be uninstalled/removed safely from `INSTALLED_APPS`.
- Run `./manage.py create_xauth_app <path-to-xauth-app>` e.g. `./manage.py create_xauth_app accounts/` and follow
  further instructions as per the output of the command. _Only run once - during initial setup_.
- Run `./manage.py makemigrations`.
- Include xauth `URLconf` in your project's `urls.py` as
  follows: `urlpatterns = [path("", include("xauth.urls")), ...,]` **OR**, register your own URLs from the `ViewSet`(s)
  in `xauth.accounts.views` module.
- Run `python manage.py migrate` to create the xauth models.
- Run `python manage.py createsuperuser` to create a superuser account.
- Run `python manage.py runserver` to start the development server.
- Visit `http://127.0.0.1:8000/accounts/signup/` to register a new account.

[jwt-url]: https://jwt.io/

[django-customizing-user-model-url]: https://docs.djangoproject.com/en/dev/topics/auth/customizing/

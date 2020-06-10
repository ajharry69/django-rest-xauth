# Customizing emails
To customize emails, you will need to:

1. Create email templates with names similar to the default(found in `xauth/templates/xauth/mails/` directory). Using a 
different file extension will require an update to `EMAIL_TEMPLATE_SUFFIX` setting in `XAUTH` settings.
2. Update or provide the directory to your templates using `EMAIL_TEMPLATES_DIRECTORY` setting in `XAUTH` settings.
3. A knowledge of working with [django-templated-email][django-templated-email-url] package's email templates could be 
of help as the `django-rest-xauth` depends on it to work with templates in emails.

**NOTE:** Every template has a `dict` of **context** properties provided to it as mentioned below

## verification-request
```python
context = {
    'code': 'XXXXXX',  # generated when verification is requested
    'user': 'instance of user',
    'app_name': 'XXXXXX',  # retireved from `XAUTH`'s `APP_NAME` setting
}

```

## password-reset-request
```python
context = {
    'password': 'XXXXXXXX',  # generated when password reset is requested
    'user': 'instance of user',
    'app_name': 'XXXXXX',  # retireved from `XAUTH`'s `APP_NAME` setting
}

```

[django-templated-email-url]: https://github.com/vintasoftware/django-templated-email
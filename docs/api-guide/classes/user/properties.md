# Properties
Class properties present in the `django-rest-xauth`'s `User` model class.

**`models` comes from `django.db.models` submodule.**

## username
**Type:** `models.CharField(unique=True,...)`

**Default:** value of `email` property

## email
**Type:** `models.EmailField(unique=True,...)`

## surname
**Type:** `models.CharField(...)`

**Default:** `None` since it is an optional field.

## first_name
**Type:** `models.CharField(...)`

**Default:** `None` since it is an optional field.

## last_name
**Type:** `models.CharField(...)`

**Default:** `None` since it is an optional field.

## mobile_number
**Type:** `models.CharField(...)`

**Default:** `None` since it is an optional field.

## date_of_birth
**Type:** `models.DateField(null=True, blank=True,)`

**Default:** `None` since it is an optional field.

## provider
**Type:** `models.CharField(...)`

**Default:** 'EMAIL'

Name of authentication provider from choices of **GOOGLE**, **APPLE**, **FACEBOOK**, **TWITTER** e.t.c

## is_superuser
**Type:** `models.BooleanField(default=False,...)`

**Default:** `False`

## is_staff
**Type:** `models.BooleanField(default=False,...)`

**Default:** `False`

## is_verified
**Type:** `models.BooleanField(default=False,...)`

**Default:** Depends on the negated(opposite) value of `XAUTH`'s `ENFORCE_ACCOUNT_VERIFICATION` [setting](/docs/api-guide/settings.md).

## is_active
**Type:** `models.BooleanField(default=True,...)`

## created_at
**Type:** `models.DateTimeField(auto_add_now=True,...)`

## updated_at
**Type:** `models.DateTimeField(auto_now=True,...)`

## Dynamic properties
### device_ip
**Type:** `str`.

**Contains setter:** `True`

Is initialized to user's device ip-address(as received from `X-Forwarded-For` request header) from which http request was sent.

### token
**Type:** `utils.Token`. `Token` is a class within the package in `token` submodule in `util` package.

**Contains setter:** `False`

### password_reset_token
**Type:** `utils.Token`. `Token` is a class within the package in `token` submodule in `util` package.

**Contains setter:** `False`

### verification_token
**Type:** `utils.Token`. `Token` is a class within the package in `token` submodule in `util` package.

**Contains setter:** `False`

### activation_token
**Type:** `utils.Token`. `Token` is a class within the package in `token` submodule in `util` package.

**Contains setter:** `False`

## Meta-properties
### USERNAME_FIELD
**Type:** `str`

**Default:** 'username'

See use [here][username-field-url]

### EMAIL_FIELD
**Type:** `str`

**Default:** 'email'

See use [here][email-field-url]

### REQUIRED_FIELDS
**Type:** `list`

**Default:** `['email', 'first_name', 'last_name', ]`

See use [here][required-fields-url]

### READ_ONLY_FIELDS
**Type:** `tuple`

**Default:** `('id', 'is_superuser', 'is_staff', 'is_verified',)`

All the fields listed here(including the `USERNAME_FIELD` and `password`) are expected as part of parameters in `objects`(UserManager).create_superuser

### WRITE_ONLY_FIELDS
**Type:** `tuple`

**Default:** `('password',)`

Contains fields that are "safe" to access publicly but proper caution should be taken before modification.

### NULLABLE_FIELDS
**Type:** `tuple`

**Default:** `('surname', 'first_name', 'last_name', 'mobile_number', 'date_of_birth',)`

Contains fields that are likely to have a null(`None`) value

### PUBLIC_READ_WRITE_FIELDS
**Type:** `tuple`

**Default:** `('username', 'email', 'provider',) + NULLABLE_FIELDS + READ_ONLY_FIELDS`

Contains fields that are "safe" to access publicly.

[username-field-url]: https://docs.djangoproject.com/en/dev/topics/auth/customizing/#django.contrib.auth.models.CustomUser.USERNAME_FIELD
[email-field-url]: https://docs.djangoproject.com/en/dev/topics/auth/customizing/#django.contrib.auth.models.CustomUser.EMAIL_FIELD
[required-fields-url]: https://docs.djangoproject.com/en/dev/topics/auth/customizing/#django.contrib.auth.models.CustomUser.REQUIRED_FIELDS
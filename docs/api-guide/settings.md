# Settings

You can customize the `django-rest-xauth` default behaviour by providing `XAUTH` setting in your django project's
`settings.py` file like below.

| Setting | Default | Description |
| ---- | --- | ----- |
| `XAUTH_ENFORCE_ACCOUNT_VERIFICATION` | `True` | Checks if user account is verified before returning access token otherwise account verification token is returned |
| `XAUTH_PASSWORD_RESET_REQUEST_SUBJECT` | `"Password Reset Request"` |  |
| `XAUTH_VERIFICATION_REQUEST_SUBJECT` | `"Account Verification"` |  |
| `XAUTH_ACCESS_TOKEN_EXPIRY` | `timedelta(days=1)` |  |
| `XAUTH_VERIFICATION_CODE_EXPIRY` | `timedelta(minutes=30)` |  |
| `XAUTH_TEMPORARY_PASSWORD_EXPIRY` | `timedelta(minutes=30)` |  |
| `XAUTH_ACCOUNT_ACTIVATION_TOKEN_EXPIRY` | `timedelta(minutes=30)` |  |
| `XAUTH_SENDER_ADDRESS` | `settings.EMAIL_HOST_USER` |  |
| `SENDER_ADDRESS_PASSWORD` | `settings.EMAIL_HOST_PASSWORD` |  |
| `XAUTH_REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES` | `None` |  |
| `XAUTH_DATE_INPUT_FORMAT` | `settings.DATE_INPUT_FORMATS[0]` |  |
| `XAUTH_GENERATE_ENCRYPTED_TOKENS` | `True` |  |
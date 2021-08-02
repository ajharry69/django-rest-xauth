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
| `XAUTH_SENDER_ADDRESS_PASSWORD` | `settings.EMAIL_HOST_PASSWORD` |  |
| `XAUTH_REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES` | `None` |  |
| `XAUTH_GENERATE_ENCRYPTED_TOKENS` | `True` | Indicates a need to generate encrypted JWT token(s) |
| `XAUTH_AUTH_APP_LABEL` | `accounts` | Which app should the dependant classes be installed |
| `XAUTH_KEYS_DIR` | `.secrets folder at repo root` | Folder to store the keys generated to sign and verify JWT token |
| `XAUTH_JWT_SIG_ALG` | `RS256` | Signing algorithm for JWT token |
| `XAUTH_MAKE_KEY_DIRS` | `True` | Whether to automatically create `KEYS_DIR` if they don't already exist |
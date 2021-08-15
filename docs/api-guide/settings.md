# Settings

You can customize the `django-rest-xauth` default behaviour by providing `XAUTH` setting in your django project's
`settings.py` file like below.

| Setting | Default | Description |
| ---- | --- | ----- |
| `XAUTH_ENFORCE_ACCOUNT_VERIFICATION` | `True` | Checks if user account is verified before returning access token otherwise account verification token is returned. |
| `XAUTH_PASSWORD_RESET_REQUEST_SUBJECT` | `"Password Reset Request"` | Used as a subject for email of OTP (temporary password) email sent by `xauth` from email referenced by `XAUTH_SENDER_ADDRESS` setting. |
| `XAUTH_VERIFICATION_REQUEST_SUBJECT` | `"Account Verification"` | Used as a subject for email of OTP (verification code) email sent by `xauth` from email referenced by `XAUTH_SENDER_ADDRESS` setting. |
| `XAUTH_ACCESS_TOKEN_EXPIRY` | `timedelta(days=1)` | Duration after which (server resource) access token should be considered expired. |
| `XAUTH_ACCOUNT_VERIFICATION_TOKEN_EXPIRY` | `timedelta(minutes=30)` | Duration after which account verification token should be considered expired. |
| `XAUTH_PASSWORD_RESET_TOKEN_EXPIRY` | `timedelta(minutes=30)` | Duration after which password reset token should be considered expired. |
| `XAUTH_ACCOUNT_ACTIVATION_TOKEN_EXPIRY` | `timedelta(minutes=30)` | Duration after which account activation token should be considered expired. |
| `XAUTH_SENDER_ADDRESS` | `settings.EMAIL_HOST_USER` | Email from which `xauth`-related emails should be sent. |
| `XAUTH_SENDER_ADDRESS_PASSWORD` | `settings.EMAIL_HOST_PASSWORD` | Used to authenticate `XAUTH_SENDER_ADDRESS` when sending emails. |
| `XAUTH_REPLY_TO_ACCOUNTS_EMAIL_ADDRESSES` | `None` | Email(s) to which replies of `xauth`-related emails should go. |
| `XAUTH_VERIFY_ENCRYPTED_TOKEN` | `True` | Verify bearer token from `Authorization` header as an encrypted JWT token. |
| `XAUTH_AUTH_APP_LABEL` | `accounts` | Which app(-label) should the dependant classes be associated with. This eases overriding of classes within modules in `xauth.accounts`. |
| `XAUTH_KEYS_DIR` | `.secrets folder at repo root` | Folder to store the keys generated to sign and verify JWT token. |
| `XAUTH_JWT_SIG_ALG` | `RS256` | Signing algorithm for JWT token. |
| `XAUTH_MAKE_KEY_DIRS` | `True` | Whether to automatically create `KEYS_DIR` if they don't already exist. |
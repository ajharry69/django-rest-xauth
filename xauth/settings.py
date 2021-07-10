__all__ = ["REST_FRAMEWORK", "AUTH_USER_MODEL"]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "xauth.authentication.JWTTokenAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

AUTH_USER_MODEL = "accounts.User"

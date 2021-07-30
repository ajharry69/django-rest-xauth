__all__ = ["REST_FRAMEWORK", "AUTH_USER_MODEL"]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "xauth.authentication.JWTTokenAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}

AUTH_USER_MODEL = "xauth.User"

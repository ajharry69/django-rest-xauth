__all__ = ["REST_FRAMEWORK", "AUTH_USER_MODEL", "XENTLY_DYNAMIC_CLASS_LOADER"]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "xauth.authentication.JWTTokenAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}

AUTH_USER_MODEL = "xauth.User"

XENTLY_DYNAMIC_CLASS_LOADER = "xently.core.loading.default_class_loader"

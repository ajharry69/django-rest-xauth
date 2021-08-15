REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "xauth.authentication.JWTAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}

AUTH_USER_MODEL = "accounts.User"

XENTLY_DYNAMIC_CLASS_LOADER = "xauth.loaders.class_loader"

XENTLY_DYNAMIC_CLASS_LOADER_MODULE_PREFIX = "xauth"

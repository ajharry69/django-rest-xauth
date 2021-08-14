__all__ = ["REST_FRAMEWORK", "XENTLY_DYNAMIC_CLASS_LOADER", "XENTLY_DYNAMIC_CLASS_LOADER_MODULE_PREFIX"]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "xauth.authentication.JWTTokenAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}

XENTLY_DYNAMIC_CLASS_LOADER = "xauth.loaders.class_loader"

XENTLY_DYNAMIC_CLASS_LOADER_MODULE_PREFIX = "xauth"

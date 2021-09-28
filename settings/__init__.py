from os import environ

from settings.base import *  # noqa

if environ.get("DJANGO_MODE", "production").lower() == "development1":
    from settings.development import *  # noqa
else:
    from settings.production import *  # noqa

try:
    from settings.local import *  # noqa
except ImportError:
    pass

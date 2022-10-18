from os import environ

from settings.base import *  # noqa

if environ.get("DJANGO_MODE", "development").lower() == "development":
    from settings.development import *  # noqa
else:
    from settings.production import *  # noqa

try:
    from settings.local import *  # noqa
except ImportError:
    pass

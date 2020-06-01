from django.conf import settings

try:
    XAUTH = settings.XAUTH
    DATE_INPUT_FORMAT = settings.DATE_INPUT_FORMATS[0]
except AttributeError:
    XAUTH = {}
except IndexError:
    DATE_INPUT_FORMAT = '%Y-%m-%d'

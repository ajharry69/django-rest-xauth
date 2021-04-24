import os

import django


def pytest_configure():
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"
    django.setup()

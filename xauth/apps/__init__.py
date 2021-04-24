from django import apps


class AppConfig(apps.AppConfig):
    name = 'xauth'

    def ready(self):
        from xauth.apps.account import signals

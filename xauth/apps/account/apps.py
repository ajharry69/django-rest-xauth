from django import apps


class AppConfig(apps.AppConfig):
    name = 'xauth.apps.account'

    def ready(self):
        pass

from django import apps


class AppConfig(apps.AppConfig):
    name = "xauth.apps.accounts"

    def ready(self):
        pass

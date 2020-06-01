from django.apps import AppConfig


class XauthConfig(AppConfig):
    name = 'xauth'

    # noinspection PyUnresolvedReferences
    def ready(self):
        from xauth import signals

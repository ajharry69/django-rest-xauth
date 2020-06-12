from django.db.models.signals import post_migrate

from xauth.models import default_security_question


def on_post_migrate(sender, **kwargs):
    default_security_question()


post_migrate.connect(on_post_migrate, dispatch_uid='1')

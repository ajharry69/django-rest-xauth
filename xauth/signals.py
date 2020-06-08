from django.db.models.signals import post_migrate

from xauth.models import SecurityQuestion


def on_post_migrate(sender, **kwargs):
    SecurityQuestion.objects.get_or_create(question='Default', usable=False, )


post_migrate.connect(on_post_migrate, dispatch_uid='1')

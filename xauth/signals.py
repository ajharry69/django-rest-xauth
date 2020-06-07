from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_migrate

from xauth.models import SecurityQuestion


def on_user_post_save(sender, instance, created, **kwargs):
    """
    Checks if `instance`(user) is marked as un-verified and send an email with verification code
    """
    user = instance
    if not user.is_verified:
        user.request_verification()


def on_post_migrate(sender, **kwargs):
    SecurityQuestion.objects.get_or_create(question='Default', usable=False, )


post_save.connect(on_user_post_save, sender=get_user_model(), dispatch_uid='1')
post_migrate.connect(on_post_migrate, dispatch_uid='2')

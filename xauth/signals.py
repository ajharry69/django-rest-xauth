from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models.signals import pre_save, post_save, post_migrate
from django.utils import timezone

from xauth.models import AccessLog, SecurityQuestion


def on_user_pre_save(sender, instance, **kwargs):
    """creates access & password reset log(s)"""
    try:
        user = get_user_model().objects.get(pk=instance.pk)
        last_login = user.last_login
        if last_login and last_login != instance.last_login:
            # the user probably just logged in
            AccessLog.objects.create(user=user, sign_in_time=timezone.now())

    except get_user_model().DoesNotExist:
        pass


def on_user_post_save(sender, instance, created, **kwargs):
    """
    Checks if `instance`(user) is marked as un-verified and send an email with verification code
    """
    user = instance
    if not user.is_verified:
        user.request_verification()


def on_post_migrate(sender, **kwargs):
    try:
        SecurityQuestion.objects.get_or_create(question='Default', usable=False, )
    except IntegrityError:
        pass


pre_save.connect(on_user_pre_save, sender=get_user_model(), dispatch_uid='1')
post_save.connect(on_user_post_save, sender=get_user_model(), dispatch_uid='2')
post_migrate.connect(on_post_migrate, dispatch_uid='3')

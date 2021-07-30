import factory
from django.apps import apps
from django.contrib.auth import get_user_model

from xauth.internal_settings import AUTH_APP_LABEL

__all__ = ["UserFactory"]


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = (model.USERNAME_FIELD,)

    email = factory.Sequence(lambda n: f"user{n + 1}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "xauth54321")


class SecurityQuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = apps.get_model(AUTH_APP_LABEL, "SecurityQuestion")
        django_get_or_create = ("question",)

    question = "What is your favorite color?"

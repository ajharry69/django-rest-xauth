import factory
from django.contrib.auth import get_user_model

__all__ = ["UserFactory"]


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = (model.USERNAME_FIELD,)

    email = factory.Sequence(lambda n: f"user{n + 1}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "xauth54321")

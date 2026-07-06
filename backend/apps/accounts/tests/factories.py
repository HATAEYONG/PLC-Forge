import factory

from apps.accounts.models import User

DEFAULT_PASSWORD = "test-password-1234!"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.django.Password(DEFAULT_PASSWORD)

import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def anon_client():
    return APIClient()

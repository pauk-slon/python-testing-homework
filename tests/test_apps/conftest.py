import pytest
from django.test.client import Client

from server.apps.identity.models import User


@pytest.fixture()
def user_client(user: User) -> Client:
    """A Django test client logged in as the current user."""
    client = Client()
    client.force_login(user)
    return client

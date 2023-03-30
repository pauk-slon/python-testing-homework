from typing import Callable

import pytest
from django.contrib import auth
from django.test.client import Client
from typing_extensions import TypeAlias

ClientAuthenticatedAssertion: TypeAlias = Callable[[Client], None]


@pytest.fixture(scope='session')
def assert_client_authenticated() -> ClientAuthenticatedAssertion:
    """Check if a Client is authenticated."""
    def factory(client: Client):
        user = auth.get_user(client)
        assert user.is_authenticated
    return factory


ClientNotAuthenticatedAssertion: TypeAlias = Callable[[Client], None]


@pytest.fixture(scope='session')
def assert_client_not_authenticated() -> ClientNotAuthenticatedAssertion:
    """Check if a Client is authenticated."""
    def factory(client: Client):
        user = auth.get_user(client)
        assert not user.is_authenticated
    return factory

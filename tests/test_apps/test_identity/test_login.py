from typing import TYPE_CHECKING, TypedDict

import pytest
from django.http import HttpResponse
from django.test.client import Client

from server.apps.identity.models import User

pytestmark = pytest.mark.django_db


if TYPE_CHECKING:
    from tests.plugins.django_auth import (
        ClientAuthenticatedAssertion,
        ClientNotAuthenticatedAssertion,
    )
    from tests.plugins.django_form_view import (
        FormNotValidAssertion,
        FormValidAssertion,
    )
    from tests.plugins.identity.user import UserFactory


class Credentials(TypedDict):
    """Credentials to use in the login form."""

    username: str
    password: str


@pytest.fixture()
def credentials(user: User, user_password: str) -> Credentials:
    """Credentials to use in the login form."""
    return {'username': user.email, 'password': user_password}


def test_valid_credentials_login(
    client: Client,
    credentials: Credentials,
    assert_form_valid: 'FormValidAssertion',
    assert_client_authenticated: 'ClientAuthenticatedAssertion',
):
    """Providing valid credentials should lead to a successful login."""
    response: HttpResponse = client.post(  # type: ignore[assignment]
        '/identity/login',
        data=credentials,
    )
    assert_form_valid(response, '/pictures/dashboard')
    assert_client_authenticated(client)


def test_inactive_user_login(
    client: Client,
    user_factory: 'UserFactory',
    user_password: str,
    assert_form_not_valid: 'FormNotValidAssertion',
    assert_client_not_authenticated: 'ClientNotAuthenticatedAssertion',
):
    """Providing credentials of an inactive should fail login."""
    user = user_factory(password=user_password, is_active=False)
    request_data = {'username': user.email, 'password': user_password}
    response: HttpResponse = client.post(  # type: ignore[assignment]
        '/identity/login',
        data=request_data,
    )
    assert_form_not_valid(response, '__all__')
    assert_client_not_authenticated(client)


@pytest.mark.parametrize(
    'invalid_fields',
    [['username'], ['password'], ['username', 'password']],
)
def test_invalid_credentials_login(
    client: Client,
    credentials: Credentials,
    invalid_fields: list[str],
    assert_form_not_valid: 'FormNotValidAssertion',
    assert_client_not_authenticated: 'ClientNotAuthenticatedAssertion',
):
    """Providing invalid credentials should fail login."""
    invalid_credentials = {
        invalid_field: '{0}-invalid'.format(credentials[invalid_field])
        for invalid_field in invalid_fields
    }
    response: HttpResponse = client.post(  # type: ignore[assignment]
        '/identity/login',
        data=credentials | invalid_credentials,
    )
    assert_form_not_valid(response, '__all__')
    assert_client_not_authenticated(client)

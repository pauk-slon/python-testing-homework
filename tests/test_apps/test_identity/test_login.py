from typing import TYPE_CHECKING

import pytest
from django.http import HttpResponse
from django.test.client import Client

from server.apps.identity.models import User

pytestmark = pytest.mark.django_db


if TYPE_CHECKING:
    from tests.plugins.django_form_view import (
        FormNotValidAssertion,
        FormValidAssertion,
    )
    from tests.plugins.identity.user import UserFactory


def test_valid_credentials_login(
    client: Client,
    user: User,
    user_password: str,
    assert_form_valid: 'FormValidAssertion',
):
    """Providing valid credentials should lead to a successful login."""
    request_data = {'username': user.email, 'password': user_password}
    response: HttpResponse = client.post(  # type: ignore[assignment]
        '/identity/login',
        data=request_data,
    )
    assert_form_valid(response, '/pictures/dashboard')


def test_inactive_user_login(
    client: Client,
    user_factory: 'UserFactory',
    user_password: str,
    assert_form_not_valid: 'FormNotValidAssertion',
):
    """Providing credentials of an inactive should fail login."""
    user = user_factory(password=user_password, is_active=False)
    request_data = {'username': user.email, 'password': user_password}
    response: HttpResponse = client.post(  # type: ignore[assignment]
        '/identity/login',
        data=request_data,
    )
    assert_form_not_valid(response, '__all__')


@pytest.mark.parametrize(
    'invalid_fields',
    [['username'], ['password'], ['username', 'password']],
)
def test_invalid_credentials_login(
    client: Client,
    user: User,
    user_password: str,
    invalid_fields: list[str],
    assert_form_not_valid: 'FormNotValidAssertion',
):
    """Providing invalid credentials should fail login."""
    request_data = {'username': user.email, 'password': user_password}
    for invalid_field in invalid_fields:
        request_data[invalid_field] = (
            '{0}-invalid'.format(request_data[invalid_field])
        )
    response: HttpResponse = client.post(  # type: ignore[assignment]
        '/identity/login',
        data=request_data,
    )
    assert_form_not_valid(response, '__all__')

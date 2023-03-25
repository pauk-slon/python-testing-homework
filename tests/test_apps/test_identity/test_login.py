from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.test.client import Client

from server.apps.identity.models import User

pytestmark = pytest.mark.django_db


if TYPE_CHECKING:
    from tests.plugins.identity.user import UserFactory


def test_valid_credentials_login(
    client: Client,
    user: User,
    user_password: str,
):
    """Providing valid username & password leads to successful login."""
    request_data = {'username': user.email, 'password': user_password}
    response = client.post('/identity/login', data=request_data)
    assert response.status_code == HTTPStatus.FOUND, (
        response.context['form'].errors
    )
    assert response['location'] == '/pictures/dashboard'


def test_inactive_user_login(
    client: Client,
    user_factory: UserFactory,
    user_password: str,
):
    """An inactive user should fail when loging in."""
    user = user_factory(password=user_password, is_active=False)
    request_data = {'username': user.email, 'password': user_password}
    response = client.post('/identity/login', data=request_data)
    assert response.status_code == HTTPStatus.OK
    assert response.context['form'].errors['__all__']

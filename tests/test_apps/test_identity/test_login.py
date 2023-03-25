from http import HTTPStatus

import pytest
from django.test.client import Client

from server.apps.identity.models import User

pytestmark = pytest.mark.django_db


def test_successful_login(client: Client, user: User, user_password: str):
    """Providing valid username & password leads to successful login."""
    request_data = {'username': user.email, 'password': user_password}
    response = client.post('/identity/login', data=request_data)
    assert response.status_code == HTTPStatus.FOUND, (
        response.context['form'].errors
    )
    assert response['location'] == '/pictures/dashboard'

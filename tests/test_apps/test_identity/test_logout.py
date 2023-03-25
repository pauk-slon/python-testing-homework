from http import HTTPStatus

import pytest
from django.test.client import Client

pytestmark = pytest.mark.django_db


def test_logout(user_client: Client):
    """Logout should be always successful."""
    response = user_client.post('/identity/logout')
    assert response.status_code == HTTPStatus.FOUND, (
        response.context['form'].errors
    )
    assert response['location'] == '/'
    assert not user_client.session.session_key

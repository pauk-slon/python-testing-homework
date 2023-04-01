from http import HTTPStatus

import pytest
from django.test.client import Client


@pytest.mark.django_db()
def test_pictures_index_view(user_client: Client):
    """Index page returns HTTP 200 OK."""
    response = user_client.get('')
    assert response.status_code == HTTPStatus.OK

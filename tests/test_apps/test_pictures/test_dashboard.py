from http import HTTPStatus
from typing import TYPE_CHECKING, Final

import pytest
from django.http import HttpResponse
from django.test.client import Client

from server.apps.identity.models import User

if TYPE_CHECKING:
    from tests.plugins.django_form_view import FormValidAssertion
    from tests.plugins.pictures.favourite_picture import FavouritePictureData


pytestmark = pytest.mark.django_db
JSON_SERVER_NUM_OF_PICTURES: Final[int] = 1


def test_create_favourite_picture_with_valid_data(
    user: User,
    user_client: Client,
    favourite_picture_data: 'FavouritePictureData',
    assert_form_valid: 'FormValidAssertion',
):
    """Providing valid data leads to creation of a `FavouritePicture`."""
    response: HttpResponse = user_client.post(  # type: ignore[assignment]
        '/pictures/dashboard',
        data=favourite_picture_data,
    )
    assert_form_valid(response, '/pictures/dashboard')
    assert user.pictures.filter(**favourite_picture_data).exists()


@pytest.mark.usefixtures('_placeholder_api_switch_to_json_server')
def test_dashboard_picture_list(user_client: Client):
    """Dashboard should contain picture list came from json-server."""
    response = user_client.get('/pictures/dashboard')
    assert response.status_code == HTTPStatus.OK
    assert len(response.context['pictures']) == JSON_SERVER_NUM_OF_PICTURES

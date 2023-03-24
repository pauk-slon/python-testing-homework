from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.test import Client

from server.apps.identity.models import User

if TYPE_CHECKING:
    from tests.plugins.identity.user import ProfileAssertion, ProfileData


pytestmark = pytest.mark.django_db


def test_valid_update(
    admin_client: Client,
    admin_user: User,
    user_profile_data: 'ProfileData',
    assert_user_profile_correct: 'ProfileAssertion',
) -> None:
    """Tests UserUpdateForm when valid data provided."""
    response = admin_client.post(
        '/identity/update',
        data=user_profile_data,
    )
    assert response.status_code == HTTPStatus.FOUND, (
        response.context['form'].errors
    )
    admin_user.refresh_from_db()
    assert_user_profile_correct(admin_user, user_profile_data)


@pytest.mark.parametrize('missing_field', User.REQUIRED_FIELDS)
def test_update_missing_required_field(
    admin_client: Client,
    admin_user: User,
    user_email: str,
    user_profile_data: 'ProfileData',
    missing_field: str,
) -> None:
    """Tests UserUpdateForm when invalid data provided."""
    request_data = user_profile_data | {missing_field: ''}
    response = admin_client.post('/identity/update', data=request_data)
    assert response.status_code == HTTPStatus.OK
    assert missing_field in response.context['form'].errors
    value_before = getattr(admin_user, missing_field)
    admin_user.refresh_from_db()
    assert getattr(admin_user, missing_field) == value_before

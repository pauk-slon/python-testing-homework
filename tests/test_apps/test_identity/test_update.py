from typing import TYPE_CHECKING

import pytest
from django.http import HttpResponse
from django.test import Client

from server.apps.identity.models import User

if TYPE_CHECKING:
    from tests.plugins.django_form_view import (
        FormNotValidAssertion,
        FormValidAssertion,
    )
    from tests.plugins.identity.user import ProfileAssertion, ProfileData


pytestmark = pytest.mark.django_db


def test_valid_update(
    user: User,
    user_client: Client,
    user_profile_data: 'ProfileData',
    assert_form_valid: 'FormValidAssertion',
    assert_user_profile_correct: 'ProfileAssertion',
) -> None:
    """Tests UserUpdateForm when valid data provided."""
    response: HttpResponse = user_client.post(  # type: ignore[assignment]
        '/identity/update',
        data=user_profile_data,
    )
    assert_form_valid(response, '/identity/update')
    user.refresh_from_db()
    assert_user_profile_correct(user, user_profile_data)


@pytest.mark.parametrize('missing_field', User.REQUIRED_FIELDS)
def test_update_missing_required_field(
    user: User,
    user_client: Client,
    user_profile_data: 'ProfileData',
    missing_field: str,
    assert_form_not_valid: 'FormNotValidAssertion',
) -> None:
    """Tests UserUpdateForm when invalid data provided."""
    request_data = user_profile_data | {missing_field: ''}
    response: HttpResponse = user_client.post(  # type: ignore[assignment]
        '/identity/update',
        data=request_data,
    )
    assert_form_not_valid(response, missing_field)
    value_before = getattr(user, missing_field)
    user.refresh_from_db()
    assert getattr(user, missing_field) == value_before

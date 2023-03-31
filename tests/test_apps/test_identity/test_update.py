from typing import TYPE_CHECKING, Callable

import pytest
from django.http import HttpResponse
from django.test import Client

from server.apps.identity.models import User

if TYPE_CHECKING:
    from tests.plugins.django_form_view import (
        FormNotValidAssertion,
        FormValidAssertion,
    )
    from tests.plugins.identity.user import RawUserDetails, UserDetailsAssertion


pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('_mock_lead_api_user_update')
def test_valid_update(  # noqa: WPS211
    user: User,
    user_client: Client,
    raw_user_details: 'RawUserDetails',
    assert_form_valid: 'FormValidAssertion',
    assert_user_details_correct: 'UserDetailsAssertion',
    assert_lead_api_user_updated: Callable[[User], None],
) -> None:
    """Providing valid data should successfully update user details."""
    response: HttpResponse = user_client.post(  # type: ignore[assignment]
        '/identity/update',
        data=raw_user_details,
    )
    assert_form_valid(response, '/identity/update')
    user.refresh_from_db()
    assert_user_details_correct(user, raw_user_details)
    assert_lead_api_user_updated(user)


@pytest.mark.parametrize('missing_field', User.REQUIRED_FIELDS)
def test_update_missing_required_field(
    user: User,
    user_client: Client,
    raw_user_details: 'RawUserDetails',
    missing_field: str,
    assert_form_not_valid: 'FormNotValidAssertion',
) -> None:
    """Missing any required field should fail editing user details."""
    request_data = raw_user_details | {missing_field: ''}
    response: HttpResponse = user_client.post(  # type: ignore[assignment]
        '/identity/update',
        data=request_data,
    )
    assert_form_not_valid(response, missing_field)
    value_before = getattr(user, missing_field)
    user.refresh_from_db()
    assert getattr(user, missing_field) == value_before

from typing import TYPE_CHECKING

import pytest
from django.contrib import auth
from django.http import HttpResponse
from django.test.client import Client

pytestmark = pytest.mark.django_db


if TYPE_CHECKING:
    from tests.plugins.django_auth import ClientNotAuthenticatedAssertion
    from tests.plugins.django_form_view import FormValidAssertion


def test_logout(
    user_client: Client,
    assert_form_valid: 'FormValidAssertion',
    assert_client_not_authenticated: 'ClientNotAuthenticatedAssertion',
):
    """Logout should be always successful."""
    response: HttpResponse = (
        user_client.post('/identity/logout')  # type: ignore[assignment]
    )
    assert_form_valid(response, '/')
    user = auth.get_user(user_client)
    assert not user.is_authenticated

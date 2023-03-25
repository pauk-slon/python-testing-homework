from typing import TYPE_CHECKING

import pytest
from django.http import HttpResponse
from django.test.client import Client

pytestmark = pytest.mark.django_db


if TYPE_CHECKING:
    from tests.plugins.django_form_view import FormValidAssertion


def test_logout(user_client: Client, assert_form_valid: 'FormValidAssertion'):
    """Logout should be always successful."""
    response: HttpResponse = (
        user_client.post('/identity/logout')  # type: ignore[assignment]
    )
    assert_form_valid(response, '/')
    assert not user_client.session.session_key

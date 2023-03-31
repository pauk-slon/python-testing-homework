import json
from typing import Callable, TypedDict
from urllib.parse import urljoin

import httpretty
import pytest
from django.conf import settings
from mimesis import Field, Schema

from server.apps.identity.models import User


class LeadAPIUserResponse(TypedDict):
    """Lead API User response."""

    id: int


@pytest.fixture()
def lead_api_user_response(faker_seed: int) -> LeadAPIUserResponse:
    """Create fake lead API response for users."""
    mf = Field(seed=faker_seed)
    schema = Schema(schema=lambda: {
        'id': mf('numeric.increment'),
    })
    return schema.create(iterations=1)[0]  # type: ignore[return-value]


@pytest.fixture()
def _httpretty_enable():
    with httpretty.enabled(allow_net_connect=False):
        yield


@pytest.fixture()
def lead_api_create_user_mock(
    _httpretty_enable,
    lead_api_user_response: LeadAPIUserResponse,
) -> LeadAPIUserResponse:
    """Mock POST /users method."""
    httpretty.register_uri(
        method=httpretty.POST,
        body=json.dumps(lead_api_user_response),
        uri=urljoin(
            settings.PLACEHOLDER_API_URL,  # type: ignore[misc]
            '/users',
        ),
    )
    return lead_api_user_response


LeadDetailsAssertion = Callable[[User, LeadAPIUserResponse], None]


@pytest.fixture(scope='session')
def assert_lead_details_correct() -> LeadDetailsAssertion:
    """Assert Lead API User response corresponds to User instance."""
    def factory(user: User, lead_api_user_response: LeadAPIUserResponse):
        assert user.lead_id == lead_api_user_response['id']
    return factory

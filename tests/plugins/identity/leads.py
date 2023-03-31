import json
import re
from http import HTTPStatus
from typing import Callable, Final, Iterator, Pattern, TypedDict
from urllib.parse import urljoin

import httpretty
import pytest
from django.conf import settings
from mimesis import Field, Schema

from server.apps.identity.models import User

USER_LIST_URL: Final[str] = urljoin(
    settings.PLACEHOLDER_API_URL,  # type: ignore[misc]
    '/users',
)
USER_DETAILS_URL: Pattern[str] = re.compile(
    r'{root_url}/(?P<lead_id>\d+)'.format(root_url=USER_LIST_URL),
)


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
def _enable_httpretty():
    with httpretty.enabled(allow_net_connect=False):
        yield


@pytest.fixture()
def lead_api_create_user_mock(
    _enable_httpretty,
    lead_api_user_response: LeadAPIUserResponse,
) -> Iterator[LeadAPIUserResponse]:
    """Mock POST /users method."""
    httpretty.register_uri(
        method=httpretty.POST,
        body=json.dumps(lead_api_user_response),
        uri=USER_LIST_URL,
    )
    yield lead_api_user_response
    assert httpretty.has_request()


LeadDetailsAssertion = Callable[[User, LeadAPIUserResponse], None]


@pytest.fixture(scope='session')
def assert_lead_details_correct() -> LeadDetailsAssertion:
    """Assert Lead API User response corresponds to User instance."""
    def factory(user: User, lead_api_user_response: LeadAPIUserResponse):
        assert user.lead_id == lead_api_user_response['id']
    return factory


def _lead_api_update_user_request_callback(request, uri, response_headers):
    url_match = USER_DETAILS_URL.match(uri)
    assert url_match
    lead_id = url_match.group('lead_id')
    return [HTTPStatus.OK, response_headers, json.dumps({'lead_id': lead_id})]


@pytest.fixture()
def _mock_lead_api_user_update(_enable_httpretty) -> None:
    """Mock PATCH /users/{lead_id} method."""
    httpretty.register_uri(
        method=httpretty.PATCH,
        uri=USER_DETAILS_URL,
        body=_lead_api_update_user_request_callback,
    )


@pytest.fixture()
def assert_lead_api_user_updated() -> Callable[[User], None]:
    """Assert a request to update the given user has been made."""
    def factory(user: User):
        expected_url = '{root_url}/{lead_id}'.format(
            root_url=USER_LIST_URL,
            lead_id=user.lead_id,
        )
        calls_to_lead_api = {
            (request.url, request.method)
            for request in httpretty.latest_requests()
        }
        assert (expected_url, httpretty.PATCH) in calls_to_lead_api

    return factory

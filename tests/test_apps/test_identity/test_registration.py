from http import HTTPStatus
from typing import TYPE_CHECKING

from django.test import Client
import pytest

from server.apps.identity.models import User


pytestmark = pytest.mark.django_db


if TYPE_CHECKING:
    from tests.plugins.identity.user import ProfileAssertion, ProfileData


@pytest.fixture
def registration_data(
    user_email: str,
    user_password: str,
    user_profile_data: 'ProfileData',
):
    return user_profile_data | {
        'email': user_email,
        'password1': user_password,
        'password2': user_password,
    }


def test_valid_registration(
    client: Client,
    user_email: str,
    user_password: str,
    registration_data,
    assert_user_profile: 'ProfileAssertion',
) -> None:
    response = client.post('/identity/registration', data=registration_data)
    assert response.status_code == HTTPStatus.FOUND, (
        response.context['form'].errors
    )
    user = User.objects.all().get(email=user_email)
    assert user.check_password(user_password)
    assert_user_profile(user, registration_data)


@pytest.mark.parametrize(
    'missing_field',
    User.REQUIRED_FIELDS + [User.USERNAME_FIELD],
)
def test_registration_missing_required_field(
    client: Client,
    user_email: str,
    registration_data,
    missing_field: str,
) -> None:
    response = client.post(
        '/identity/registration',
        data=registration_data | {missing_field: ''},
    )
    assert response.status_code == HTTPStatus.OK
    assert missing_field in response.context['form'].errors
    assert not User.objects.filter(email=user_email).exists()

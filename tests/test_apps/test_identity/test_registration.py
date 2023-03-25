from typing import TYPE_CHECKING

import pytest
from django.test import Client

from server.apps.identity.models import User

pytestmark = pytest.mark.django_db


if TYPE_CHECKING:
    from tests.plugins.django_form_view import (
        FormNotValidAssertion,
        FormValidAssertion,
    )
    from tests.plugins.identity.user import ProfileAssertion, ProfileData


@pytest.fixture()
def registration_data(
    user_email: str,
    user_password: str,
    user_profile_data: 'ProfileData',
):
    """Raw data for RegistrationForm."""
    return user_profile_data | {
        'email': user_email,
        'password1': user_password,
        'password2': user_password,
    }


def test_valid_registration(
    client: Client,
    registration_data,
    assert_form_valid: 'FormValidAssertion',
    assert_user_profile_correct: 'ProfileAssertion',
) -> None:
    """Providing valid registration data leads to successful registration."""
    response = client.post('/identity/registration', data=registration_data)
    assert_form_valid(response, '/identity/login')
    user = User.objects.get(email=registration_data['email'])
    assert user.check_password(registration_data['password1'])
    assert_user_profile_correct(user, registration_data)


@pytest.mark.parametrize(
    'missing_field',
    User.REQUIRED_FIELDS + [User.USERNAME_FIELD],
)
def test_registration_missing_required_field(
    client: Client,
    registration_data,
    missing_field: str,
    assert_form_not_valid: 'FormNotValidAssertion',
) -> None:
    """Missing any required field should fail registration process."""
    request_data = registration_data | {missing_field: ''}
    response = client.post('/identity/registration', data=request_data)
    assert_form_not_valid(response, missing_field)
    assert not User.objects.exists()


@pytest.mark.parametrize(('invalid_field', 'invalid_value'), [
    ('email', 'invalid@email'),
    ('date_of_birth', '2000-02-30'),
])
def test_registration_invalid_field(
    client: Client,
    registration_data,
    invalid_field: str,
    invalid_value: str,
    assert_form_not_valid: 'FormNotValidAssertion',
) -> None:
    """Invalid field value should fail registration process."""
    request_data = registration_data | {invalid_field: invalid_value}
    response = client.post('/identity/registration', data=request_data)
    assert_form_not_valid(response, invalid_field)
    assert not User.objects.exists()

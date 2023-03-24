import datetime
from typing import Callable, Protocol, TypedDict, final

import pytest
from mimesis.schema import Field, Schema
from typing_extensions import Unpack

from server.apps.identity.models import User

USER_BIRTHDAY_FORMAT = '%Y-%m-%d'  # noqa: WPS323


@final
class ProfileData(TypedDict, total=False):
    """Raw user profile data."""

    first_name: str
    last_name: str
    date_of_birth: str
    address: str
    job_title: str
    phone: str


@final
class ProfileDataFactory(Protocol):
    """A factory to generate `ProfileData`."""

    def __call__(self, **fields: Unpack[ProfileData]) -> ProfileData:
        """Profile data factory protocol."""


@pytest.fixture()
def mf() -> Field:
    """Returns the current mimesis `Field`."""
    return Field()


@pytest.fixture()
def user_profile_data_factory(mf) -> ProfileDataFactory:
    """Returns a factory to generate `ProfileData`."""
    schema = Schema(
        schema=lambda: {
            'first_name': mf('person.first_name'),
            'last_name': mf('person.last_name'),
            'date_of_birth': mf(
                'datetime.formatted_date',
                fmt=USER_BIRTHDAY_FORMAT,
                end=datetime.date.today().year - 1,
            ),
            'address': mf('address.address'),
            'job_title': mf('person.occupation'),
            'phone': mf('person.telephone'),
        },
    )
    return lambda **fields: next(schema.iterator(1)) | fields


@pytest.fixture()
def user_profile_data(
    user_profile_data_factory: ProfileDataFactory,
) -> ProfileData:
    """Generates a new `ProfileData`."""
    return user_profile_data_factory()


ProfileAssertion = Callable[[User, ProfileData], None]


def _assert_user_profile_correct(user: User, profile_data: ProfileData):
    assert user.first_name == profile_data['first_name']
    assert user.last_name == profile_data['last_name']
    if user.date_of_birth:
        formatted_date_of_birth = user.date_of_birth.strftime(
            USER_BIRTHDAY_FORMAT,
        )
        assert formatted_date_of_birth == profile_data['date_of_birth']
    else:
        assert not profile_data['date_of_birth']
    assert user.address == profile_data['address']
    assert user.job_title == profile_data['job_title']
    assert user.phone == profile_data['phone']


@pytest.fixture()
def assert_user_profile_correct() -> ProfileAssertion:
    """Checks `ProfileData` corresponds to the given `User` instance."""
    return _assert_user_profile_correct


@pytest.fixture()
def user_email(mf) -> str:
    """Generates a new email."""
    return mf('person.email', unique=True)


@pytest.fixture()
def user_password(mf) -> str:
    """Generates a password."""
    return mf('person.password')

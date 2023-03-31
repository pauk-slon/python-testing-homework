import datetime
from typing import Callable, Protocol, TypedDict, final

import pytest
from django_fakery.faker_factory import Factory
from mimesis.schema import Field, Schema
from typing_extensions import Unpack

from server.apps.identity.models import User

USER_BIRTHDAY_FORMAT = '%Y-%m-%d'  # noqa: WPS323


@final
class RawUserDetails(TypedDict, total=False):
    """Raw user details."""

    first_name: str
    last_name: str
    date_of_birth: str
    address: str
    job_title: str
    phone: str


@final
class RawUserDetailsFactory(Protocol):  # type: ignore[misc]
    """A factory to generate `RawUserDetails`."""

    def __call__(self, **fields: Unpack[RawUserDetails]) -> RawUserDetails:
        """Profile data factory protocol."""


@pytest.fixture(scope='session')
def mf(faker_seed: int) -> Field:
    """Returns the current mimesis `Field`."""
    return Field(seed=faker_seed)


@pytest.fixture()
def raw_user_details_factory(mf) -> RawUserDetailsFactory:
    """Returns a factory to generate a `RawUserDetails` dictionary."""
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
def raw_user_details(
    raw_user_details_factory,
) -> RawUserDetails:
    """Generates a new `RawUserDetails` dictionary."""
    return raw_user_details_factory()


UserDetailsAssertion = Callable[[User, RawUserDetails], None]


@pytest.fixture(scope='session')
def assert_user_details_correct() -> UserDetailsAssertion:
    """Checks if `RawUserDetails` corresponds to `User`."""
    def factory(user: User, raw_user_details: RawUserDetails):
        assert user.first_name == raw_user_details['first_name']
        assert user.last_name == raw_user_details['last_name']
        if user.date_of_birth:
            formatted_date_of_birth = user.date_of_birth.strftime(
                USER_BIRTHDAY_FORMAT,
            )
            assert formatted_date_of_birth == raw_user_details['date_of_birth']
        else:
            assert not raw_user_details['date_of_birth']
        assert user.address == raw_user_details['address']
        assert user.job_title == raw_user_details['job_title']
        assert user.phone == raw_user_details['phone']
    return factory


@pytest.fixture()
def user_email(mf) -> str:
    """Email of the current user."""
    return mf('person.email')


@pytest.fixture()
def default_password(mf) -> str:
    """Default password for user factory."""
    return mf('person.password')


@pytest.fixture()
def user_password(default_password) -> str:
    """Password of the current user."""
    return default_password


@final
class UserFactory(Protocol):  # type: ignore[misc]
    """A factory to generate a `User` instance."""

    def __call__(self, **fields) -> User:
        """Profile data factory protocol."""


@pytest.fixture()
def user_factory(
    fakery: Factory[User],
    faker_seed: int,
    default_password: str,
) -> UserFactory:
    """Creates a factory to generate a user instance."""
    def factory(**fields):
        password = fields.pop('password', default_password)
        return fakery.make(  # type: ignore[call-overload]
            model=User,
            fields=fields,
            seed=faker_seed,
            pre_save=[lambda _user: _user.set_password(password)],
        )
    return factory


@pytest.fixture()
def user(
    user_factory: UserFactory,
    user_email: str,
    user_password: str,
    mf: Field,
) -> User:
    """The current user.

    The fixtures `user_email` and `user_password` are used
    as email and password of the user correspondingly.
    """
    return user_factory(
        email=user_email,
        password=user_password,
        lead_id=mf('numeric.increment'),
        is_active=True,
    )

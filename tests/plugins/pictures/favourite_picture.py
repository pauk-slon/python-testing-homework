from typing import Protocol, TypedDict, final

import pytest
from mimesis.schema import Field, Schema
from typing_extensions import Unpack


class FavouritePictureData(TypedDict, total=False):
    """Data to create a `FavouritePicture`."""

    foreign_id: int
    url: str


@final
class FavouritePictureDataFactory(Protocol):  # type: ignore[misc]
    """A factory to generate `FavouritePictureData`."""

    def __call__(
        self,
        **fields: Unpack[FavouritePictureData],
    ) -> FavouritePictureData:
        """`FavouritePictureData` factory protocol."""


@pytest.fixture()
def mf(faker_seed: int) -> Field:
    """Returns the current mimesis `Field`."""
    return Field(seed=faker_seed)


@pytest.fixture()
def favourite_picture_data_factory(mf: Field):
    """Returns a factory to generate a `FavouritePictureData` dictionary."""
    schema = Schema(
        schema=lambda: {
            'foreign_id': mf('numeric.increment'),
            'url': mf('internet.url'),
        },
    )
    return lambda **fields: next(schema.iterator(1)) | fields


@pytest.fixture()
def favourite_picture_data(
    favourite_picture_data_factory: FavouritePictureDataFactory,
) -> FavouritePictureData:
    """Generates a `FavouritePictureData`."""
    return favourite_picture_data_factory()

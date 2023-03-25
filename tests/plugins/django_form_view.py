from http import HTTPStatus
from typing import Protocol, Union

import pytest
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

FormViewResponse = Union[TemplateResponse, HttpResponseRedirect]


class FormValidAssertion(Protocol):  # type: ignore[misc]
    """Check if a FormView processed the form successfully."""

    def __call__(self, response: FormViewResponse, redirect_url: str) -> None:
        """`FormValidAssertion` protocol."""


@pytest.fixture()
def assert_form_valid() -> FormValidAssertion:
    """Check if a FormView processed the form successfully."""
    def factory(response: FormViewResponse, redirect_url: str):
        assert response.status_code == HTTPStatus.FOUND, (
            response.context['form'].errors
        )
        assert response['location'] == redirect_url
    return factory

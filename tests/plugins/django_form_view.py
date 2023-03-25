from http import HTTPStatus
from typing import Protocol, Union

import pytest
from django import forms
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

FormViewResponse = Union[TemplateResponse, HttpResponseRedirect]


def _get_errors(response: FormViewResponse):
    assert isinstance(response, TemplateResponse)
    assert response.context_data
    form: forms.Form = response.context_data['form']
    return form.errors


class FormValidAssertion(Protocol):
    """Check if a FormView processed the form successfully."""

    def __call__(self, response: FormViewResponse, redirect_url: str) -> None:
        """`FormValidAssertion` protocol."""


@pytest.fixture()
def assert_form_valid() -> FormValidAssertion:
    """Check if a FormView processed the form successfully."""
    def factory(response: FormViewResponse, redirect_url: str):
        assert response.status_code == HTTPStatus.FOUND, _get_errors(response)
        assert response['location'] == redirect_url
    return factory


class FormNotValidAssertion(Protocol):
    """Check if a FormView processed the form with errors."""

    def __call__(self, response: FormViewResponse, invalid_field: str) -> None:
        """`FormNotValidAssertion` protocol."""


@pytest.fixture()
def assert_form_not_valid() -> FormNotValidAssertion:
    """Check if a FormView processed the form with errors."""
    def factory(response: FormViewResponse, invalid_field: str):
        assert response.status_code == HTTPStatus.OK
        assert invalid_field in _get_errors(response)
    return factory

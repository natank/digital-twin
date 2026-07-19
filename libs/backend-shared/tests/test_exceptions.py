"""Tests for the application exception hierarchy."""

import pytest

from backend_shared.exceptions import (
    AppError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)


def test_base_error_carries_message_code_and_status():
    err = AppError("something broke")
    assert err.message == "something broke"
    assert err.error_code == "INTERNAL_001"
    assert err.status_code == 500
    assert err.details == {}


def test_error_code_can_be_overridden_per_instance():
    err = AuthenticationError("token expired", error_code="AUTH_002")
    assert err.error_code == "AUTH_002"
    # Class default is unchanged for other instances.
    assert AuthenticationError("bad creds").error_code == "AUTH_001"


def test_details_are_preserved():
    err = ValidationError("bad input", details={"field": "email"})
    assert err.details == {"field": "email"}


@pytest.mark.parametrize(
    ("exc_class", "expected_status"),
    [
        (ValidationError, 422),
        (AuthenticationError, 401),
        (NotFoundError, 404),
        (ConflictError, 409),
    ],
)
def test_status_codes(exc_class: type[AppError], expected_status: int):
    assert exc_class("x").status_code == expected_status


def test_exceptions_are_catchable_as_app_error():
    with pytest.raises(AppError):
        raise NotFoundError("missing")

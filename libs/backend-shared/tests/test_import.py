"""Smoke tests verifying the package's public API is importable."""

import backend_shared


def test_package_importable():
    assert backend_shared is not None


def test_public_api_is_exported():
    """Everything in __all__ must actually be importable from the package."""
    missing = [name for name in backend_shared.__all__ if not hasattr(backend_shared, name)]
    assert missing == [], f"__all__ names not exported: {missing}"


def test_key_symbols_available():
    from backend_shared import ApiResponse, AppError, configure_logging, encrypt_field

    assert all(
        callable(obj) for obj in (ApiResponse.ok, AppError, configure_logging, encrypt_field)
    )

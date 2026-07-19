"""Smoke test verifying the package is importable."""

import src


def test_package_importable():
    """The backend-shared package should import without error."""
    assert src is not None

"""Shared FastAPI dependencies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend_shared.exceptions import AuthenticationError
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.db.session import get_db

if TYPE_CHECKING:
    from src.db.models import Owner

# Re-export so routers import dependencies from one place.
__all__ = ["get_db", "get_current_owner"]

_bearer = HTTPBearer(auto_error=False)


def get_current_owner(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> "Owner":
    """Resolve the authenticated owner from a Bearer token.

    PR-001 ships a stub that always rejects (no DB required). PR-002 replaces
    this implementation with JWT + session validation and will add a ``db``
    dependency while keeping the public name stable for route signatures.
    """
    _ = credentials  # present so OpenAPI shows the Bearer scheme
    raise AuthenticationError(
        "Authentication is not configured yet",
        error_code="AUTH_001",
    )

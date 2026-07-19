"""Shared FastAPI dependencies."""

from __future__ import annotations

from backend_shared.exceptions import AuthenticationError
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.db.models import Owner
from src.db.session import get_db

# Re-export so routers import dependencies from one place.
__all__ = ["get_db", "get_current_owner"]

_bearer = HTTPBearer(auto_error=False)


def get_current_owner(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Owner:
    """Resolve the authenticated owner from a Bearer JWT + DB session row."""
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Not authenticated")

    from src.auth.service import get_owner_for_token

    return get_owner_for_token(db, credentials.credentials)

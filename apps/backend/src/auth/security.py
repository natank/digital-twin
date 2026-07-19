"""Password hashing and JWT helpers."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from src.settings import Settings, get_settings


def hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Return True if password matches the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def hash_token(raw: str) -> str:
    """One-way hash for storing session tokens (never store raw JWTs)."""
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def create_access_token(
    *,
    owner_id: uuid.UUID,
    session_id: uuid.UUID,
    settings: Settings | None = None,
    expires_delta: timedelta | None = None,
) -> tuple[str, datetime]:
    """Create a signed JWT access token.

    Returns:
        (token, expires_at_utc)
    """
    cfg = settings or get_settings()
    now = datetime.now(timezone.utc)
    expires_at = now + (expires_delta or timedelta(seconds=cfg.jwt_expiry))
    payload: dict[str, Any] = {
        "sub": str(owner_id),
        "sid": str(session_id),
        "jti": str(uuid.uuid4()),  # unique per issuance so refreshes differ
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "type": "access",
    }
    token = jwt.encode(payload, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)
    # PyJWT may return bytes on older versions; normalize to str.
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token, expires_at


def decode_access_token(token: str, settings: Settings | None = None) -> dict[str, Any]:
    """Decode and validate a JWT access token.

    Raises:
        jwt.PyJWTError: on invalid/expired tokens.
    """
    cfg = settings or get_settings()
    return jwt.decode(token, cfg.jwt_secret, algorithms=[cfg.jwt_algorithm])

"""Auth domain services: registration, login, session creation."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from backend_shared.exceptions import AuthenticationError, ConflictError, ValidationError
from backend_shared.utils import validate_email, validate_password_strength
from sqlalchemy.orm import Session

from src.auth.security import (
    create_access_token,
    hash_password,
    hash_token,
    verify_password,
)
from src.db.models import Owner, OwnerSession, Profile
from src.settings import Settings, get_settings


def register_owner(
    db: Session,
    *,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
) -> Owner:
    """Create a new owner + empty profile."""
    normalized = email.strip().lower()
    if not validate_email(normalized):
        raise ValidationError("Invalid email address", details={"field": "email"})

    problems = validate_password_strength(password)
    if problems:
        raise ValidationError(
            "Password does not meet security requirements",
            details={"problems": problems},
        )

    existing = db.query(Owner).filter(Owner.email == normalized).first()
    if existing is not None:
        raise ConflictError("An account with this email already exists")

    owner = Owner(
        email=normalized,
        password_hash=hash_password(password),
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        is_active=True,
        email_verified=False,
    )
    owner.profile = Profile()
    db.add(owner)
    db.commit()
    db.refresh(owner)
    return owner


def authenticate_owner(
    db: Session,
    *,
    email: str,
    password: str,
    settings: Settings | None = None,
) -> Owner:
    """Validate credentials and return the owner.

    Always uses a generic error message to avoid user enumeration.
    """
    cfg = settings or get_settings()
    normalized = email.strip().lower()
    owner = db.query(Owner).filter(Owner.email == normalized).first()
    if owner is None or not verify_password(password, owner.password_hash):
        raise AuthenticationError("Invalid email or password")

    if not owner.is_active:
        raise AuthenticationError("Account is inactive")

    if not owner.email_verified and not cfg.auth_allow_unverified_login:
        raise AuthenticationError(
            "Email address has not been verified",
            error_code="AUTH_002",
        )
    return owner


def create_owner_session(
    db: Session,
    owner: Owner,
    *,
    settings: Settings | None = None,
) -> tuple[str, datetime, OwnerSession]:
    """Persist a session row and return (access_token, expires_at, session)."""
    cfg = settings or get_settings()
    session_id = uuid.uuid4()
    token, expires_at = create_access_token(
        owner_id=owner.id,
        session_id=session_id,
        settings=cfg,
    )
    # Store hash of the access token so we can revoke without keeping the JWT.
    row = OwnerSession(
        id=session_id,
        owner_id=owner.id,
        token=hash_token(token),
        expires_at=expires_at.replace(tzinfo=None) if expires_at.tzinfo else expires_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return token, expires_at, row


def get_owner_for_token(
    db: Session,
    token: str,
    *,
    settings: Settings | None = None,
) -> Owner:
    """Resolve a Bearer token to an active owner with a valid session."""
    from src.auth.security import decode_access_token
    import jwt

    cfg = settings or get_settings()
    try:
        payload = decode_access_token(token, settings=cfg)
    except jwt.PyJWTError as exc:
        raise AuthenticationError("Invalid or expired token") from exc

    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type")

    try:
        owner_id = uuid.UUID(str(payload["sub"]))
        session_id = uuid.UUID(str(payload["sid"]))
    except (KeyError, ValueError) as exc:
        raise AuthenticationError("Invalid token claims") from exc

    session = (
        db.query(OwnerSession)
        .filter(OwnerSession.id == session_id, OwnerSession.owner_id == owner_id)
        .first()
    )
    if session is None:
        raise AuthenticationError("Session not found or revoked")

    # Compare token hash (rotation/invalidation support).
    if session.token != hash_token(token):
        raise AuthenticationError("Session token mismatch")

    expires = session.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        raise AuthenticationError("Session expired")

    owner = db.query(Owner).filter(Owner.id == owner_id).first()
    if owner is None or not owner.is_active:
        raise AuthenticationError("Account is inactive or missing")
    return owner

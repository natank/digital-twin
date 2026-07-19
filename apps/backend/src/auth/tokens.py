"""One-time owner tokens (email verification, password reset)."""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from backend_shared.exceptions import AuthenticationError, ValidationError
from sqlalchemy.orm import Session

from src.auth.security import hash_password, hash_token, verify_password
from src.db.models import Owner, OwnerSession, OwnerToken
from src.email.sender import EmailSender, get_email_sender
from src.settings import Settings, get_settings

TOKEN_EMAIL_VERIFY = "email_verify"
TOKEN_PASSWORD_RESET = "password_reset"

VERIFY_TTL = timedelta(hours=24)
RESET_TTL = timedelta(hours=1)


def _utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def issue_token(
    db: Session,
    owner: Owner,
    *,
    token_type: str,
    ttl: timedelta,
) -> str:
    """Create a one-time token row and return the raw token (shown once)."""
    raw = secrets.token_urlsafe(32)
    row = OwnerToken(
        id=uuid.uuid4(),
        owner_id=owner.id,
        token_type=token_type,
        token_hash=hash_token(raw),
        expires_at=_utcnow_naive() + ttl,
    )
    db.add(row)
    db.commit()
    return raw


def _consume_token(
    db: Session,
    raw_token: str,
    *,
    token_type: str,
) -> OwnerToken:
    token_hash = hash_token(raw_token)
    row = (
        db.query(OwnerToken)
        .filter(
            OwnerToken.token_hash == token_hash,
            OwnerToken.token_type == token_type,
        )
        .first()
    )
    if row is None or row.used_at is not None:
        raise ValidationError("Invalid or already used token")
    if row.expires_at < _utcnow_naive():
        raise ValidationError("Token has expired")
    row.used_at = _utcnow_naive()
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def send_verification_email(
    db: Session,
    owner: Owner,
    *,
    email_sender: EmailSender | None = None,
    settings: Settings | None = None,
) -> None:
    """Issue a verification token and send it via the email backend."""
    cfg = settings or get_settings()
    sender = email_sender or get_email_sender()
    raw = issue_token(db, owner, token_type=TOKEN_EMAIL_VERIFY, ttl=VERIFY_TTL)
    sender.send(
        to=owner.email,
        subject="Verify your Digital Twin account",
        body=(
            f"Hello {owner.first_name},\n\n"
            f"Verify your email by calling POST /auth/verify-email with token:\n\n"
            f"  {raw}\n\n"
            f"This token expires in 24 hours.\n"
            f"From: {cfg.email_from}\n"
        ),
    )


def verify_email(db: Session, raw_token: str) -> Owner:
    """Mark the owner email as verified using a one-time token."""
    row = _consume_token(db, raw_token, token_type=TOKEN_EMAIL_VERIFY)
    owner = db.query(Owner).filter(Owner.id == row.owner_id).first()
    if owner is None:
        raise ValidationError("Owner not found for token")
    owner.email_verified = True
    db.add(owner)
    db.commit()
    db.refresh(owner)
    return owner


def request_password_reset(
    db: Session,
    email: str,
    *,
    email_sender: EmailSender | None = None,
    settings: Settings | None = None,
) -> None:
    """Always succeeds from the caller's perspective (no user enumeration)."""
    cfg = settings or get_settings()
    sender = email_sender or get_email_sender()
    owner = db.query(Owner).filter(Owner.email == email.strip().lower()).first()
    if owner is None:
        return
    raw = issue_token(db, owner, token_type=TOKEN_PASSWORD_RESET, ttl=RESET_TTL)
    sender.send(
        to=owner.email,
        subject="Reset your Digital Twin password",
        body=(
            f"Hello {owner.first_name},\n\n"
            f"Reset your password via POST /auth/reset-password with token:\n\n"
            f"  {raw}\n\n"
            f"This token expires in 1 hour.\n"
            f"From: {cfg.email_from}\n"
        ),
    )


def reset_password(db: Session, *, raw_token: str, new_password: str) -> Owner:
    """Reset password, invalidate sessions, mark token used."""
    from backend_shared.utils import validate_password_strength

    problems = validate_password_strength(new_password)
    if problems:
        raise ValidationError(
            "Password does not meet security requirements",
            details={"problems": problems},
        )

    row = _consume_token(db, raw_token, token_type=TOKEN_PASSWORD_RESET)
    owner = db.query(Owner).filter(Owner.id == row.owner_id).first()
    if owner is None:
        raise ValidationError("Owner not found for token")

    # Avoid no-op "change" to the same password if we can detect it.
    if verify_password(new_password, owner.password_hash):
        raise ValidationError("New password must be different from the current password")

    owner.password_hash = hash_password(new_password)
    db.add(owner)
    # Invalidate all sessions for this owner.
    db.query(OwnerSession).filter(OwnerSession.owner_id == owner.id).delete()
    db.commit()
    db.refresh(owner)
    return owner


def require_active_session_owner(
    db: Session,
    token: str,
) -> Owner:
    """Helper for routes that need the current owner (re-export style)."""
    from src.auth.service import get_owner_for_token

    try:
        return get_owner_for_token(db, token)
    except AuthenticationError:
        raise

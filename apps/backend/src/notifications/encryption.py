"""Fernet helpers for encrypting Pushover user keys at rest."""

from __future__ import annotations

import base64
import hashlib

from backend_shared.exceptions import ValidationError
from cryptography.fernet import Fernet, InvalidToken

from src.settings import Settings, get_settings

# Stable dev-only material when ENCRYPTION_KEY is empty (never for production).
_DEV_FALLBACK_MATERIAL = b"digital-twin-dev-only-encryption-key-v1"


def _fernet_from_settings(settings: Settings | None = None) -> Fernet:
    cfg = settings or get_settings()
    raw = (cfg.encryption_key or "").strip()
    if raw:
        # Accept raw Fernet key (url-safe base64 32-byte) or arbitrary secret.
        try:
            return Fernet(raw.encode("utf-8") if isinstance(raw, str) else raw)
        except (ValueError, TypeError):
            digest = hashlib.sha256(raw.encode("utf-8")).digest()
            return Fernet(base64.urlsafe_b64encode(digest))
    if cfg.debug:
        digest = hashlib.sha256(_DEV_FALLBACK_MATERIAL).digest()
        return Fernet(base64.urlsafe_b64encode(digest))
    raise ValidationError(
        "ENCRYPTION_KEY is required to store Pushover credentials",
        details={"field": "encryption_key"},
    )


def encrypt_secret(plaintext: str, *, settings: Settings | None = None) -> str:
    """Encrypt a secret string; returns Fernet token as str."""
    if not plaintext:
        raise ValidationError("Cannot encrypt empty secret")
    token = _fernet_from_settings(settings).encrypt(plaintext.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_secret(ciphertext: str, *, settings: Settings | None = None) -> str:
    """Decrypt a Fernet token string."""
    if not ciphertext:
        raise ValidationError("Cannot decrypt empty ciphertext")
    try:
        raw = _fernet_from_settings(settings).decrypt(ciphertext.encode("utf-8"))
    except InvalidToken as exc:
        raise ValidationError("Failed to decrypt stored secret") from exc
    return raw.decode("utf-8")


def mask_user_key(user_key: str) -> str:
    """Return a masked representation safe for API responses."""
    key = (user_key or "").strip()
    if len(key) <= 4:
        return "****"
    return f"…{key[-4:]}"

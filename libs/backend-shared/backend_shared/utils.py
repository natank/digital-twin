"""Common utilities: field-level encryption and validation helpers.

Encryption functions take the key as an argument rather than reading it from
application settings — that keeps this library free of configuration
dependencies and makes the functions trivially testable. Callers are expected
to pass ``settings.encryption_key``.
"""

import re

from cryptography.fernet import Fernet, InvalidToken

from backend_shared.exceptions import ValidationError

# Deliberately pragmatic: full RFC 5322 validation is not useful here, and
# deliverability can only ever be confirmed by sending mail. Pydantic's
# EmailStr should be preferred at API boundaries; this helper exists for
# non-schema call sites.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")

MIN_PASSWORD_LENGTH = 8


def generate_encryption_key() -> str:
    """Generate a new Fernet key, for provisioning ``ENCRYPTION_KEY``."""
    return Fernet.generate_key().decode()


def encrypt_field(value: str, key: str) -> str:
    """Encrypt a string for at-rest storage.

    Args:
        value: Plaintext to encrypt.
        key: URL-safe base64-encoded 32-byte Fernet key.

    Raises:
        ValidationError: If the key is not a valid Fernet key.
    """
    try:
        cipher = Fernet(key.encode() if isinstance(key, str) else key)
    except (ValueError, TypeError) as exc:
        raise ValidationError("Invalid encryption key") from exc
    return cipher.encrypt(value.encode()).decode()


def decrypt_field(encrypted: str, key: str) -> str:
    """Decrypt a value produced by :func:`encrypt_field`.

    Raises:
        ValidationError: If the key is invalid or the ciphertext was not
            produced by this key (tampered, corrupted, or wrong key).
    """
    try:
        cipher = Fernet(key.encode() if isinstance(key, str) else key)
    except (ValueError, TypeError) as exc:
        raise ValidationError("Invalid encryption key") from exc
    try:
        return cipher.decrypt(encrypted.encode()).decode()
    except InvalidToken as exc:
        raise ValidationError("Could not decrypt value") from exc


def validate_email(email: str) -> bool:
    """Return whether ``email`` looks like a valid address."""
    if not email or len(email) > 254:
        return False
    return bool(_EMAIL_RE.match(email))


def validate_password_strength(password: str) -> list[str]:
    """Check a password against the policy in docs/PRD.md (E1-S1).

    Returns:
        A list of human-readable problems; empty means the password passes.
    """
    problems: list[str] = []
    if len(password) < MIN_PASSWORD_LENGTH:
        problems.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
    if not any(c.isupper() for c in password):
        problems.append("Password must contain an uppercase letter")
    if not any(c.isdigit() for c in password):
        problems.append("Password must contain a number")
    if not any(not c.isalnum() for c in password):
        problems.append("Password must contain a special character")
    return problems

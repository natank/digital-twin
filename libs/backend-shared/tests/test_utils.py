"""Tests for encryption and validation helpers."""

import pytest

from backend_shared.exceptions import ValidationError
from backend_shared.utils import (
    decrypt_field,
    encrypt_field,
    generate_encryption_key,
    validate_email,
    validate_password_strength,
)


@pytest.fixture
def key() -> str:
    return generate_encryption_key()


def test_encrypt_decrypt_roundtrip(key: str):
    assert decrypt_field(encrypt_field("sensitive", key), key) == "sensitive"


def test_ciphertext_differs_from_plaintext(key: str):
    assert encrypt_field("sensitive", key) != "sensitive"


def test_encryption_is_non_deterministic(key: str):
    """Fernet embeds a timestamp/IV, so the same input encrypts differently."""
    assert encrypt_field("same", key) != encrypt_field("same", key)


def test_decrypt_with_wrong_key_is_rejected(key: str):
    encrypted = encrypt_field("secret", key)
    with pytest.raises(ValidationError):
        decrypt_field(encrypted, generate_encryption_key())


def test_decrypt_rejects_tampered_ciphertext(key: str):
    with pytest.raises(ValidationError):
        decrypt_field("not-a-real-token", key)


def test_encrypt_rejects_invalid_key():
    with pytest.raises(ValidationError):
        encrypt_field("value", "not-a-valid-fernet-key")


def test_unicode_survives_roundtrip(key: str):
    value = "Ünïcodé — 日本語 🎉"
    assert decrypt_field(encrypt_field(value, key), key) == value


@pytest.mark.parametrize(
    "email",
    ["user@example.com", "first.last@sub.example.co.uk", "a+tag@example.io"],
)
def test_valid_emails(email: str):
    assert validate_email(email) is True


@pytest.mark.parametrize(
    "email",
    ["", "no-at-sign", "@example.com", "user@", "user@nodot", "a b@example.com"],
)
def test_invalid_emails(email: str):
    assert validate_email(email) is False


def test_email_length_limit():
    assert validate_email("a" * 250 + "@example.com") is False


def test_strong_password_passes():
    assert validate_password_strength("SecurePass1!") == []


@pytest.mark.parametrize(
    ("password", "expected_problem"),
    [
        ("Sh0rt!", "at least 8 characters"),
        ("nouppercase1!", "uppercase letter"),
        ("NoDigitsHere!", "a number"),
        ("NoSpecial123", "special character"),
    ],
)
def test_weak_passwords_are_reported(password: str, expected_problem: str):
    problems = validate_password_strength(password)
    assert any(expected_problem in p for p in problems)


def test_multiple_problems_reported_together():
    assert len(validate_password_strength("abc")) == 4

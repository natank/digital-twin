"""Auth module tests: register, login, me, password/JWT helpers."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.auth.security import create_access_token, hash_password, verify_password
from src.db.models import Owner


STRONG_PASSWORD = "SecurePass1!"


def test_hash_and_verify_password() -> None:
    hashed = hash_password(STRONG_PASSWORD)
    assert hashed != STRONG_PASSWORD
    assert verify_password(STRONG_PASSWORD, hashed)
    assert not verify_password("wrong", hashed)


def test_register_login_me_flow(client: TestClient) -> None:
    reg = client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "password": STRONG_PASSWORD,
            "first_name": "Alice",
            "last_name": "Owner",
        },
    )
    assert reg.status_code == 201, reg.text
    body = reg.json()
    assert body["status"] == "success"
    assert body["data"]["email"] == "alice@example.com"
    assert body["data"]["email_verified"] is False

    login = client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": STRONG_PASSWORD},
    )
    assert login.status_code == 200, login.text
    token = login.json()["data"]["access_token"]
    assert token

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200, me.text
    assert me.json()["data"]["email"] == "alice@example.com"


def test_register_duplicate_email(client: TestClient) -> None:
    payload = {
        "email": "dup@example.com",
        "password": STRONG_PASSWORD,
        "first_name": "A",
        "last_name": "B",
    }
    assert client.post("/auth/register", json=payload).status_code == 201
    again = client.post("/auth/register", json=payload)
    assert again.status_code == 409
    assert again.json()["error"]["code"] == "CONFLICT_001"


def test_register_weak_password(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "weak@example.com",
            "password": "password",
            "first_name": "A",
            "last_name": "B",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_001"


def test_login_invalid_credentials(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={
            "email": "bob@example.com",
            "password": STRONG_PASSWORD,
            "first_name": "Bob",
            "last_name": "Owner",
        },
    )
    response = client.post(
        "/auth/login",
        json={"email": "bob@example.com", "password": "WrongPass1!"},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["error"]["message"]


def test_me_without_token(client: TestClient) -> None:
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_with_invalid_token(client: TestClient) -> None:
    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert response.status_code == 401


def test_create_access_token_roundtrip(db_session: Session) -> None:
    owner = Owner(
        email="jwt@example.com",
        password_hash=hash_password(STRONG_PASSWORD),
        first_name="J",
        last_name="W",
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)

    session_id = uuid.uuid4()
    token, expires = create_access_token(owner_id=owner.id, session_id=session_id)
    assert isinstance(token, str)
    assert expires is not None


def test_logout_invalidates_session(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={
            "email": "logout@example.com",
            "password": STRONG_PASSWORD,
            "first_name": "L",
            "last_name": "O",
        },
    )
    login = client.post(
        "/auth/login",
        json={"email": "logout@example.com", "password": STRONG_PASSWORD},
    )
    token = login.json()["data"]["access_token"]
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200

    out = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert out.status_code == 200
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_refresh_token_rotates(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={
            "email": "refresh@example.com",
            "password": STRONG_PASSWORD,
            "first_name": "R",
            "last_name": "F",
        },
    )
    login = client.post(
        "/auth/login",
        json={"email": "refresh@example.com", "password": STRONG_PASSWORD},
    )
    old_token = login.json()["data"]["access_token"]
    refreshed = client.post(
        "/auth/refresh-token",
        headers={"Authorization": f"Bearer {old_token}"},
    )
    assert refreshed.status_code == 200, refreshed.text
    new_token = refreshed.json()["data"]["access_token"]
    assert new_token != old_token
    # Old token no longer matches stored hash.
    assert (
        client.get("/auth/me", headers={"Authorization": f"Bearer {old_token}"}).status_code == 401
    )
    assert (
        client.get("/auth/me", headers={"Authorization": f"Bearer {new_token}"}).status_code == 200
    )


def test_login_rate_limit(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    import threading

    from src.auth import rate_limit as rl
    from src.settings import Settings

    # Deterministic in-memory limiter (ignore Redis leftover keys).
    settings = Settings(
        auth_login_max_attempts=3,
        auth_login_lockout_seconds=900,
    )
    limiter = rl.LoginRateLimiter.__new__(rl.LoginRateLimiter)
    limiter._settings = settings  # type: ignore[attr-defined]
    limiter._memory = {}  # type: ignore[attr-defined]
    limiter._lock = threading.Lock()  # type: ignore[attr-defined]
    limiter._redis = None  # type: ignore[attr-defined]
    rl._limiter = limiter  # type: ignore[attr-defined]

    email = f"limited-{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": STRONG_PASSWORD,
            "first_name": "X",
            "last_name": "Y",
        },
    )
    for _ in range(3):
        resp = client.post(
            "/auth/login",
            json={"email": email, "password": "WrongPass1!"},
        )
        assert resp.status_code == 401, resp.text

    blocked = client.post(
        "/auth/login",
        json={"email": email, "password": "WrongPass1!"},
    )
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "RATE_LIMIT_001"

    rl._limiter = None  # type: ignore[attr-defined]

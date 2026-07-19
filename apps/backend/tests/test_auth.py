"""Auth module tests: register, login, me, password/JWT helpers."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.auth.security import create_access_token, hash_password, verify_password
from src.db.models import Owner
from sqlalchemy.orm import Session
import uuid


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

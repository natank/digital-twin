"""Profile CRUD API tests (Phase 1 PR-007+)."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.db.models import Owner, Profile

STRONG_PASSWORD = "SecurePass1!"


def _register_and_login(
    client: TestClient,
    email: str = "profile-owner@example.com",
) -> str:
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": STRONG_PASSWORD,
            "first_name": "Pat",
            "last_name": "Owner",
        },
    )
    login = client.post(
        "/auth/login",
        json={"email": email, "password": STRONG_PASSWORD},
    )
    assert login.status_code == 200, login.text
    return login.json()["data"]["access_token"]


def test_get_me_requires_auth(client: TestClient) -> None:
    assert client.get("/profiles/me").status_code == 401


def test_get_me_auto_creates_profile(client: TestClient) -> None:
    token = _register_and_login(client, "auto-profile@example.com")
    response = client.get("/profiles/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "success"
    data = body["data"]
    assert data["has_cv"] is False
    assert data["headline"] is None
    assert "cv_extracted_text" not in data


def test_put_me_updates_fields(client: TestClient) -> None:
    token = _register_and_login(client, "update-profile@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/profiles/me",
        headers=headers,
        json={
            "headline": "Staff Engineer",
            "bio": "Builds twins.",
            "skills": ["Python", "FastAPI"],
            "experience_years": 8,
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["headline"] == "Staff Engineer"
    assert data["bio"] == "Builds twins."
    assert data["skills"] == ["Python", "FastAPI"]
    assert data["experience_years"] == 8

    again = client.get("/profiles/me", headers=headers)
    assert again.json()["data"]["headline"] == "Staff Engineer"


def test_public_profile_limited_fields(client: TestClient, db_session: Session) -> None:
    token = _register_and_login(client, "public-profile@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    client.put(
        "/profiles/me",
        headers=headers,
        json={"headline": "Public Headline", "skills": ["Go"]},
    )
    me = client.get("/profiles/me", headers=headers).json()["data"]
    owner_id = me["owner_id"]

    pub = client.get(f"/profiles/{owner_id}")
    assert pub.status_code == 200, pub.text
    data = pub.json()["data"]
    assert data["headline"] == "Public Headline"
    assert data["skills"] == ["Go"]
    assert "bio" not in data
    assert "cv_file_path" not in data
    assert data["first_name"] == "Pat"


def test_public_profile_unknown_owner(client: TestClient) -> None:
    response = client.get(f"/profiles/{uuid.uuid4()}")
    assert response.status_code == 404


def test_register_creates_empty_profile(client: TestClient, db_session: Session) -> None:
    email = f"seeded-{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": STRONG_PASSWORD,
            "first_name": "A",
            "last_name": "B",
        },
    )
    owner = db_session.query(Owner).filter(Owner.email == email).first()
    assert owner is not None
    profile = db_session.query(Profile).filter(Profile.owner_id == owner.id).first()
    assert profile is not None

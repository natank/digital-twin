"""OAuth skeleton tests with mocked provider clients."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.auth.oauth import OAuthProfile, set_oauth_client
from src.settings import get_settings


class _FakeOAuthClient:
    def fetch_google(self, access_token: str) -> OAuthProfile:
        assert access_token == "google-token"
        return OAuthProfile(
            email="google.user@example.com",
            sub="google-sub-1",
            first_name="Goo",
            last_name="Gle",
            email_verified=True,
        )

    def fetch_github(self, access_token: str) -> OAuthProfile:
        assert access_token == "github-token"
        return OAuthProfile(
            email="gh.user@example.com",
            sub="42",
            first_name="Git",
            last_name="Hub",
            email_verified=True,
        )


def test_oauth_google_not_configured(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "")
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
    get_settings.cache_clear()
    response = client.post("/auth/oauth/google", json={"access_token": "x" * 10})
    assert response.status_code == 502
    assert "not configured" in response.json()["error"]["message"]
    get_settings.cache_clear()


def test_oauth_google_success(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "gid")
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "gsecret")
    get_settings.cache_clear()
    set_oauth_client(_FakeOAuthClient())
    try:
        response = client.post(
            "/auth/oauth/google",
            json={"access_token": "google-token"},
        )
        assert response.status_code == 200, response.text
        data = response.json()["data"]
        assert data["owner"]["email"] == "google.user@example.com"
        assert data["owner"]["oauth_provider"] == "google"
        assert data["access_token"]
        # Second call reuses the same oauth owner.
        again = client.post(
            "/auth/oauth/google",
            json={"access_token": "google-token"},
        )
        assert again.status_code == 200
        assert again.json()["data"]["owner"]["id"] == data["owner"]["id"]
    finally:
        set_oauth_client(None)
        get_settings.cache_clear()


def test_oauth_github_success(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("GITHUB_OAUTH_CLIENT_ID", "hid")
    monkeypatch.setenv("GITHUB_OAUTH_CLIENT_SECRET", "hsecret")
    get_settings.cache_clear()
    set_oauth_client(_FakeOAuthClient())
    try:
        response = client.post(
            "/auth/oauth/github",
            json={"access_token": "github-token"},
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"]["owner"]["email"] == "gh.user@example.com"
    finally:
        set_oauth_client(None)
        get_settings.cache_clear()


def test_oauth_conflict_existing_email(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "gid")
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "gsecret")
    get_settings.cache_clear()
    client.post(
        "/auth/register",
        json={
            "email": "google.user@example.com",
            "password": "SecurePass1!",
            "first_name": "Existing",
            "last_name": "User",
        },
    )
    set_oauth_client(_FakeOAuthClient())
    try:
        response = client.post(
            "/auth/oauth/google",
            json={"access_token": "google-token"},
        )
        assert response.status_code == 409
    finally:
        set_oauth_client(None)
        get_settings.cache_clear()

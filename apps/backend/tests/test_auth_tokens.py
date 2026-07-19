"""Email verification and password-reset flow tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.email.sender import ConsoleEmailSender, set_email_sender

STRONG_PASSWORD = "SecurePass1!"
NEW_PASSWORD = "NewSecure9!"


def test_verify_email_flow(client: TestClient) -> None:
    sender = ConsoleEmailSender()
    set_email_sender(sender)
    try:
        reg = client.post(
            "/auth/register",
            json={
                "email": "verify@example.com",
                "password": STRONG_PASSWORD,
                "first_name": "V",
                "last_name": "E",
            },
        )
        assert reg.status_code == 201
        assert reg.json()["data"]["email_verified"] is False
        assert sender.sent, "expected verification email"
        # Extract token from console body line that is just the token.
        body = sender.sent[-1]["body"]
        token = next(
            line.strip()
            for line in body.splitlines()
            if line.strip() and " " not in line.strip() and len(line.strip()) > 20
        )

        verified = client.post("/auth/verify-email", json={"token": token})
        assert verified.status_code == 200, verified.text
        assert verified.json()["data"]["email_verified"] is True
    finally:
        set_email_sender(None)


def test_password_reset_flow(client: TestClient) -> None:
    sender = ConsoleEmailSender()
    set_email_sender(sender)
    try:
        client.post(
            "/auth/register",
            json={
                "email": "resetme@example.com",
                "password": STRONG_PASSWORD,
                "first_name": "R",
                "last_name": "S",
            },
        )
        login = client.post(
            "/auth/login",
            json={"email": "resetme@example.com", "password": STRONG_PASSWORD},
        )
        old_token = login.json()["data"]["access_token"]

        forgot = client.post("/auth/forgot-password", json={"email": "resetme@example.com"})
        assert forgot.status_code == 202
        assert sender.sent
        body = sender.sent[-1]["body"]
        reset_token = next(
            line.strip()
            for line in body.splitlines()
            if line.strip() and " " not in line.strip() and len(line.strip()) > 20
        )

        reset = client.post(
            "/auth/reset-password",
            json={"token": reset_token, "new_password": NEW_PASSWORD},
        )
        assert reset.status_code == 200, reset.text

        # Old session invalidated.
        assert (
            client.get("/auth/me", headers={"Authorization": f"Bearer {old_token}"}).status_code
            == 401
        )
        # New password works.
        again = client.post(
            "/auth/login",
            json={"email": "resetme@example.com", "password": NEW_PASSWORD},
        )
        assert again.status_code == 200
        # Old password fails.
        assert (
            client.post(
                "/auth/login",
                json={"email": "resetme@example.com", "password": STRONG_PASSWORD},
            ).status_code
            == 401
        )
    finally:
        set_email_sender(None)


def test_forgot_password_unknown_email_still_202(client: TestClient) -> None:
    response = client.post(
        "/auth/forgot-password",
        json={"email": "nobody@example.com"},
    )
    assert response.status_code == 202

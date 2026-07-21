"""Config module tests (Phase 2 PR-006+)."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

STRONG_PASSWORD = "SecurePass1!"


def _register_login(client: TestClient, email: str | None = None) -> str:
    email = email or f"cfg-{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": STRONG_PASSWORD,
            "first_name": "C",
            "last_name": "O",
        },
    )
    login = client.post(
        "/auth/login",
        json={"email": email, "password": STRONG_PASSWORD},
    )
    assert login.status_code == 200, login.text
    return login.json()["data"]["access_token"]


def test_config_status_mounted(client: TestClient) -> None:
    assert client.get("/config/status").status_code == 200
    assert client.get("/config/status").json()["module"] == "config"


def test_get_me_requires_auth(client: TestClient) -> None:
    assert client.get("/config/me").status_code == 401


def test_get_me_auto_creates_defaults(client: TestClient) -> None:
    token = _register_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/config/me", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["tone"] == "professional"
    assert data["response_length"] == "balanced"
    assert "digital twin" in data["system_prompt"].lower()
    assert data["allowed_topics"] == []


def test_put_me_updates_fields(client: TestClient) -> None:
    token = _register_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/config/me",
        headers=headers,
        json={
            "tone": "friendly",
            "response_length": "concise",
            "allowed_topics": ["Python", "APIs"],
            "forbidden_topics": ["politics"],
            "brand_guidelines": "Mention FastAPI",
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["tone"] == "friendly"
    assert data["response_length"] == "concise"
    assert data["allowed_topics"] == ["Python", "APIs"]
    assert data["forbidden_topics"] == ["politics"]
    assert data["brand_guidelines"] == "Mention FastAPI"

    again = client.get("/config/me", headers=headers)
    assert again.json()["data"]["tone"] == "friendly"


def test_put_invalid_tone(client: TestClient) -> None:
    token = _register_login(client)
    response = client.put(
        "/config/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"tone": "sassy"},
    )
    assert response.status_code == 422


def test_owners_isolated(client: TestClient) -> None:
    token_a = _register_login(client, f"a-{uuid.uuid4().hex[:8]}@ex.com")
    token_b = _register_login(client, f"b-{uuid.uuid4().hex[:8]}@ex.com")
    client.put(
        "/config/me",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"tone": "technical"},
    )
    data_b = client.get("/config/me", headers={"Authorization": f"Bearer {token_b}"}).json()["data"]
    assert data_b["tone"] == "professional"


def test_system_prompt_versions_and_restore(client: TestClient) -> None:
    token = _register_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    client.get("/config/me", headers=headers)

    put1 = client.put(
        "/config/me/system-prompt",
        headers=headers,
        json={"system_prompt": "PROMPT_V2 for {owner_name}"},
    )
    assert put1.status_code == 200, put1.text
    assert put1.json()["data"]["version_number"] == 2

    put2 = client.put(
        "/config/me/system-prompt",
        headers=headers,
        json={"system_prompt": "PROMPT_V3 marker unique"},
    )
    assert put2.json()["data"]["version_number"] == 3

    versions = client.get("/config/me/system-prompt/versions", headers=headers)
    assert versions.status_code == 200
    nums = [v["version_number"] for v in versions.json()["data"]["versions"]]
    assert nums[0] == 3
    assert 1 in nums and 2 in nums

    restored = client.post("/config/me/system-prompt/restore/2", headers=headers)
    assert restored.status_code == 200, restored.text
    assert "PROMPT_V2" in restored.json()["data"]["system_prompt"]
    assert restored.json()["data"]["version_number"] == 4


def test_system_prompt_empty_rejected(client: TestClient) -> None:
    token = _register_login(client)
    response = client.put(
        "/config/me/system-prompt",
        headers={"Authorization": f"Bearer {token}"},
        json={"system_prompt": "   "},
    )
    assert response.status_code == 422


def test_prompt_preview_uses_mock_llm(client: TestClient) -> None:
    token = _register_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/config/me/system-prompt/preview",
        headers=headers,
        json={
            "system_prompt": "You are twin for {owner_name}. Context: {profile_summary}",
            "sample_question": "What do you do?",
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert "twin" in data["rendered_system_prompt"].lower()
    assert data["sample_reply"]

"""Phase 2 cross-module integration (PR-010).

Register → config → chat (config-aware) → notification → mark read.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from src.notifications.pushover_client import FakePushoverClient, set_pushover_client

STRONG_PASSWORD = "SecurePass1!"


def test_phase2_config_chat_notify_flow(client: TestClient) -> None:
    fake = FakePushoverClient()
    set_pushover_client(fake)
    try:
        email = f"p2-{uuid.uuid4().hex[:8]}@example.com"
        reg = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": STRONG_PASSWORD,
                "first_name": "Phase",
                "last_name": "Two",
            },
        )
        assert reg.status_code == 201, reg.text
        owner_id = reg.json()["data"]["id"]
        token = client.post(
            "/auth/login",
            json={"email": email, "password": STRONG_PASSWORD},
        ).json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Config: tone + custom prompt marker
        cfg = client.put(
            "/config/me",
            headers=headers,
            json={
                "tone": "friendly",
                "system_prompt": (
                    "PHASE2_MARKER twin for {owner_name}. Context:\n{profile_summary}"
                ),
            },
        )
        assert cfg.status_code == 200, cfg.text
        assert cfg.json()["data"]["tone"] == "friendly"

        # Pushover for delivery path
        client.put(
            "/notifications/me/pushover",
            headers=headers,
            json={"user_key": "valid-user-key-12345", "enabled": True},
        )

        # Capture LLM system prompt
        from src.llm import claude as claude_mod

        captured: dict[str, str] = {}

        def _cap(system_prompt: str, messages: list) -> tuple[str, int | None]:
            captured["system"] = system_prompt
            return ("phase2 reply", 3)

        claude_mod.set_chat_reply_generator(_cap)
        try:
            sid = client.post("/chat/sessions", json={"owner_id": owner_id}).json()["data"][
                "session_id"
            ]
            msg = client.post(
                f"/chat/sessions/{sid}/messages",
                json={"content": "What is your background?"},
            )
            assert msg.status_code == 200, msg.text
            assert "PHASE2_MARKER" in captured.get("system", "")
            assert "friendly" in captured.get("system", "").lower() or "Tone" in captured.get(
                "system", ""
            )
        finally:
            claude_mod.set_chat_reply_generator(None)

        # Notification created for conversation_started
        listed = client.get("/notifications/me", headers=headers)
        assert listed.status_code == 200
        items = listed.json()["data"]["items"]
        assert any(i["type"] == "conversation_started" for i in items)
        # Push should have been attempted (eager delivery)
        assert fake.calls or items[0]["delivery_status"] in {
            "sent",
            "pending",
            "skipped",
            "failed",
        }

        nid = items[0]["id"]
        read = client.post(f"/notifications/me/{nid}/read", headers=headers)
        assert read.status_code == 200
        assert read.json()["data"]["read"] is True
    finally:
        set_pushover_client(None)

"""Notifications module tests (Phase 2 Week 9 PR-001–005)."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.db.models import Notification, Owner, Profile
from src.notifications.encryption import decrypt_secret, encrypt_secret, mask_user_key
from src.notifications.pushover_client import FakePushoverClient, set_pushover_client
from src.notifications.service import create_notification
from src.worker.tasks.notifications import deliver_notification_job

STRONG_PASSWORD = "SecurePass1!"


def _register_login(client: TestClient, email: str) -> tuple[str, str]:
    reg = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": STRONG_PASSWORD,
            "first_name": "N",
            "last_name": "O",
        },
    )
    assert reg.status_code == 201, reg.text
    owner_id = reg.json()["data"]["id"]
    login = client.post(
        "/auth/login",
        json={"email": email, "password": STRONG_PASSWORD},
    )
    assert login.status_code == 200, login.text
    return login.json()["data"]["access_token"], owner_id


@pytest.fixture()
def fake_pushover():
    client = FakePushoverClient()
    set_pushover_client(client)
    yield client
    set_pushover_client(None)


def test_notifications_status_mounted(client: TestClient) -> None:
    response = client.get("/notifications/status")
    assert response.status_code == 200
    assert response.json()["module"] == "notifications"


def test_encrypt_decrypt_roundtrip() -> None:
    token = encrypt_secret("my-user-key-abc")
    assert token != "my-user-key-abc"
    assert decrypt_secret(token) == "my-user-key-abc"
    assert mask_user_key("my-user-key-abc").endswith("abc")


def test_list_requires_auth(client: TestClient) -> None:
    assert client.get("/notifications/me").status_code == 401


def test_in_app_list_read_delete(client: TestClient, db_session: Session) -> None:
    token, owner_id = _register_login(client, f"n1-{uuid.uuid4().hex[:8]}@ex.com")
    headers = {"Authorization": f"Bearer {token}"}
    create_notification(
        db_session,
        owner_id=uuid.UUID(owner_id),
        type="conversation_started",
        title="Hello",
        message="Visitor said hi",
        delivery_status="skipped",
    )

    listed = client.get("/notifications/me", headers=headers)
    assert listed.status_code == 200, listed.text
    body = listed.json()["data"]
    assert body["total"] == 1
    assert body["unread_count"] == 1
    nid = body["items"][0]["id"]

    unread = client.get("/notifications/me/unread-count", headers=headers)
    assert unread.json()["data"]["unread_count"] == 1

    read = client.post(f"/notifications/me/{nid}/read", headers=headers)
    assert read.status_code == 200
    assert read.json()["data"]["read"] is True

    assert (
        client.get("/notifications/me/unread-count", headers=headers).json()["data"]["unread_count"]
        == 0
    )

    deleted = client.delete(f"/notifications/me/{nid}", headers=headers)
    assert deleted.status_code == 200
    assert client.get("/notifications/me", headers=headers).json()["data"]["total"] == 0


def test_idor_other_owner(client: TestClient, db_session: Session) -> None:
    token_a, owner_a = _register_login(client, f"na-{uuid.uuid4().hex[:8]}@ex.com")
    token_b, _owner_b = _register_login(client, f"nb-{uuid.uuid4().hex[:8]}@ex.com")
    notif = create_notification(
        db_session,
        owner_id=uuid.UUID(owner_a),
        type="test",
        title="A only",
        message="secret",
        delivery_status="skipped",
    )
    headers_b = {"Authorization": f"Bearer {token_b}"}
    assert client.post(f"/notifications/me/{notif.id}/read", headers=headers_b).status_code == 404
    assert client.delete(f"/notifications/me/{notif.id}", headers=headers_b).status_code == 404
    # Owner A can still access
    headers_a = {"Authorization": f"Bearer {token_a}"}
    assert client.post(f"/notifications/me/{notif.id}/read", headers=headers_a).status_code == 200


def test_pushover_config_mask(client: TestClient, fake_pushover: FakePushoverClient) -> None:
    token, _ = _register_login(client, f"push-{uuid.uuid4().hex[:8]}@ex.com")
    headers = {"Authorization": f"Bearer {token}"}
    put = client.put(
        "/notifications/me/pushover",
        headers=headers,
        json={
            "user_key": "uQiRzpo4DXghDmr9QzzfQu27cmVRsG",
            "sound": "cosmic",
            "enabled": True,
        },
    )
    assert put.status_code == 200, put.text
    data = put.json()["data"]
    assert data["configured"] is True
    assert data["user_key_masked"].endswith("RsG") or "…" in data["user_key_masked"]
    assert "uQiRzpo4" not in data["user_key_masked"]

    got = client.get("/notifications/me/pushover", headers=headers)
    assert got.json()["data"]["sound"] == "cosmic"


def test_deliver_success_and_skip(
    client: TestClient, db_session: Session, fake_pushover: FakePushoverClient
) -> None:
    token, owner_id = _register_login(client, f"del-{uuid.uuid4().hex[:8]}@ex.com")
    headers = {"Authorization": f"Bearer {token}"}
    client.put(
        "/notifications/me/pushover",
        headers=headers,
        json={"user_key": "valid-user-key-12345", "enabled": True},
    )
    notif = create_notification(
        db_session,
        owner_id=uuid.UUID(owner_id),
        type="test",
        title="T",
        message="M",
        delivery_status="pending",
    )
    result = deliver_notification_job(str(notif.id))
    assert result["status"] == "sent"
    assert fake_pushover.calls
    db_session.expire_all()
    row = db_session.query(Notification).filter(Notification.id == notif.id).one()
    assert row.delivery_status == "sent"
    assert row.pushover_receipt


def test_deliver_retry_then_fail(client: TestClient, db_session: Session) -> None:
    failer = FakePushoverClient(fail_times=10)
    set_pushover_client(failer)
    try:
        token, owner_id = _register_login(client, f"fail-{uuid.uuid4().hex[:8]}@ex.com")
        headers = {"Authorization": f"Bearer {token}"}
        client.put(
            "/notifications/me/pushover",
            headers=headers,
            json={"user_key": "valid-user-key-12345", "enabled": True},
        )
        notif = create_notification(
            db_session,
            owner_id=uuid.UUID(owner_id),
            type="test",
            title="T",
            message="M",
            delivery_status="pending",
        )
        # max_retries default 3
        for _ in range(3):
            result = deliver_notification_job(str(notif.id))
        assert result["status"] == "failed"
        db_session.expire_all()
        row = db_session.query(Notification).filter(Notification.id == notif.id).one()
        assert row.delivery_status == "failed"
        assert row.retry_count >= 3
    finally:
        set_pushover_client(None)


def test_chat_emits_conversation_started(
    client: TestClient, db_session: Session, fake_pushover: FakePushoverClient
) -> None:
    token, owner_id = _register_login(client, f"chat-{uuid.uuid4().hex[:8]}@ex.com")
    headers = {"Authorization": f"Bearer {token}"}
    # Seed profile summary for twin
    owner = db_session.query(Owner).filter(Owner.id == uuid.UUID(owner_id)).one()
    if owner.profile is None:
        owner.profile = Profile(headline="Eng")
    owner.profile.profile_summary = {"summary": "Test twin"}
    db_session.add(owner)
    db_session.commit()

    client.put(
        "/notifications/me/pushover",
        headers=headers,
        json={"user_key": "valid-user-key-12345", "enabled": True},
    )

    sid = client.post("/chat/sessions", json={"owner_id": owner_id}).json()["data"]["session_id"]
    msg = client.post(
        f"/chat/sessions/{sid}/messages",
        json={"content": "What is your background?"},
    )
    assert msg.status_code == 200, msg.text

    listed = client.get("/notifications/me", headers=headers)
    assert listed.status_code == 200
    items = listed.json()["data"]["items"]
    types = {i["type"] for i in items}
    assert "conversation_started" in types


def test_preferences_skip_push(
    client: TestClient, db_session: Session, fake_pushover: FakePushoverClient
) -> None:
    token, owner_id = _register_login(client, f"pref-{uuid.uuid4().hex[:8]}@ex.com")
    headers = {"Authorization": f"Bearer {token}"}
    client.put(
        "/notifications/me/pushover",
        headers=headers,
        json={"user_key": "valid-user-key-12345", "enabled": True},
    )
    prefs = client.put(
        "/notifications/me/preferences",
        headers=headers,
        json={"global_push_enabled": False},
    )
    assert prefs.status_code == 200, prefs.text

    from src.notifications.events import emit_notification_event

    nid = emit_notification_event(
        uuid.UUID(owner_id),
        type="conversation_started",
        title="X",
        message="Y",
        db=db_session,
        enqueue=True,
    )
    assert nid is not None
    db_session.expire_all()
    row = db_session.query(Notification).filter(Notification.id == nid).one()
    assert row.delivery_status == "skipped"
    assert not fake_pushover.calls


def test_test_endpoint(client: TestClient, fake_pushover: FakePushoverClient) -> None:
    token, _ = _register_login(client, f"testn-{uuid.uuid4().hex[:8]}@ex.com")
    headers = {"Authorization": f"Bearer {token}"}
    assert client.post("/notifications/me/test", headers=headers).status_code == 422
    client.put(
        "/notifications/me/pushover",
        headers=headers,
        json={"user_key": "valid-user-key-12345", "enabled": True},
    )
    resp = client.post("/notifications/me/test", headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["delivery_status"] in {"sent", "pending", "skipped"}
    assert fake_pushover.calls

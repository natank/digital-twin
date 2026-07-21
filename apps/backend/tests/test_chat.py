"""Chat module tests: sessions, messages, boundaries, SSE, rate limits."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.auth.security import hash_password
from src.chat.boundaries import check_message_boundary
from src.chat.rate_limit import ChatRateLimiter
from src.db.models import ChatSession, Owner, Profile
from src.settings import Settings

STRONG_PASSWORD = "SecurePass1!"


def _seed_owner(db: Session, email: str = "twin@example.com") -> Owner:
    owner = Owner(
        email=email,
        password_hash=hash_password(STRONG_PASSWORD),
        first_name="Twin",
        last_name="Owner",
        is_active=True,
        email_verified=True,
    )
    owner.profile = Profile(
        headline="Staff Engineer",
        skills=["Python", "FastAPI"],
        experience_years=8,
        profile_summary={
            "headline": "Staff Engineer",
            "summary": "Builds APIs and twins.",
            "highlights": ["Led platform work"],
            "skills": ["Python", "FastAPI"],
            "experience_years": 8,
        },
    )
    db.add(owner)
    db.commit()
    db.refresh(owner)
    return owner


def test_boundary_off_topic() -> None:
    result = check_message_boundary("Give me crypto tip for insider trade")
    assert result.off_topic is True
    assert result.redirect_message


def test_boundary_career_ok() -> None:
    result = check_message_boundary("What is your experience with Python?")
    assert result.off_topic is False


def test_create_get_delete_session(client: TestClient, db_session: Session) -> None:
    owner = _seed_owner(db_session)
    created = client.post("/chat/sessions", json={"owner_id": str(owner.id)})
    assert created.status_code == 201, created.text
    data = created.json()["data"]
    sid = data["session_id"]
    assert data["owner_id"] == str(owner.id)
    assert data["owner_headline"] == "Staff Engineer"
    assert data["owner_first_name"] == "Twin"

    got = client.get(f"/chat/sessions/{sid}")
    assert got.status_code == 200
    assert got.json()["data"]["session_id"] == sid

    deleted = client.delete(f"/chat/sessions/{sid}")
    assert deleted.status_code == 200
    assert client.get(f"/chat/sessions/{sid}").status_code == 404


def test_unknown_owner_404(client: TestClient) -> None:
    response = client.post("/chat/sessions", json={"owner_id": str(uuid.uuid4())})
    assert response.status_code == 404


def test_expired_session_rejected(client: TestClient, db_session: Session) -> None:
    owner = _seed_owner(db_session, "expired@example.com")
    created = client.post("/chat/sessions", json={"owner_id": str(owner.id)})
    sid = created.json()["data"]["session_id"]

    row = db_session.query(ChatSession).filter(ChatSession.public_id == sid).first()
    assert row is not None
    row.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.add(row)
    db_session.commit()

    assert client.get(f"/chat/sessions/{sid}").status_code == 422
    assert (
        client.post(
            f"/chat/sessions/{sid}/messages",
            json={"content": "Hello?"},
        ).status_code
        == 422
    )


def test_send_message_and_history(client: TestClient, db_session: Session) -> None:
    owner = _seed_owner(db_session, "msg@example.com")
    sid = client.post("/chat/sessions", json={"owner_id": str(owner.id)}).json()["data"][
        "session_id"
    ]

    sent = client.post(
        f"/chat/sessions/{sid}/messages",
        json={"content": "What is your background?"},
    )
    assert sent.status_code == 200, sent.text
    body = sent.json()["data"]
    assert body["visitor_message"]["sender"] == "visitor"
    assert body["reply"]["sender"] == "ai"
    assert "Mock twin reply" in body["reply"]["content"]
    assert body["boundary_redirect"] is False

    hist = client.get(f"/chat/sessions/{sid}/messages")
    assert hist.status_code == 200
    messages = hist.json()["data"]["messages"]
    assert len(messages) == 2
    assert messages[0]["sender"] == "visitor"
    assert messages[1]["sender"] == "ai"


def test_reject_empty_and_oversize(client: TestClient, db_session: Session) -> None:
    owner = _seed_owner(db_session, "size@example.com")
    sid = client.post("/chat/sessions", json={"owner_id": str(owner.id)}).json()["data"][
        "session_id"
    ]
    empty = client.post(f"/chat/sessions/{sid}/messages", json={"content": "   "})
    assert empty.status_code == 422

    huge = client.post(
        f"/chat/sessions/{sid}/messages",
        json={"content": "x" * 10_001},
    )
    assert huge.status_code == 422


def test_boundary_redirect_persists(client: TestClient, db_session: Session) -> None:
    owner = _seed_owner(db_session, "bound@example.com")
    sid = client.post("/chat/sessions", json={"owner_id": str(owner.id)}).json()["data"][
        "session_id"
    ]
    sent = client.post(
        f"/chat/sessions/{sid}/messages",
        json={"content": "Give me a crypto tip for insider trade please"},
    )
    assert sent.status_code == 200, sent.text
    data = sent.json()["data"]
    assert data["boundary_redirect"] is True
    assert (
        "career" in data["reply"]["content"].lower()
        or "professional" in data["reply"]["content"].lower()
    )


def test_sse_stream_post(client: TestClient, db_session: Session) -> None:
    owner = _seed_owner(db_session, "sse@example.com")
    sid = client.post("/chat/sessions", json={"owner_id": str(owner.id)}).json()["data"][
        "session_id"
    ]
    with client.stream(
        "POST",
        f"/chat/sse/{sid}/stream",
        json={"content": "Tell me about your skills"},
    ) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")
        body = "".join(response.iter_text())
    assert "event: meta" in body
    assert "event: token" in body
    assert "event: done" in body
    assert "Mock twin reply" in body


def test_chat_uses_owner_config_prompt(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    from src.llm import claude as claude_mod

    captured: dict[str, str] = {}

    def _capture(system_prompt: str, messages: list) -> tuple[str, int | None]:
        captured["system"] = system_prompt
        return ("ok", 1)

    claude_mod.set_chat_reply_generator(_capture)
    try:
        owner = _seed_owner(db_session, f"cfgchat-{uuid.uuid4().hex[:8]}@ex.com")
        # Login as owner to set config
        client.post(
            "/auth/register",
            json={
                "email": f"login-{uuid.uuid4().hex[:8]}@ex.com",
                "password": STRONG_PASSWORD,
                "first_name": "X",
                "last_name": "Y",
            },
        )
        # Directly set config for seeded owner via service
        from src.config.service import get_or_create_config, update_config

        cfg = get_or_create_config(db_session, owner)
        update_config(
            db_session,
            owner,
            system_prompt="MARKER_UNIQUE_PROMPT for {owner_name}. Context: {profile_summary}",
            tone="technical",
            forbidden_topics=["cryptocurrency trading"],
            fields_set={"system_prompt", "tone", "forbidden_topics"},
        )
        assert cfg is not None

        sid = client.post("/chat/sessions", json={"owner_id": str(owner.id)}).json()["data"][
            "session_id"
        ]
        resp = client.post(
            f"/chat/sessions/{sid}/messages",
            json={"content": "What is your engineering experience?"},
        )
        assert resp.status_code == 200, resp.text
        assert "MARKER_UNIQUE_PROMPT" in captured.get("system", "")
        assert "technical" in captured.get("system", "").lower() or "Tone" in captured.get(
            "system", ""
        )

        # Forbidden topic should redirect without LLM overwrite of capture necessarily
        r2 = client.post(
            f"/chat/sessions/{sid}/messages",
            json={"content": "Tell me about cryptocurrency trading strategies"},
        )
        assert r2.status_code == 200
        assert r2.json()["data"]["boundary_redirect"] is True
    finally:
        claude_mod.set_chat_reply_generator(None)


def test_chat_rate_limit_memory() -> None:
    settings = Settings(chat_rate_limit_per_hour=3, chat_rate_limit_window_seconds=3600)
    limiter = ChatRateLimiter.__new__(ChatRateLimiter)
    limiter._settings = settings  # type: ignore[attr-defined]
    limiter._memory = {}  # type: ignore[attr-defined]
    limiter._lock = __import__("threading").Lock()  # type: ignore[attr-defined]
    limiter._redis = None  # type: ignore[attr-defined]

    sid = f"sess-{uuid.uuid4().hex[:8]}"
    for _ in range(3):
        limiter.assert_allowed(sid)
    with pytest.raises(Exception) as exc:
        limiter.assert_allowed(sid)
    assert (
        "rate limit" in str(exc.value).lower()
        or getattr(exc.value, "error_code", "") == "RATE_LIMIT_001"
    )

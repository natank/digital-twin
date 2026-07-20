"""Chat domain services: sessions, messages, twin replies."""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from backend_shared.exceptions import NotFoundError, ValidationError
from backend_shared.logging import get_logger
from sqlalchemy.orm import Session, joinedload

from src.chat.boundaries import FLAG_AFTER_VIOLATIONS, check_message_boundary
from src.chat.prompts import build_system_prompt
from src.db.models import (
    ChatMessage,
    ChatSession,
    ConversationContext,
    Owner,
    Profile,
)
from src.settings import Settings, get_settings

logger = get_logger(__name__)

MAX_MESSAGE_CHARS = 10_000
LLM_FALLBACK_REPLY = (
    "I'm having trouble generating a response right now. " "Please try again in a moment."
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _hash_ip(ip: str | None) -> str | None:
    if not ip:
        return None
    return hashlib.sha256(ip.strip().encode("utf-8")).hexdigest()


def _new_public_id() -> str:
    return secrets.token_urlsafe(24)


def create_session(
    db: Session,
    *,
    owner_id: uuid.UUID,
    visitor_ip: str | None = None,
    settings: Settings | None = None,
) -> ChatSession:
    """Create an anonymous visitor session for an active owner's twin."""
    cfg = settings or get_settings()
    owner = db.query(Owner).filter(Owner.id == owner_id).first()
    if owner is None or not owner.is_active:
        raise NotFoundError("Owner not found", error_code="NOT_FOUND_001")

    now = _utcnow()
    session = ChatSession(
        public_id=_new_public_id(),
        owner_id=owner.id,
        visitor_ip_hash=_hash_ip(visitor_ip),
        expires_at=now + timedelta(minutes=cfg.chat_session_ttl_minutes),
    )
    session.context = ConversationContext(violation_count=0, flagged=False)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session_by_public_id(
    db: Session,
    public_id: str,
    *,
    allow_expired: bool = False,
) -> ChatSession:
    """Load session by public id; raise if missing or expired."""
    session = (
        db.query(ChatSession)
        .options(
            joinedload(ChatSession.owner).joinedload(Owner.profile),
            joinedload(ChatSession.context),
        )
        .filter(ChatSession.public_id == public_id)
        .first()
    )
    if session is None:
        raise NotFoundError("Chat session not found")
    if not allow_expired and _as_aware(session.expires_at) <= _utcnow():
        raise ValidationError(
            "Chat session has expired",
            error_code="VALIDATION_001",
            details={"session_id": public_id},
        )
    return session


def touch_session(db: Session, session: ChatSession, settings: Settings | None = None) -> None:
    """Extend inactivity expiry on activity."""
    cfg = settings or get_settings()
    session.expires_at = _utcnow() + timedelta(minutes=cfg.chat_session_ttl_minutes)
    db.add(session)
    db.commit()
    db.refresh(session)


def delete_session(db: Session, public_id: str) -> None:
    """End a visitor session (cascade deletes messages/context)."""
    session = db.query(ChatSession).filter(ChatSession.public_id == public_id).first()
    if session is None:
        raise NotFoundError("Chat session not found")
    db.delete(session)
    db.commit()


def list_messages(db: Session, public_id: str) -> list[ChatMessage]:
    session = get_session_by_public_id(db, public_id)
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


def _ensure_context(db: Session, session: ChatSession) -> ConversationContext:
    if session.context is not None:
        return session.context
    ctx = ConversationContext(session_id=session.id, violation_count=0, flagged=False)
    db.add(ctx)
    db.commit()
    db.refresh(ctx)
    session.context = ctx
    return ctx


def _record_violation(db: Session, session: ChatSession) -> ConversationContext:
    ctx = _ensure_context(db, session)
    ctx.violation_count = int(ctx.violation_count or 0) + 1
    if ctx.violation_count >= FLAG_AFTER_VIOLATIONS:
        ctx.flagged = True
        ctx.flag_reason = f"Repeated off-topic messages ({ctx.violation_count})"
    db.add(ctx)
    db.commit()
    db.refresh(ctx)
    return ctx


def _owner_display_name(owner: Owner) -> str:
    return f"{owner.first_name} {owner.last_name}".strip() or owner.email


def _history_for_llm(db: Session, session: ChatSession, *, limit: int = 20) -> list[dict[str, str]]:
    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    rows = list(reversed(rows))
    out: list[dict[str, str]] = []
    for m in rows:
        role = "user" if m.sender == "visitor" else "assistant"
        out.append({"role": role, "content": m.content})
    return out


def post_message(
    db: Session,
    public_id: str,
    content: str,
    *,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Persist visitor message, generate AI reply (or boundary redirect), return both."""
    cfg = settings or get_settings()
    text = (content or "").strip()
    if not text:
        raise ValidationError("Message content is required", details={"field": "content"})
    if len(text) > MAX_MESSAGE_CHARS:
        raise ValidationError(
            f"Message exceeds maximum of {MAX_MESSAGE_CHARS} characters",
            details={"field": "content", "max": MAX_MESSAGE_CHARS},
        )

    session = get_session_by_public_id(db, public_id)
    owner = session.owner
    profile: Profile | None = owner.profile if owner else None

    visitor_msg = ChatMessage(
        session_id=session.id,
        sender="visitor",
        content=text,
        tokens_used=None,
    )
    db.add(visitor_msg)
    db.commit()
    db.refresh(visitor_msg)

    boundary = check_message_boundary(text)
    boundary_redirect = False
    tokens_used: int | None = None

    if boundary.off_topic and boundary.redirect_message:
        reply_text = boundary.redirect_message
        boundary_redirect = True
        _record_violation(db, session)
    else:
        system = build_system_prompt(
            owner_name=_owner_display_name(owner),
            profile_summary=profile.profile_summary if profile else None,
            skills=profile.skills if profile else None,
        )
        history = _history_for_llm(db, session)
        try:
            from src.llm.claude import generate_chat_reply

            reply_text, tokens_used = generate_chat_reply(
                system_prompt=system,
                messages=history,
                settings=cfg,
            )
        except Exception:  # noqa: BLE001
            logger.exception("chat LLM failed session=%s", public_id)
            reply_text = LLM_FALLBACK_REPLY

    ai_msg = ChatMessage(
        session_id=session.id,
        sender="ai",
        content=reply_text,
        tokens_used=tokens_used,
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    touch_session(db, session, cfg)

    # Phase 2: emit notifications (never fail the chat response).
    try:
        _emit_chat_notifications(
            db,
            session=session,
            visitor_text=text,
            public_id=public_id,
            boundary_redirect=boundary_redirect,
        )
    except Exception:  # noqa: BLE001
        logger.exception(
            "notification hook failed session=%s",
            public_id,
        )

    logger.info(
        "message_processed session=%s visitor_msg=%s ai_msg=%s boundary=%s",
        public_id,
        visitor_msg.id,
        ai_msg.id,
        boundary_redirect,
    )

    return {
        "visitor_message": visitor_msg,
        "reply": ai_msg,
        "session": session,
        "boundary_redirect": boundary_redirect,
    }


def _emit_chat_notifications(
    db: Session,
    *,
    session: ChatSession,
    visitor_text: str,
    public_id: str,
    boundary_redirect: bool,
) -> None:
    """Notify owner of first message / high-intent signals."""
    from src.notifications.events import (
        looks_like_high_intent,
        notify_conversation_started,
        notify_high_intent,
    )

    visitor_count = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session.id,
            ChatMessage.sender == "visitor",
        )
        .count()
    )
    if visitor_count == 1:
        notify_conversation_started(
            session.owner_id,
            session_public_id=public_id,
            preview=visitor_text,
            db=db,
        )
    if boundary_redirect or looks_like_high_intent(visitor_text):
        # High-intent: keyword match; also surface boundary-flagged as attention.
        if looks_like_high_intent(visitor_text):
            notify_high_intent(
                session.owner_id,
                session_public_id=public_id,
                preview=visitor_text,
                db=db,
            )


def stream_reply_chunks(text: str, *, chunk_size: int = 48) -> list[str]:
    """Split a full reply into SSE-friendly chunks (deterministic for tests)."""
    if not text:
        return [""]
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def session_to_response_dict(session: ChatSession) -> dict[str, Any]:
    owner = session.owner
    profile = owner.profile if owner else None
    flagged = bool(session.context.flagged) if session.context else False
    return {
        "session_id": session.public_id,
        "owner_id": session.owner_id,
        "expires_at": session.expires_at,
        "created_at": session.created_at,
        "owner_headline": profile.headline if profile else None,
        "owner_first_name": owner.first_name if owner else None,
        "flagged": flagged,
    }


def message_to_dict(msg: ChatMessage) -> dict[str, Any]:
    return {
        "id": msg.id,
        "sender": msg.sender,
        "content": msg.content,
        "tokens_used": msg.tokens_used,
        "created_at": msg.created_at,
    }

"""Product event → notification creation + async delivery enqueue."""

from __future__ import annotations

import uuid
from typing import Any

from backend_shared.logging import get_logger
from sqlalchemy.orm import Session

from src.db.session import SessionLocal
from src.notifications.schemas import (
    NOTIF_CONVERSATION_STARTED,
    NOTIF_HIGH_INTENT,
    NOTIF_PROFILE_SUMMARY_READY,
    NOTIF_TEST,
)
from src.notifications.service import create_notification, is_push_enabled_for_type

logger = get_logger(__name__)


def emit_notification_event(
    owner_id: uuid.UUID,
    *,
    type: str,
    title: str,
    message: str,
    data: dict[str, Any] | None = None,
    priority: int = 0,
    db: Session | None = None,
    enqueue: bool = True,
) -> uuid.UUID | None:
    """Create an in-app notification and optionally enqueue Pushover delivery.

    Never raises to callers when ``db`` is owned externally and fails mid-flight
    for delivery — creation errors are logged and return None.
    """
    owns_session = db is None
    session = db or SessionLocal()
    try:
        push_wanted = is_push_enabled_for_type(session, owner_id, type)
        # Always store in-app; skip push enqueue if disabled.
        delivery = "pending" if push_wanted else "skipped"
        notif = create_notification(
            session,
            owner_id=owner_id,
            type=type,
            title=title,
            message=message,
            data=data,
            priority=priority,
            delivery_status=delivery,
        )
        notif_id = notif.id
        if enqueue and push_wanted:
            try:
                from src.worker.tasks.notifications import deliver_notification

                deliver_notification.delay(str(notif_id))
            except Exception:  # noqa: BLE001
                logger.exception("failed to enqueue notification delivery id=%s", notif_id)
        return notif_id
    except Exception:  # noqa: BLE001
        logger.exception("emit_notification_event failed owner=%s type=%s", owner_id, type)
        return None
    finally:
        if owns_session:
            session.close()


def notify_conversation_started(
    owner_id: uuid.UUID,
    *,
    session_public_id: str,
    preview: str,
    db: Session | None = None,
) -> None:
    preview_clean = (preview or "").strip()
    if len(preview_clean) > 200:
        preview_clean = preview_clean[:197] + "…"
    emit_notification_event(
        owner_id,
        type=NOTIF_CONVERSATION_STARTED,
        title="New visitor conversation",
        message=preview_clean or "A visitor started chatting with your twin.",
        data={"session_id": session_public_id},
        priority=0,
        db=db,
    )


def notify_high_intent(
    owner_id: uuid.UUID,
    *,
    session_public_id: str,
    preview: str,
    db: Session | None = None,
) -> None:
    preview_clean = (preview or "").strip()
    if len(preview_clean) > 200:
        preview_clean = preview_clean[:197] + "…"
    emit_notification_event(
        owner_id,
        type=NOTIF_HIGH_INTENT,
        title="High-intent message",
        message=preview_clean or "A visitor sent a high-intent message.",
        data={"session_id": session_public_id},
        priority=1,
        db=db,
    )


def notify_profile_summary_ready(
    owner_id: uuid.UUID,
    *,
    db: Session | None = None,
) -> None:
    emit_notification_event(
        owner_id,
        type=NOTIF_PROFILE_SUMMARY_READY,
        title="Profile summary ready",
        message="Your CV profile summary has been generated.",
        data={},
        priority=0,
        db=db,
    )


def notify_test(owner_id: uuid.UUID, *, db: Session | None = None) -> uuid.UUID | None:
    return emit_notification_event(
        owner_id,
        type=NOTIF_TEST,
        title="Test notification",
        message="This is a test notification from Digital Twin.",
        data={"test": True},
        priority=0,
        db=db,
        enqueue=True,
    )


# Lightweight high-intent keywords (not ML).
_HIGH_INTENT_HINTS = (
    "hire",
    "available",
    "rate",
    "budget",
    "contract",
    "interview",
    "schedule a call",
    "looking for",
    "opportunity",
)


def looks_like_high_intent(text: str) -> bool:
    lower = (text or "").lower()
    return any(h in lower for h in _HIGH_INTENT_HINTS)

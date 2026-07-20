"""Celery task: deliver a notification via Pushover with retries."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from backend_shared.logging import get_logger

from src.worker.celery_app import celery_app

logger = get_logger(__name__)


def deliver_notification_job(notification_id: str) -> dict[str, str]:
    """Attempt one delivery; returns status. Marks failed after max retries."""
    from src.db.models import Notification, PushoverConfig
    from src.db.session import SessionLocal
    from src.notifications.encryption import decrypt_secret
    from src.notifications.pushover_client import get_pushover_client
    from src.settings import get_settings

    try:
        notif_uuid = uuid.UUID(notification_id)
    except ValueError:
        return {"notification_id": notification_id, "status": "invalid_id"}

    settings = get_settings()
    max_retries = settings.notification_max_retries
    db = SessionLocal()
    try:
        notif = db.query(Notification).filter(Notification.id == notif_uuid).first()
        if notif is None:
            return {"notification_id": notification_id, "status": "not_found"}

        if notif.delivery_status in {"sent", "skipped"}:
            return {
                "notification_id": notification_id,
                "status": notif.delivery_status,
            }

        config = db.query(PushoverConfig).filter(PushoverConfig.owner_id == notif.owner_id).first()
        if config is None or not config.enabled:
            notif.delivery_status = "skipped"
            notif.error_message = "Pushover not configured or disabled"
            db.add(notif)
            db.commit()
            return {"notification_id": notification_id, "status": "skipped"}

        try:
            user_key = decrypt_secret(config.user_key_encrypted, settings=settings)
        except Exception as exc:  # noqa: BLE001
            notif.delivery_status = "failed"
            notif.error_message = f"decrypt failed: {exc}"[:500]
            db.add(notif)
            db.commit()
            return {"notification_id": notification_id, "status": "failed"}

        client = get_pushover_client()
        result = client.send(
            user_key=user_key,
            message=notif.message,
            title=notif.title,
            priority=int(notif.priority or 0),
            device=config.device,
            sound=config.sound or "pushover",
        )

        if result.ok:
            notif.delivery_status = "sent"
            notif.pushover_receipt = result.receipt
            notif.sent_at = datetime.now(timezone.utc)
            notif.error_message = None
            db.add(notif)
            db.commit()
            logger.info("notification delivered id=%s", notification_id)
            return {"notification_id": notification_id, "status": "sent"}

        notif.retry_count = int(notif.retry_count or 0) + 1
        notif.error_message = (result.error or "delivery failed")[:500]
        if notif.retry_count >= max_retries:
            notif.delivery_status = "failed"
            db.add(notif)
            db.commit()
            logger.warning(
                "notification permanently failed id=%s retries=%s",
                notification_id,
                notif.retry_count,
            )
            return {"notification_id": notification_id, "status": "failed"}

        notif.delivery_status = "pending"
        db.add(notif)
        db.commit()
        return {
            "notification_id": notification_id,
            "status": "retry",
            "retry_count": str(notif.retry_count),
        }
    finally:
        db.close()


@celery_app.task(name="tasks.deliver_notification", bind=True, max_retries=3)
def deliver_notification(self: Any, notification_id: str) -> dict[str, str]:
    """Deliver one notification via Pushover; re-queue while status is retry."""
    result = deliver_notification_job(notification_id)
    if result.get("status") != "retry":
        return result

    # Eager mode: loop until sent/failed without Celery broker retries.
    if getattr(self.request, "called_directly", False) or celery_app.conf.task_always_eager:
        for _ in range(5):
            result = deliver_notification_job(notification_id)
            if result.get("status") != "retry":
                return result
        from src.db.models import Notification
        from src.db.session import SessionLocal

        db = SessionLocal()
        try:
            notif = (
                db.query(Notification)
                .filter(Notification.id == uuid.UUID(notification_id))
                .first()
            )
            if notif is not None and notif.delivery_status == "pending":
                notif.delivery_status = "failed"
                db.add(notif)
                db.commit()
                return {"notification_id": notification_id, "status": "failed"}
        finally:
            db.close()
        return result

    retries = int(getattr(self.request, "retries", 0) or 0)
    countdown = 30 * (2**retries)
    raise self.retry(countdown=countdown)

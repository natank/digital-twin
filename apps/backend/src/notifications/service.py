"""Notification domain services: CRUD, Pushover config, preferences."""

from __future__ import annotations

import uuid
from typing import Any

from backend_shared.exceptions import NotFoundError, ValidationError
from sqlalchemy.orm import Session

from src.db.models import Notification, Owner, PushoverConfig
from src.notifications.encryption import decrypt_secret, encrypt_secret, mask_user_key
from src.notifications.schemas import DEFAULT_TYPE_PREFS
from src.settings import Settings


def create_notification(
    db: Session,
    *,
    owner_id: uuid.UUID,
    type: str,
    title: str,
    message: str,
    data: dict[str, Any] | None = None,
    priority: int = 0,
    delivery_status: str = "pending",
) -> Notification:
    """Persist an in-app notification row."""
    notif = Notification(
        owner_id=owner_id,
        type=type,
        title=title[:255],
        message=message,
        data=data,
        priority=priority,
        read=False,
        delivery_status=delivery_status,
        retry_count=0,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def list_notifications(
    db: Session,
    owner: Owner,
    *,
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False,
) -> tuple[list[Notification], int, int]:
    """Return (items, total, unread_count) for the owner."""
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    q = db.query(Notification).filter(Notification.owner_id == owner.id)
    unread_count = (
        db.query(Notification)
        .filter(Notification.owner_id == owner.id, Notification.read.is_(False))
        .count()
    )
    if unread_only:
        q = q.filter(Notification.read.is_(False))
    total = q.count()
    items = q.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    return items, total, unread_count


def get_owner_notification(db: Session, owner: Owner, notification_id: uuid.UUID) -> Notification:
    notif = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.owner_id == owner.id)
        .first()
    )
    if notif is None:
        raise NotFoundError("Notification not found")
    return notif


def mark_read(db: Session, owner: Owner, notification_id: uuid.UUID) -> Notification:
    notif = get_owner_notification(db, owner, notification_id)
    notif.read = True
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def mark_all_read(db: Session, owner: Owner) -> int:
    updated = (
        db.query(Notification)
        .filter(Notification.owner_id == owner.id, Notification.read.is_(False))
        .update({Notification.read: True}, synchronize_session=False)
    )
    db.commit()
    return int(updated)


def delete_notification(db: Session, owner: Owner, notification_id: uuid.UUID) -> None:
    notif = get_owner_notification(db, owner, notification_id)
    db.delete(notif)
    db.commit()


def get_pushover_config(db: Session, owner_id: uuid.UUID) -> PushoverConfig | None:
    return db.query(PushoverConfig).filter(PushoverConfig.owner_id == owner_id).first()


def upsert_pushover_config(
    db: Session,
    owner: Owner,
    *,
    user_key: str,
    device: str | None = None,
    sound: str = "pushover",
    enabled: bool = True,
    settings: Settings | None = None,
) -> PushoverConfig:
    key = (user_key or "").strip()
    if len(key) < 8:
        raise ValidationError(
            "Pushover user key is too short",
            details={"field": "user_key"},
        )
    encrypted = encrypt_secret(key, settings=settings)
    row = get_pushover_config(db, owner.id)
    if row is None:
        row = PushoverConfig(
            owner_id=owner.id,
            user_key_encrypted=encrypted,
            device=device,
            sound=sound or "pushover",
            enabled=enabled,
            preferences={
                "global_push_enabled": True,
                "types": dict(DEFAULT_TYPE_PREFS),
            },
        )
    else:
        row.user_key_encrypted = encrypted
        row.device = device
        row.sound = sound or "pushover"
        row.enabled = enabled
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def delete_pushover_config(db: Session, owner: Owner) -> None:
    row = get_pushover_config(db, owner.id)
    if row is None:
        raise NotFoundError("Pushover is not configured")
    db.delete(row)
    db.commit()


def pushover_status_dict(
    db: Session, owner: Owner, *, settings: Settings | None = None
) -> dict[str, Any]:
    row = get_pushover_config(db, owner.id)
    if row is None:
        return {
            "configured": False,
            "enabled": False,
            "device": None,
            "sound": None,
            "user_key_masked": None,
        }
    try:
        plain = decrypt_secret(row.user_key_encrypted, settings=settings)
        masked = mask_user_key(plain)
    except Exception:  # noqa: BLE001
        masked = "****"
    return {
        "configured": True,
        "enabled": bool(row.enabled),
        "device": row.device,
        "sound": row.sound,
        "user_key_masked": masked,
    }


def get_preferences(db: Session, owner: Owner) -> dict[str, Any]:
    row = get_pushover_config(db, owner.id)
    if row is None or not row.preferences:
        return {
            "global_push_enabled": True,
            "types": dict(DEFAULT_TYPE_PREFS),
        }
    prefs = dict(row.preferences)
    types = dict(DEFAULT_TYPE_PREFS)
    raw_types = prefs.get("types") or {}
    if isinstance(raw_types, dict):
        for k, v in raw_types.items():
            types[str(k)] = bool(v)
    return {
        "global_push_enabled": bool(prefs.get("global_push_enabled", True)),
        "types": types,
    }


def update_preferences(
    db: Session,
    owner: Owner,
    *,
    global_push_enabled: bool | None = None,
    types: dict[str, bool] | None = None,
) -> dict[str, Any]:
    """Update prefs; requires an existing PushoverConfig (create shell if needed)."""
    row = get_pushover_config(db, owner.id)
    if row is None:
        # Preferences without user key: store placeholder encrypted empty? Prefer require setup.
        raise ValidationError(
            "Configure Pushover before setting preferences",
            details={"hint": "PUT /notifications/me/pushover first"},
        )
    current = get_preferences(db, owner)
    if global_push_enabled is not None:
        current["global_push_enabled"] = global_push_enabled
    if types is not None:
        merged = dict(current["types"])
        for k, v in types.items():
            merged[str(k)] = bool(v)
        current["types"] = merged
    row.preferences = current
    db.add(row)
    db.commit()
    db.refresh(row)
    return get_preferences(db, owner)


def is_push_enabled_for_type(db: Session, owner_id: uuid.UUID, notif_type: str) -> bool:
    row = get_pushover_config(db, owner_id)
    if row is None or not row.enabled:
        return False
    prefs = row.preferences or {}
    if prefs.get("global_push_enabled") is False:
        return False
    types = prefs.get("types") or {}
    if isinstance(types, dict) and notif_type in types:
        return bool(types[notif_type])
    return DEFAULT_TYPE_PREFS.get(notif_type, True)


def notification_to_dict(n: Notification) -> dict[str, Any]:
    return {
        "id": n.id,
        "type": n.type,
        "title": n.title,
        "message": n.message,
        "data": n.data,
        "priority": n.priority,
        "read": n.read,
        "delivery_status": n.delivery_status,
        "retry_count": n.retry_count,
        "created_at": n.created_at,
        "sent_at": n.sent_at,
    }

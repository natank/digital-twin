"""Notification HTTP routes — owner-scoped in-app + Pushover setup."""

from __future__ import annotations

import uuid

from backend_shared.schemas import ApiResponse
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import get_current_owner, get_db
from src.db.models import Owner
from src.notifications.events import notify_test
from src.notifications.schemas import (
    NotificationListResponse,
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate,
    NotificationResponse,
    PushoverConfigResponse,
    PushoverConfigUpdateRequest,
    TestNotificationResponse,
    UnreadCountResponse,
)
from src.notifications.service import (
    delete_notification,
    delete_pushover_config,
    get_owner_notification,
    get_preferences,
    list_notifications,
    mark_all_read,
    mark_read,
    notification_to_dict,
    pushover_status_dict,
    update_preferences,
    upsert_pushover_config,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/status")
def notifications_module_status() -> dict[str, str]:
    """Lightweight marker that the notifications module router is mounted."""
    return {"module": "notifications", "status": "ready"}


@router.get("/me", response_model=ApiResponse[NotificationListResponse])
def list_my_notifications(
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    unread_only: bool = Query(default=False),
) -> ApiResponse[NotificationListResponse]:
    """Paginated notification list for the authenticated owner."""
    items, total, unread = list_notifications(
        db, owner, limit=limit, offset=offset, unread_only=unread_only
    )
    return ApiResponse.ok(
        NotificationListResponse(
            items=[NotificationResponse.model_validate(notification_to_dict(n)) for n in items],
            total=total,
            limit=limit,
            offset=offset,
            unread_count=unread,
        )
    )


@router.get("/me/unread-count", response_model=ApiResponse[UnreadCountResponse])
def unread_count(
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[UnreadCountResponse]:
    _, _, unread = list_notifications(db, owner, limit=1, offset=0)
    return ApiResponse.ok(UnreadCountResponse(unread_count=unread))


@router.post(
    "/me/{notification_id}/read",
    response_model=ApiResponse[NotificationResponse],
)
def read_notification(
    notification_id: uuid.UUID,
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[NotificationResponse]:
    notif = mark_read(db, owner, notification_id)
    return ApiResponse.ok(NotificationResponse.model_validate(notification_to_dict(notif)))


@router.post("/me/read-all", response_model=ApiResponse[dict[str, int]])
def read_all(
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[dict[str, int]]:
    count = mark_all_read(db, owner)
    return ApiResponse.ok({"marked_read": count})


@router.delete("/me/{notification_id}", response_model=ApiResponse[dict[str, str]])
def remove_notification(
    notification_id: uuid.UUID,
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[dict[str, str]]:
    delete_notification(db, owner, notification_id)
    return ApiResponse.ok({"status": "deleted", "id": str(notification_id)})


@router.get("/me/pushover", response_model=ApiResponse[PushoverConfigResponse])
def get_pushover(
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[PushoverConfigResponse]:
    return ApiResponse.ok(PushoverConfigResponse.model_validate(pushover_status_dict(db, owner)))


@router.put("/me/pushover", response_model=ApiResponse[PushoverConfigResponse])
def put_pushover(
    body: PushoverConfigUpdateRequest,
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[PushoverConfigResponse]:
    upsert_pushover_config(
        db,
        owner,
        user_key=body.user_key,
        device=body.device,
        sound=body.sound,
        enabled=body.enabled,
    )
    return ApiResponse.ok(PushoverConfigResponse.model_validate(pushover_status_dict(db, owner)))


@router.delete("/me/pushover", response_model=ApiResponse[dict[str, str]])
def remove_pushover(
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[dict[str, str]]:
    delete_pushover_config(db, owner)
    return ApiResponse.ok({"status": "deleted"})


@router.get(
    "/me/preferences",
    response_model=ApiResponse[NotificationPreferencesResponse],
)
def get_prefs(
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[NotificationPreferencesResponse]:
    return ApiResponse.ok(
        NotificationPreferencesResponse.model_validate(get_preferences(db, owner))
    )


@router.put(
    "/me/preferences",
    response_model=ApiResponse[NotificationPreferencesResponse],
)
def put_prefs(
    body: NotificationPreferencesUpdate,
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[NotificationPreferencesResponse]:
    prefs = update_preferences(
        db,
        owner,
        global_push_enabled=body.global_push_enabled,
        types=body.types,
    )
    return ApiResponse.ok(NotificationPreferencesResponse.model_validate(prefs))


@router.post("/me/test", response_model=ApiResponse[TestNotificationResponse])
def test_notification(
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[TestNotificationResponse]:
    """Send a test notification (requires Pushover config)."""
    from src.notifications.service import get_pushover_config
    from backend_shared.exceptions import ValidationError

    if get_pushover_config(db, owner.id) is None:
        raise ValidationError(
            "Configure Pushover before sending a test notification",
            details={"hint": "PUT /notifications/me/pushover"},
        )
    notif_id = notify_test(owner.id, db=db)
    if notif_id is None:
        raise ValidationError("Failed to create test notification")

    # Refresh delivery status after eager Celery run
    db.expire_all()
    notif = get_owner_notification(db, owner, notif_id)
    return ApiResponse.ok(
        TestNotificationResponse(
            notification_id=notif.id,
            delivery_status=notif.delivery_status,
            message="Test notification created",
        )
    )

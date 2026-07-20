"""Pydantic schemas for the notifications module."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from backend_shared.schemas import BaseSchema
from pydantic import Field

# Canonical notification type strings
NOTIF_CONVERSATION_STARTED = "conversation_started"
NOTIF_HIGH_INTENT = "high_intent_detected"
NOTIF_PROFILE_SUMMARY_READY = "profile_summary_ready"
NOTIF_ERROR = "error_occurred"
NOTIF_TEST = "test"

DEFAULT_TYPE_PREFS: dict[str, bool] = {
    NOTIF_CONVERSATION_STARTED: True,
    NOTIF_HIGH_INTENT: True,
    NOTIF_PROFILE_SUMMARY_READY: True,
    NOTIF_ERROR: True,
    NOTIF_TEST: True,
}


class NotificationResponse(BaseSchema):
    id: uuid.UUID
    type: str
    title: str
    message: str
    data: dict[str, Any] | None = None
    priority: int = 0
    read: bool = False
    delivery_status: str
    retry_count: int = 0
    created_at: datetime | None = None
    sent_at: datetime | None = None


class NotificationListResponse(BaseSchema):
    items: list[NotificationResponse]
    total: int
    limit: int
    offset: int
    unread_count: int


class UnreadCountResponse(BaseSchema):
    unread_count: int


class PushoverConfigUpdateRequest(BaseSchema):
    user_key: str = Field(min_length=8, max_length=128)
    device: str | None = Field(default=None, max_length=128)
    sound: str = Field(default="pushover", max_length=64)
    enabled: bool = True


class PushoverConfigResponse(BaseSchema):
    configured: bool
    enabled: bool = False
    device: str | None = None
    sound: str | None = None
    user_key_masked: str | None = None


class NotificationPreferencesUpdate(BaseSchema):
    global_push_enabled: bool | None = None
    types: dict[str, bool] | None = None


class NotificationPreferencesResponse(BaseSchema):
    global_push_enabled: bool = True
    types: dict[str, bool] = Field(default_factory=lambda: dict(DEFAULT_TYPE_PREFS))


class TestNotificationResponse(BaseSchema):
    notification_id: uuid.UUID
    delivery_status: str
    message: str

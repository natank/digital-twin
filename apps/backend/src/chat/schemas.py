"""Pydantic schemas for the chat module."""

from __future__ import annotations

import uuid
from datetime import datetime

from backend_shared.schemas import BaseSchema
from pydantic import Field


class CreateSessionRequest(BaseSchema):
    owner_id: uuid.UUID
    visitor_ip: str | None = Field(default=None, max_length=64)


class ChatSessionResponse(BaseSchema):
    session_id: str
    owner_id: uuid.UUID
    expires_at: datetime
    created_at: datetime | None = None
    owner_headline: str | None = None
    owner_first_name: str | None = None
    flagged: bool = False


class SendMessageRequest(BaseSchema):
    content: str = Field(min_length=1, max_length=10_000)


class MessageResponse(BaseSchema):
    id: uuid.UUID
    sender: str
    content: str
    tokens_used: int | None = None
    created_at: datetime | None = None


class SendMessageResponse(BaseSchema):
    visitor_message: MessageResponse
    reply: MessageResponse
    session_id: str
    expires_at: datetime
    boundary_redirect: bool = False


class MessageListResponse(BaseSchema):
    session_id: str
    messages: list[MessageResponse]


class OwnerConversationSummary(BaseSchema):
    """Owner dashboard row for a visitor chat session."""

    session_id: str
    created_at: datetime | None = None
    expires_at: datetime | None = None
    flagged: bool = False
    flag_reason: str | None = None
    message_count: int = 0
    preview: str | None = None
    last_message_at: datetime | None = None


class OwnerConversationListResponse(BaseSchema):
    items: list[OwnerConversationSummary]
    total: int
    limit: int
    offset: int


class OwnerConversationDetailResponse(BaseSchema):
    session_id: str
    created_at: datetime | None = None
    expires_at: datetime | None = None
    flagged: bool = False
    flag_reason: str | None = None
    messages: list[MessageResponse]

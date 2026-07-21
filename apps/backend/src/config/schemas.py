"""Pydantic schemas for the config module."""

from __future__ import annotations

import uuid
from datetime import datetime

from backend_shared.schemas import BaseSchema
from pydantic import Field


class ConfigUpdateRequest(BaseSchema):
    """Partial update of owner twin configuration (PR-006)."""

    system_prompt: str | None = Field(default=None, min_length=1, max_length=20_000)
    tone: str | None = Field(default=None, max_length=32)
    response_length: str | None = Field(default=None, max_length=32)
    allowed_topics: list[str] | None = None
    forbidden_topics: list[str] | None = None
    brand_guidelines: str | None = Field(default=None, max_length=10_000)


class ConfigResponse(BaseSchema):
    id: uuid.UUID
    owner_id: uuid.UUID
    system_prompt: str
    tone: str
    response_length: str
    allowed_topics: list[str] | None = None
    forbidden_topics: list[str] | None = None
    brand_guidelines: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SystemPromptUpdateRequest(BaseSchema):
    system_prompt: str = Field(min_length=1, max_length=20_000)


class SystemPromptResponse(BaseSchema):
    system_prompt: str
    version_number: int | None = None


class PromptVersionResponse(BaseSchema):
    version_number: int
    system_prompt: str
    created_at: datetime | None = None


class PromptVersionListResponse(BaseSchema):
    versions: list[PromptVersionResponse]


class PromptPreviewRequest(BaseSchema):
    system_prompt: str = Field(min_length=1, max_length=20_000)
    sample_question: str = Field(min_length=1, max_length=2000)


class PromptPreviewResponse(BaseSchema):
    rendered_system_prompt: str
    sample_reply: str


class ToneUpdateRequest(BaseSchema):
    tone: str = Field(min_length=1, max_length=32)


class StyleUpdateRequest(BaseSchema):
    response_length: str = Field(min_length=1, max_length=32)


class TopicsUpdateRequest(BaseSchema):
    allowed_topics: list[str] | None = None
    forbidden_topics: list[str] | None = None

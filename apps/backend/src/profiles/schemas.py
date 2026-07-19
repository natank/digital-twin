"""Pydantic request/response models for the profiles module."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from backend_shared.schemas import BaseSchema
from pydantic import Field


class ProfileUpdateRequest(BaseSchema):
    """Owner-editable profile fields (partial update via PUT)."""

    bio: str | None = Field(default=None, max_length=10_000)
    headline: str | None = Field(default=None, max_length=255)
    skills: list[str] | None = None
    experience_years: int | None = Field(default=None, ge=0, le=80)


class ProfileResponse(BaseSchema):
    """Owner-facing profile (excludes large/PII extracted CV text)."""

    id: uuid.UUID
    owner_id: uuid.UUID
    bio: str | None = None
    headline: str | None = None
    skills: list[str] | None = None
    experience_years: int | None = None
    profile_summary: dict[str, Any] | None = None
    has_cv: bool = False
    has_extracted_text: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PublicProfileResponse(BaseSchema):
    """Limited public view for chat visitors (no CV paths or full bio dumps)."""

    owner_id: uuid.UUID
    headline: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    skills: list[str] | None = None
    experience_years: int | None = None


class ProfileSummaryUpdateRequest(BaseSchema):
    """Owner edit of the structured AI-generated summary."""

    profile_summary: dict[str, Any] = Field(min_length=1)
    skills: list[str] | None = None
    experience_years: int | None = Field(default=None, ge=0, le=80)


class ProfileSummaryResponse(BaseSchema):
    profile_summary: dict[str, Any] | None = None
    skills: list[str] | None = None
    experience_years: int | None = None


class CVUploadResponse(BaseSchema):
    cv_file_path: str
    filename: str
    content_type: str
    size_bytes: int


class CVDownloadResponse(BaseSchema):
    """Presigned URL for temporary CV download."""

    url: str
    expires_in_seconds: int
    cv_file_path: str


class CVJobResponse(BaseSchema):
    id: uuid.UUID
    owner_id: uuid.UUID
    status: str
    cv_file_path: str
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

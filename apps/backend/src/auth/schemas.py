"""Pydantic request/response models for the auth module."""

from __future__ import annotations

import uuid
from datetime import datetime

from backend_shared.schemas import BaseSchema
from pydantic import EmailStr, Field


class RegisterRequest(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class OwnerPublic(BaseSchema):
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    is_active: bool
    email_verified: bool
    oauth_provider: str | None = None
    created_at: datetime | None = None


class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    owner: OwnerPublic

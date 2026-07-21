"""Config domain services: get-or-create, update, defaults."""

from __future__ import annotations

from typing import Any

from backend_shared.exceptions import ValidationError
from sqlalchemy.orm import Session

from src.chat.prompts import DEFAULT_SYSTEM_PROMPT
from src.config.defaults import (
    DEFAULT_RESPONSE_LENGTH,
    DEFAULT_TONE,
    RESPONSE_LENGTHS,
    TONES,
)
from src.db.models import DigitalTwinConfig, Owner, PromptVersion
from src.settings import Settings, get_settings


def _validate_tone(tone: str) -> str:
    t = tone.strip().lower()
    if t not in TONES:
        raise ValidationError(
            f"Invalid tone. Allowed: {', '.join(sorted(TONES))}",
            details={"field": "tone", "allowed": sorted(TONES)},
        )
    return t


def _validate_response_length(value: str) -> str:
    v = value.strip().lower()
    if v not in RESPONSE_LENGTHS:
        raise ValidationError(
            f"Invalid response_length. Allowed: {', '.join(sorted(RESPONSE_LENGTHS))}",
            details={"field": "response_length", "allowed": sorted(RESPONSE_LENGTHS)},
        )
    return v


def _clean_topics(topics: list[str] | None, *, field: str) -> list[str] | None:
    if topics is None:
        return None
    cleaned: list[str] = []
    for t in topics:
        if not isinstance(t, str):
            raise ValidationError(f"{field} must be a list of strings")
        s = t.strip()
        if not s:
            continue
        if len(s) > 100:
            raise ValidationError(
                "Topic too long (max 100 chars)",
                details={"field": field},
            )
        cleaned.append(s)
    if len(cleaned) > 50:
        raise ValidationError(
            "Too many topics (max 50)",
            details={"field": field},
        )
    return cleaned


def get_or_create_config(db: Session, owner: Owner) -> DigitalTwinConfig:
    """Return owner's config, creating defaults + version 1 if missing."""
    row = db.query(DigitalTwinConfig).filter(DigitalTwinConfig.owner_id == owner.id).first()
    if row is not None:
        return row

    row = DigitalTwinConfig(
        owner_id=owner.id,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        tone=DEFAULT_TONE,
        response_length=DEFAULT_RESPONSE_LENGTH,
        allowed_topics=[],
        forbidden_topics=[],
        brand_guidelines=None,
    )
    db.add(row)
    db.flush()
    version = PromptVersion(
        config_id=row.id,
        system_prompt=row.system_prompt,
        version_number=1,
    )
    db.add(version)
    db.commit()
    db.refresh(row)
    return row


def update_config(
    db: Session,
    owner: Owner,
    *,
    system_prompt: str | None = None,
    tone: str | None = None,
    response_length: str | None = None,
    allowed_topics: list[str] | None = None,
    forbidden_topics: list[str] | None = None,
    brand_guidelines: str | None = None,
    fields_set: set[str] | None = None,
    settings: Settings | None = None,
) -> DigitalTwinConfig:
    """Partial update; creating a prompt version when system_prompt changes."""
    cfg = settings or get_settings()
    max_chars = cfg.config_system_prompt_max_chars
    row = get_or_create_config(db, owner)
    set_fields = fields_set or set()

    if "system_prompt" in set_fields or system_prompt is not None:
        if system_prompt is None or not str(system_prompt).strip():
            raise ValidationError(
                "system_prompt must be non-empty",
                details={"field": "system_prompt"},
            )
        text = str(system_prompt).strip()
        if len(text) > max_chars:
            raise ValidationError(
                f"system_prompt exceeds maximum of {max_chars} characters",
                details={"field": "system_prompt", "max": max_chars},
            )
        if text != row.system_prompt:
            row.system_prompt = text
            _append_prompt_version(db, row)

    if "tone" in set_fields or tone is not None:
        if tone is None:
            raise ValidationError("tone cannot be null", details={"field": "tone"})
        row.tone = _validate_tone(tone)

    if "response_length" in set_fields or response_length is not None:
        if response_length is None:
            raise ValidationError(
                "response_length cannot be null",
                details={"field": "response_length"},
            )
        row.response_length = _validate_response_length(response_length)

    if "allowed_topics" in set_fields or allowed_topics is not None:
        row.allowed_topics = _clean_topics(allowed_topics, field="allowed_topics") or []

    if "forbidden_topics" in set_fields or forbidden_topics is not None:
        row.forbidden_topics = _clean_topics(forbidden_topics, field="forbidden_topics") or []

    if "brand_guidelines" in set_fields:
        row.brand_guidelines = brand_guidelines

    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _append_prompt_version(db: Session, config: DigitalTwinConfig) -> PromptVersion:
    latest = (
        db.query(PromptVersion)
        .filter(PromptVersion.config_id == config.id)
        .order_by(PromptVersion.version_number.desc())
        .first()
    )
    next_num = (latest.version_number + 1) if latest else 1
    version = PromptVersion(
        config_id=config.id,
        system_prompt=config.system_prompt,
        version_number=next_num,
    )
    db.add(version)
    return version


def list_prompt_versions(db: Session, owner: Owner) -> list[PromptVersion]:
    row = get_or_create_config(db, owner)
    return (
        db.query(PromptVersion)
        .filter(PromptVersion.config_id == row.id)
        .order_by(PromptVersion.version_number.desc())
        .all()
    )


def restore_prompt_version(db: Session, owner: Owner, version_number: int) -> DigitalTwinConfig:
    row = get_or_create_config(db, owner)
    version = (
        db.query(PromptVersion)
        .filter(
            PromptVersion.config_id == row.id,
            PromptVersion.version_number == version_number,
        )
        .first()
    )
    if version is None:
        from backend_shared.exceptions import NotFoundError

        raise NotFoundError(f"Prompt version {version_number} not found")
    if version.system_prompt != row.system_prompt:
        row.system_prompt = version.system_prompt
        _append_prompt_version(db, row)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def config_to_dict(row: DigitalTwinConfig) -> dict[str, Any]:
    return {
        "id": row.id,
        "owner_id": row.owner_id,
        "system_prompt": row.system_prompt,
        "tone": row.tone,
        "response_length": row.response_length,
        "allowed_topics": row.allowed_topics,
        "forbidden_topics": row.forbidden_topics,
        "brand_guidelines": row.brand_guidelines,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def current_version_number(db: Session, config: DigitalTwinConfig) -> int | None:
    latest = (
        db.query(PromptVersion)
        .filter(PromptVersion.config_id == config.id)
        .order_by(PromptVersion.version_number.desc())
        .first()
    )
    return latest.version_number if latest else None

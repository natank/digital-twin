"""Profile domain services: CRUD, auto-create, public limited view, CV storage."""

from __future__ import annotations

import uuid
from typing import Any, BinaryIO

from backend_shared.exceptions import NotFoundError, ValidationError
from sqlalchemy.orm import Session

from src.db.models import Owner, Profile
from src.profiles.storage import (
    StoredObject,
    delete_object,
    parse_s3_key,
    presigned_get_url,
    upload_cv,
)
from src.settings import Settings, get_settings


def get_or_create_profile(db: Session, owner: Owner) -> Profile:
    """Return the owner's profile, creating an empty row if missing."""
    if owner.profile is not None:
        return owner.profile

    profile = db.query(Profile).filter(Profile.owner_id == owner.id).first()
    if profile is not None:
        return profile

    profile = Profile(owner_id=owner.id)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_profile_for_owner(db: Session, owner: Owner) -> Profile:
    """Get the authenticated owner's profile (auto-create if needed)."""
    return get_or_create_profile(db, owner)


def update_profile(
    db: Session,
    owner: Owner,
    *,
    bio: str | None = None,
    headline: str | None = None,
    skills: list[str] | None = None,
    experience_years: int | None = None,
    fields_set: set[str] | None = None,
) -> Profile:
    """Update owner profile fields.

    When ``fields_set`` is provided (from Pydantic ``model_fields_set``), only
    those keys are written so explicit nulls can clear values.
    """
    profile = get_or_create_profile(db, owner)
    set_fields = fields_set or {
        name
        for name, value in (
            ("bio", bio),
            ("headline", headline),
            ("skills", skills),
            ("experience_years", experience_years),
        )
        if value is not None
    }

    if "bio" in set_fields:
        profile.bio = bio
    if "headline" in set_fields:
        profile.headline = headline
    if "skills" in set_fields:
        if skills is not None:
            cleaned = [s.strip() for s in skills if isinstance(s, str) and s.strip()]
            if len(cleaned) > 100:
                raise ValidationError(
                    "Too many skills (max 100)",
                    details={"field": "skills"},
                )
            profile.skills = cleaned
        else:
            profile.skills = None
    if "experience_years" in set_fields:
        profile.experience_years = experience_years

    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_public_profile(db: Session, owner_id: uuid.UUID) -> tuple[Owner, Profile]:
    """Load a limited public profile for an active owner."""
    owner = db.query(Owner).filter(Owner.id == owner_id).first()
    if owner is None or not owner.is_active:
        raise NotFoundError("Owner not found", error_code="NOT_FOUND_001")

    profile = get_or_create_profile(db, owner)
    return owner, profile


def update_profile_summary(
    db: Session,
    owner: Owner,
    *,
    profile_summary: dict[str, Any],
    skills: list[str] | None = None,
    experience_years: int | None = None,
    fields_set: set[str] | None = None,
) -> Profile:
    """Owner-edited structured summary (and optional skills/years)."""
    if not isinstance(profile_summary, dict) or not profile_summary:
        raise ValidationError(
            "profile_summary must be a non-empty object",
            details={"field": "profile_summary"},
        )

    profile = get_or_create_profile(db, owner)
    profile.profile_summary = profile_summary

    set_fields = fields_set or set()
    if "skills" in set_fields or skills is not None:
        if skills is not None:
            profile.skills = [s.strip() for s in skills if s and s.strip()]
        elif "skills" in set_fields:
            profile.skills = None
    if "experience_years" in set_fields or experience_years is not None:
        profile.experience_years = experience_years

    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def profile_to_response_dict(profile: Profile) -> dict[str, Any]:
    """Map ORM profile to API response fields (no raw CV text)."""
    return {
        "id": profile.id,
        "owner_id": profile.owner_id,
        "bio": profile.bio,
        "headline": profile.headline,
        "skills": profile.skills,
        "experience_years": profile.experience_years,
        "profile_summary": profile.profile_summary,
        "has_cv": bool(profile.cv_file_path),
        "has_extracted_text": bool(profile.cv_extracted_text),
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
    }


def store_owner_cv(
    db: Session,
    owner: Owner,
    *,
    filename: str,
    content_type: str | None,
    body: bytes | BinaryIO,
    size: int | None = None,
) -> tuple[Profile, StoredObject]:
    """Upload CV to object storage and persist path on the profile."""
    profile = get_or_create_profile(db, owner)
    previous = profile.cv_file_path

    stored = upload_cv(
        owner_id=owner.id,
        filename=filename,
        content_type=content_type,
        body=body,
        size=size,
    )

    # New upload invalidates prior extraction until re-processed.
    profile.cv_file_path = stored.s3_uri
    profile.cv_extracted_text = None
    db.add(profile)
    db.commit()
    db.refresh(profile)

    if previous:
        try:
            old_key = parse_s3_key(previous)
            if old_key != stored.key:
                delete_object(old_key)
        except Exception:  # noqa: BLE001 — best-effort cleanup
            pass

    return profile, stored


def get_cv_download_url(
    db: Session,
    owner: Owner,
    *,
    expires_in: int = 3600,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Return a presigned URL for the owner's current CV."""
    profile = get_or_create_profile(db, owner)
    if not profile.cv_file_path:
        raise NotFoundError("No CV uploaded for this profile")

    cfg = settings or get_settings()
    key = parse_s3_key(profile.cv_file_path, cfg.s3_bucket)
    url = presigned_get_url(key, expires_in=expires_in)
    return {
        "url": url,
        "expires_in_seconds": expires_in,
        "cv_file_path": profile.cv_file_path,
    }

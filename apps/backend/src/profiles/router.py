"""Profile HTTP routes — owner-scoped CRUD and public limited view."""

from __future__ import annotations

import uuid

from backend_shared.schemas import ApiResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_owner, get_db
from src.db.models import Owner
from src.profiles.schemas import (
    ProfileResponse,
    ProfileUpdateRequest,
    PublicProfileResponse,
)
from src.profiles.service import (
    get_profile_for_owner,
    get_public_profile,
    profile_to_response_dict,
    update_profile,
)

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("/status")
def profiles_module_status() -> dict[str, str]:
    """Lightweight marker that the profiles module router is mounted."""
    return {"module": "profiles", "status": "ready"}


@router.get("/me", response_model=ApiResponse[ProfileResponse])
def get_my_profile(
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[ProfileResponse]:
    """Return the authenticated owner's profile (auto-created if missing)."""
    profile = get_profile_for_owner(db, owner)
    return ApiResponse.ok(ProfileResponse.model_validate(profile_to_response_dict(profile)))


@router.put("/me", response_model=ApiResponse[ProfileResponse])
def put_my_profile(
    body: ProfileUpdateRequest,
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[ProfileResponse]:
    """Update bio, headline, skills, and experience_years for the owner."""
    profile = update_profile(
        db,
        owner,
        bio=body.bio,
        headline=body.headline,
        skills=body.skills,
        experience_years=body.experience_years,
        fields_set=set(body.model_fields_set),
    )
    return ApiResponse.ok(ProfileResponse.model_validate(profile_to_response_dict(profile)))


@router.get("/{owner_id}", response_model=ApiResponse[PublicProfileResponse])
def get_public_profile_route(
    owner_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> ApiResponse[PublicProfileResponse]:
    """Public limited profile for chat visitors (no auth required)."""
    owner, profile = get_public_profile(db, owner_id)
    return ApiResponse.ok(
        PublicProfileResponse(
            owner_id=owner.id,
            headline=profile.headline,
            first_name=owner.first_name,
            last_name=owner.last_name,
            skills=profile.skills,
            experience_years=profile.experience_years,
        )
    )

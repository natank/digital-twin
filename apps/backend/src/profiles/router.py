"""Profile HTTP routes — owner-scoped CRUD, CV upload, public limited view."""

from __future__ import annotations

import uuid

from backend_shared.schemas import ApiResponse
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from src.api.deps import get_current_owner, get_db
from src.db.models import Owner
from src.profiles.schemas import (
    CVDownloadResponse,
    CVJobResponse,
    CVUploadResponse,
    ProfileResponse,
    ProfileUpdateRequest,
    PublicProfileResponse,
)
from src.profiles.service import (
    enqueue_cv_processing,
    get_cv_download_url,
    get_cv_job,
    get_profile_for_owner,
    get_public_profile,
    profile_to_response_dict,
    store_owner_cv,
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


@router.post("/me/cv", response_model=ApiResponse[CVUploadResponse], status_code=201)
async def upload_my_cv(
    file: UploadFile = File(...),
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[CVUploadResponse]:
    """Upload a PDF/DOCX CV to S3-compatible storage (LocalStack in dev).

    Alias of PRD ``POST /profiles/cv/upload`` using owner-scoped ``/me``.
    """
    raw = await file.read()
    _profile, stored = store_owner_cv(
        db,
        owner,
        filename=file.filename or "upload.bin",
        content_type=file.content_type,
        body=raw,
        size=len(raw),
    )
    return ApiResponse.ok(
        CVUploadResponse(
            cv_file_path=stored.s3_uri,
            filename=stored.original_filename,
            content_type=stored.content_type,
            size_bytes=stored.size_bytes,
        )
    )


@router.get("/me/cv", response_model=ApiResponse[CVDownloadResponse])
def get_my_cv(
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[CVDownloadResponse]:
    """Return a presigned URL to download the owner's current CV."""
    payload = get_cv_download_url(db, owner)
    return ApiResponse.ok(CVDownloadResponse.model_validate(payload))


@router.post("/me/process-cv", response_model=ApiResponse[CVJobResponse], status_code=202)
def process_my_cv(
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[CVJobResponse]:
    """Enqueue async CV text extraction for the owner's uploaded CV."""
    job = enqueue_cv_processing(db, owner, generate_summary=False)
    return ApiResponse.ok(
        CVJobResponse(
            id=job.id,
            owner_id=job.owner_id,
            status=job.status,
            cv_file_path=job.cv_file_path,
            error_message=job.error_message,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )
    )


@router.get("/me/cv/jobs/{job_id}", response_model=ApiResponse[CVJobResponse])
def get_my_cv_job(
    job_id: uuid.UUID,
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[CVJobResponse]:
    """Return status for a CV processing job owned by the current user."""
    job = get_cv_job(db, owner, job_id)
    return ApiResponse.ok(
        CVJobResponse(
            id=job.id,
            owner_id=job.owner_id,
            status=job.status,
            cv_file_path=job.cv_file_path,
            error_message=job.error_message,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )
    )


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

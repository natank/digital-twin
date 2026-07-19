"""Auth HTTP routes (register, login, me)."""

from __future__ import annotations

from backend_shared.schemas import ApiResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_owner, get_db
from src.auth.schemas import LoginRequest, OwnerPublic, RegisterRequest, TokenResponse
from src.auth.service import authenticate_owner, create_owner_session, register_owner
from src.db.models import Owner

router = APIRouter(prefix="/auth", tags=["Auth"])


def _owner_public(owner: Owner) -> OwnerPublic:
    return OwnerPublic(
        id=owner.id,
        email=owner.email,
        first_name=owner.first_name,
        last_name=owner.last_name,
        is_active=owner.is_active,
        email_verified=owner.email_verified,
        oauth_provider=owner.oauth_provider,
        created_at=owner.created_at,
    )


@router.get("/status")
def auth_module_status() -> dict[str, str]:
    """Lightweight marker that the auth module router is mounted."""
    return {"module": "auth", "status": "ready"}


@router.post("/register", response_model=ApiResponse[OwnerPublic], status_code=201)
def register(
    body: RegisterRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[OwnerPublic]:
    """Register a new owner with email/password."""
    owner = register_owner(
        db,
        email=body.email,
        password=body.password,
        first_name=body.first_name,
        last_name=body.last_name,
    )
    return ApiResponse.ok(_owner_public(owner))


@router.post("/login", response_model=ApiResponse[TokenResponse])
def login(
    body: LoginRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    """Authenticate and issue a JWT access token."""
    owner = authenticate_owner(db, email=body.email, password=body.password)
    token, expires_at, _session = create_owner_session(db, owner)
    return ApiResponse.ok(
        TokenResponse(
            access_token=token,
            expires_at=expires_at,
            owner=_owner_public(owner),
        )
    )


@router.get("/me", response_model=ApiResponse[OwnerPublic])
def me(owner: Owner = Depends(get_current_owner)) -> ApiResponse[OwnerPublic]:
    """Return the currently authenticated owner."""
    return ApiResponse.ok(_owner_public(owner))

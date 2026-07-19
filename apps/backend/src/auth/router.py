"""Auth HTTP routes (register, login, me, logout, refresh)."""

from __future__ import annotations

from backend_shared.exceptions import AuthenticationError
from backend_shared.schemas import ApiResponse
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.api.deps import get_current_owner, get_db
from src.auth.rate_limit import get_login_rate_limiter
from src.auth.schemas import LoginRequest, OwnerPublic, RegisterRequest, TokenResponse
from src.auth.service import (
    authenticate_owner,
    create_owner_session,
    refresh_owner_session,
    register_owner,
    resolve_session_for_token,
    revoke_session,
)
from src.db.models import Owner

router = APIRouter(prefix="/auth", tags=["Auth"])
_bearer = HTTPBearer(auto_error=False)


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
    limiter = get_login_rate_limiter()
    limiter.assert_allowed(body.email)
    try:
        owner = authenticate_owner(db, email=body.email, password=body.password)
    except AuthenticationError:
        limiter.record_failure(body.email)
        raise
    limiter.clear(body.email)
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


@router.post("/logout", response_model=ApiResponse[dict[str, str]])
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> ApiResponse[dict[str, str]]:
    """Invalidate the current session."""
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Not authenticated")
    _owner, session = resolve_session_for_token(db, credentials.credentials)
    revoke_session(db, session)
    return ApiResponse.ok({"detail": "logged_out"})


@router.post("/refresh-token", response_model=ApiResponse[TokenResponse])
def refresh_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    """Rotate the access token for a still-valid session."""
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Not authenticated")
    token, expires_at, owner = refresh_owner_session(db, credentials.credentials)
    return ApiResponse.ok(
        TokenResponse(
            access_token=token,
            expires_at=expires_at,
            owner=_owner_public(owner),
        )
    )

"""OAuth provider skeleton (Google / GitHub).

Phase 1 implements token-in exchange endpoints suitable for SPA or mobile
clients that already obtained an access token from the provider. Full browser
redirect UX lands with the Phase 3 frontend.
"""

from __future__ import annotations

import secrets
from typing import Any, Protocol

import httpx
from backend_shared.exceptions import (
    AuthenticationError,
    ConflictError,
    ExternalServiceError,
    ValidationError,
)
from sqlalchemy.orm import Session

from src.auth.security import hash_password
from src.db.models import Owner, Profile
from src.settings import Settings, get_settings


class OAuthProfile(dict[str, Any]):
    """Normalized provider profile: email, sub, name parts."""


class OAuthUserInfoClient(Protocol):
    def fetch_google(self, access_token: str) -> OAuthProfile: ...

    def fetch_github(self, access_token: str) -> OAuthProfile: ...


class HttpOAuthUserInfoClient:
    """Fetch user profiles from Google/GitHub using an access token."""

    def fetch_google(self, access_token: str) -> OAuthProfile:
        try:
            response = httpx.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceError("Failed to fetch Google profile") from exc
        data = response.json()
        email = data.get("email")
        if not email:
            raise AuthenticationError("Google account did not return an email")
        return OAuthProfile(
            email=str(email).lower(),
            sub=str(data.get("sub") or ""),
            first_name=str(data.get("given_name") or "Google"),
            last_name=str(data.get("family_name") or "User"),
            email_verified=bool(data.get("email_verified", False)),
        )

    def fetch_github(self, access_token: str) -> OAuthProfile:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "digital-twin-backend",
        }
        try:
            user_resp = httpx.get(
                "https://api.github.com/user",
                headers=headers,
                timeout=10.0,
            )
            user_resp.raise_for_status()
            user = user_resp.json()
            email = user.get("email")
            if not email:
                emails_resp = httpx.get(
                    "https://api.github.com/user/emails",
                    headers=headers,
                    timeout=10.0,
                )
                emails_resp.raise_for_status()
                emails = emails_resp.json()
                primary = next(
                    (e for e in emails if e.get("primary") and e.get("verified")),
                    None,
                )
                email = (primary or (emails[0] if emails else {})).get("email")
        except httpx.HTTPError as exc:
            raise ExternalServiceError("Failed to fetch GitHub profile") from exc
        if not email:
            raise AuthenticationError("GitHub account did not return an email")
        name = str(user.get("name") or user.get("login") or "GitHub User")
        parts = name.split(None, 1)
        return OAuthProfile(
            email=str(email).lower(),
            sub=str(user.get("id") or ""),
            first_name=parts[0],
            last_name=parts[1] if len(parts) > 1 else "User",
            email_verified=True,
        )


_client: OAuthUserInfoClient | None = None


def get_oauth_client() -> OAuthUserInfoClient:
    global _client
    if _client is None:
        _client = HttpOAuthUserInfoClient()
    return _client


def set_oauth_client(client: OAuthUserInfoClient | None) -> None:
    global _client
    _client = client


def ensure_oauth_configured(provider: str, settings: Settings | None = None) -> None:
    """Raise ExternalServiceError (503-ish) when OAuth secrets are missing."""
    cfg = settings or get_settings()
    if provider == "google":
        if not cfg.google_oauth_client_id or not cfg.google_oauth_client_secret:
            raise ExternalServiceError(
                "Google OAuth is not configured",
                error_code="EXTERNAL_001",
                details={"provider": "google"},
            )
    elif provider == "github":
        if not cfg.github_oauth_client_id or not cfg.github_oauth_client_secret:
            raise ExternalServiceError(
                "GitHub OAuth is not configured",
                error_code="EXTERNAL_001",
                details={"provider": "github"},
            )
    else:
        raise ValidationError(f"Unknown OAuth provider: {provider}")


def upsert_oauth_owner(
    db: Session,
    *,
    provider: str,
    profile: OAuthProfile,
) -> Owner:
    """Find or create an owner from an OAuth profile.

    Linking when an email already exists with a password account is deferred;
    we reject with ConflictError to avoid silent account takeover.
    """
    oauth_id = str(profile.get("sub") or "")
    email = str(profile.get("email") or "").lower()
    if not oauth_id or not email:
        raise AuthenticationError("OAuth profile incomplete")

    by_oauth = (
        db.query(Owner).filter(Owner.oauth_provider == provider, Owner.oauth_id == oauth_id).first()
    )
    if by_oauth is not None:
        return by_oauth

    by_email = db.query(Owner).filter(Owner.email == email).first()
    if by_email is not None:
        raise ConflictError(
            "An account with this email already exists; account linking is not yet supported"
        )

    owner = Owner(
        email=email,
        # Unusable random hash — password login disabled unless later set.
        password_hash=hash_password(secrets.token_urlsafe(32)),
        first_name=str(profile.get("first_name") or "User"),
        last_name=str(profile.get("last_name") or "User"),
        is_active=True,
        email_verified=bool(profile.get("email_verified", True)),
        oauth_provider=provider,
        oauth_id=oauth_id,
    )
    owner.profile = Profile()
    db.add(owner)
    db.commit()
    db.refresh(owner)
    return owner

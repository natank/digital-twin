"""Pushover HTTP client (injectable for tests)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import httpx
from backend_shared.exceptions import ExternalServiceError, ValidationError
from backend_shared.logging import get_logger

from src.settings import Settings, get_settings

logger = get_logger(__name__)


@dataclass(frozen=True)
class PushoverSendResult:
    ok: bool
    status_code: int
    receipt: str | None = None
    raw: dict[str, Any] | None = None
    error: str | None = None


class PushoverClient(Protocol):
    def send(
        self,
        *,
        user_key: str,
        message: str,
        title: str,
        priority: int = 0,
        device: str | None = None,
        sound: str = "pushover",
    ) -> PushoverSendResult: ...


class HttpPushoverClient:
    """Live Pushover API client using httpx."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def send(
        self,
        *,
        user_key: str,
        message: str,
        title: str,
        priority: int = 0,
        device: str | None = None,
        sound: str = "pushover",
    ) -> PushoverSendResult:
        token = (self._settings.pushover_app_token or "").strip()
        if not token or token in {"test-token", "changeme", "sk-test"}:
            raise ExternalServiceError(
                "Pushover app token is not configured",
                details={"hint": "Set PUSHOVER_APP_TOKEN"},
            )
        if not user_key.strip():
            raise ValidationError("Pushover user key is required")

        payload: dict[str, Any] = {
            "token": token,
            "user": user_key.strip(),
            "message": message[:1024],
            "title": title[:250],
            "priority": int(priority),
            "sound": sound or "pushover",
        }
        if device:
            payload["device"] = device
        # Emergency priority requires retry/expire per Pushover docs.
        if int(priority) == 2:
            payload["retry"] = 60
            payload["expire"] = 3600

        url = self._settings.pushover_api_url
        timeout = self._settings.pushover_timeout_seconds
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, data=payload)
        except httpx.HTTPError as exc:
            logger.exception("Pushover request failed")
            return PushoverSendResult(ok=False, status_code=0, error=f"network error: {exc}")

        try:
            body = response.json()
        except Exception:  # noqa: BLE001
            body = {}

        if response.status_code >= 500:
            return PushoverSendResult(
                ok=False,
                status_code=response.status_code,
                raw=body if isinstance(body, dict) else None,
                error=f"Pushover HTTP {response.status_code}",
            )

        if response.status_code >= 400 or (isinstance(body, dict) and body.get("status") != 1):
            errs = body.get("errors") if isinstance(body, dict) else None
            return PushoverSendResult(
                ok=False,
                status_code=response.status_code,
                raw=body if isinstance(body, dict) else None,
                error=str(errs or body or f"HTTP {response.status_code}")[:500],
            )

        receipt = None
        if isinstance(body, dict):
            receipt = body.get("receipt") or body.get("request")
            if receipt is not None:
                receipt = str(receipt)
        return PushoverSendResult(
            ok=True,
            status_code=response.status_code,
            receipt=receipt,
            raw=body if isinstance(body, dict) else None,
        )


class FakePushoverClient:
    """In-memory fake for unit tests."""

    def __init__(self, *, fail_times: int = 0) -> None:
        self.fail_times = fail_times
        self.calls: list[dict[str, Any]] = []
        self._failures_left = fail_times

    def send(
        self,
        *,
        user_key: str,
        message: str,
        title: str,
        priority: int = 0,
        device: str | None = None,
        sound: str = "pushover",
    ) -> PushoverSendResult:
        self.calls.append(
            {
                "user_key": user_key,
                "message": message,
                "title": title,
                "priority": priority,
                "device": device,
                "sound": sound,
            }
        )
        if self._failures_left > 0:
            self._failures_left -= 1
            return PushoverSendResult(ok=False, status_code=500, error="simulated failure")
        return PushoverSendResult(ok=True, status_code=200, receipt="fake-receipt-1")


_client: PushoverClient | None = None


def get_pushover_client() -> PushoverClient:
    global _client
    if _client is None:
        _client = HttpPushoverClient()
    return _client


def set_pushover_client(client: PushoverClient | None) -> None:
    """Install a test double (None restores default on next get)."""
    global _client
    _client = client

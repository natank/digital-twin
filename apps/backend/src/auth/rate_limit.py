"""Login rate limiting (Redis with in-process fallback)."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass

from backend_shared.exceptions import RateLimitError
from backend_shared.logging import get_logger

from src.settings import Settings, get_settings

logger = get_logger(__name__)


@dataclass
class _MemoryBucket:
    count: int
    reset_at: float


class LoginRateLimiter:
    """Track failed login attempts per email key.

    Prefers Redis when available; falls back to a process-local dict so
    local/dev tests keep working without Redis.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._memory: dict[str, _MemoryBucket] = {}
        self._lock = threading.Lock()
        self._redis = None
        try:
            import redis

            client = redis.Redis.from_url(self._settings.redis_url, decode_responses=True)
            client.ping()
            self._redis = client
        except Exception:  # noqa: BLE001 — intentional soft fallback
            logger.debug("Redis unavailable for rate limiting; using in-memory store")
            self._redis = None

    def _key(self, email: str) -> str:
        return f"auth:login_fail:{email.strip().lower()}"

    def assert_allowed(self, email: str) -> None:
        """Raise RateLimitError if the key is currently locked out."""
        max_attempts = self._settings.auth_login_max_attempts
        window = self._settings.auth_login_lockout_seconds
        key = self._key(email)

        if self._redis is not None:
            try:
                raw = self._redis.get(key)
                count = int(raw) if raw is not None else 0  # type: ignore[arg-type]
                if count >= max_attempts:
                    raw_ttl = self._redis.ttl(key)
                    ttl = int(raw_ttl) if raw_ttl is not None else window  # type: ignore[arg-type]
                    raise RateLimitError(
                        "Too many login attempts. Try again later.",
                        details={"retry_after_seconds": max(ttl, 1)},
                    )
                return
            except RateLimitError:
                raise
            except Exception:  # noqa: BLE001
                logger.warning("Redis rate-limit check failed; falling back to memory")

        now = time.time()
        with self._lock:
            bucket = self._memory.get(key)
            if bucket is None or bucket.reset_at <= now:
                return
            if bucket.count >= max_attempts:
                raise RateLimitError(
                    "Too many login attempts. Try again later.",
                    details={"retry_after_seconds": max(int(bucket.reset_at - now), 1)},
                )

    def record_failure(self, email: str) -> None:
        """Increment the failure counter for email (does not raise)."""
        window = self._settings.auth_login_lockout_seconds
        key = self._key(email)

        if self._redis is not None:
            try:
                pipe = self._redis.pipeline()
                pipe.incr(key)
                pipe.expire(key, window)
                pipe.execute()
                return
            except Exception:  # noqa: BLE001
                logger.warning("Redis rate-limit write failed; falling back to memory")

        now = time.time()
        with self._lock:
            bucket = self._memory.get(key)
            if bucket is None or bucket.reset_at <= now:
                self._memory[key] = _MemoryBucket(count=1, reset_at=now + window)
                return
            bucket.count += 1

    def clear(self, email: str) -> None:
        """Clear counters after a successful login."""
        key = self._key(email)
        if self._redis is not None:
            try:
                self._redis.delete(key)
            except Exception:  # noqa: BLE001
                pass
        with self._lock:
            self._memory.pop(key, None)


_limiter: LoginRateLimiter | None = None


def get_login_rate_limiter() -> LoginRateLimiter:
    global _limiter
    if _limiter is None:
        _limiter = LoginRateLimiter()
    return _limiter

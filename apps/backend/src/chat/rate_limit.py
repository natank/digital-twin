"""Visitor chat rate limiting (50 requests / hour / session via Redis)."""

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


class ChatRateLimiter:
    """Track chat API calls per session public id."""

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
        except Exception:  # noqa: BLE001
            logger.debug("Redis unavailable for chat rate limiting; using in-memory store")
            self._redis = None

    def _key(self, session_public_id: str) -> str:
        return f"chat:rate:{session_public_id}"

    def assert_allowed(self, session_public_id: str) -> None:
        """Raise RateLimitError if the session exceeded its hourly budget."""
        max_req = self._settings.chat_rate_limit_per_hour
        window = self._settings.chat_rate_limit_window_seconds
        key = self._key(session_public_id)

        if self._redis is not None:
            try:
                raw = self._redis.get(key)
                count = int(raw) if raw is not None else 0  # type: ignore[arg-type]
                if count >= max_req:
                    raw_ttl = self._redis.ttl(key)
                    ttl = int(raw_ttl) if raw_ttl is not None else window  # type: ignore[arg-type]
                    raise RateLimitError(
                        "Chat rate limit exceeded. Try again later.",
                        details={"retry_after_seconds": max(ttl, 1)},
                    )
                pipe = self._redis.pipeline()
                pipe.incr(key)
                # Only set expiry on first hit in the window.
                if raw is None:
                    pipe.expire(key, window)
                pipe.execute()
                return
            except RateLimitError:
                raise
            except Exception:  # noqa: BLE001
                logger.warning("Redis chat rate-limit failed; falling back to memory")

        now = time.time()
        with self._lock:
            bucket = self._memory.get(key)
            if bucket is None or bucket.reset_at <= now:
                self._memory[key] = _MemoryBucket(count=1, reset_at=now + window)
                return
            if bucket.count >= max_req:
                raise RateLimitError(
                    "Chat rate limit exceeded. Try again later.",
                    details={"retry_after_seconds": max(int(bucket.reset_at - now), 1)},
                )
            bucket.count += 1


_limiter: ChatRateLimiter | None = None


def get_chat_rate_limiter() -> ChatRateLimiter:
    global _limiter
    if _limiter is None:
        _limiter = ChatRateLimiter()
    return _limiter

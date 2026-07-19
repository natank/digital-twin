"""Health / smoke task for verifying Celery connectivity."""

from __future__ import annotations

from datetime import datetime, timezone

from backend_shared.logging import get_logger

from src.worker.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="tasks.ping")
def ping(message: str = "pong") -> dict[str, str]:
    """Return a trivial payload so enqueue → execute can be smoke-tested."""
    logger.info("celery ping received", extra={"ping_message": message})
    return {
        "message": message,
        "ts": datetime.now(timezone.utc).isoformat(),
    }

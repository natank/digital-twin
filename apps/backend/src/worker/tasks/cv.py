"""CV processing Celery tasks (implemented fully in PR-009 / PR-010).

Registered early so the worker process imports a stable task name:
``tasks.process_cv``. The body is filled when extraction lands.
"""

from __future__ import annotations

from backend_shared.logging import get_logger

from src.worker.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="tasks.process_cv", bind=True, max_retries=2)
def process_cv(self, job_id: str) -> dict[str, str]:  # type: ignore[no-untyped-def]
    """Process an uploaded CV: extract text and (later) generate a summary.

    Placeholder until PR-009 wires extraction; raises if invoked early so
    mis-queued jobs fail loudly instead of silently succeeding.
    """
    del self  # reserved for retry binding
    logger.warning(
        "process_cv stub invoked before PR-009 implementation job_id=%s",
        job_id,
    )
    return {"job_id": job_id, "status": "not_implemented"}

"""Celery application factory.

Broker and result backend default to Redis (``CELERY_BROKER_URL`` /
``CELERY_RESULT_BACKEND``, falling back to ``REDIS_URL``).

Run a worker from ``apps/backend``:

    poetry run celery -A src.worker.celery_app.celery_app worker -l INFO

Or via Nx:

    pnpm nx run apps/backend:worker

Tests should set ``CELERY_TASK_ALWAYS_EAGER=true`` (see ``conftest.py``)
so tasks execute in-process without a live broker.
"""

from __future__ import annotations

import os

from celery import Celery
from celery.signals import setup_logging as celery_setup_logging

from src.settings import get_settings


def _broker_url() -> str:
    return os.environ.get("CELERY_BROKER_URL") or get_settings().celery_broker_url


def _result_backend() -> str:
    return os.environ.get("CELERY_RESULT_BACKEND") or get_settings().celery_result_backend


def create_celery_app() -> Celery:
    """Build and configure the Celery app used by API and workers."""
    settings = get_settings()
    app = Celery(
        "digital_twin",
        broker=_broker_url(),
        backend=_result_backend(),
        include=[
            "src.worker.tasks",
            "src.worker.tasks.ping",
            "src.worker.tasks.cv",
            "src.worker.tasks.notifications",
        ],
    )
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_default_queue="default",
        # Eager mode for tests / offline smoke (env wins).
        task_always_eager=settings.celery_task_always_eager
        or os.environ.get("CELERY_TASK_ALWAYS_EAGER", "").lower() in {"1", "true", "yes"},
        task_eager_propagates=True,
        worker_hijack_root_logger=False,
    )
    return app


celery_app = create_celery_app()


@celery_setup_logging.connect
def _configure_celery_logging(**_kwargs: object) -> None:
    """Reuse backend_shared structured logging instead of Celery's defaults."""
    from backend_shared.logging import configure_logging

    configure_logging(level=get_settings().log_level)

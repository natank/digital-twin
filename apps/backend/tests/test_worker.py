"""Celery worker infrastructure tests (Phase 1 PR-006)."""

from __future__ import annotations

from src.worker.celery_app import celery_app
from src.worker.tasks.ping import ping


def test_celery_app_configured() -> None:
    assert celery_app.main == "digital_twin"
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.task_always_eager is True


def test_ping_task_registered() -> None:
    registered = celery_app.tasks
    assert "tasks.ping" in registered


def test_ping_task_eager_execution() -> None:
    result = ping.delay(message="hello")
    payload = result.get(timeout=5)
    assert payload["message"] == "hello"
    assert "ts" in payload


def test_ping_task_direct_call() -> None:
    payload = ping(message="direct")
    assert payload["message"] == "direct"


def test_process_cv_task_registered() -> None:
    assert "tasks.process_cv" in celery_app.tasks

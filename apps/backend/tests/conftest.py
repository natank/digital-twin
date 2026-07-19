"""Shared pytest fixtures for the backend test suite."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Run Celery tasks in-process for the whole suite (no Redis broker required).
os.environ.setdefault("CELERY_TASK_ALWAYS_EAGER", "true")

from src.db.base import Base  # noqa: E402
from src.db.session import get_db  # noqa: E402
from src.main import app  # noqa: E402

# Import models so metadata is populated.
from src.db import models as _models  # noqa: E402, F401

# Ensure Celery app picks up eager mode after env is set, and tasks are imported.
from src.worker.celery_app import celery_app as _celery_app  # noqa: E402
from src.worker import tasks as _tasks  # noqa: E402, F401

_celery_app.conf.task_always_eager = True
_celery_app.conf.task_eager_propagates = True


@pytest.fixture(autouse=True)
def _default_llm_mock() -> None:  # type: ignore[misc]
    """Prevent live Anthropic calls in the suite; tests may override."""
    from src.llm.claude import set_chat_reply_generator, set_profile_summary_generator

    def _default(cv_text: str) -> dict:
        return {
            "profile_summary": {
                "headline": "Test Professional",
                "summary": f"Auto-mock summary ({len(cv_text)} chars).",
                "highlights": [],
                "skills": [],
                "experience_years": None,
            },
            "skills": [],
            "experience_years": None,
        }

    def _chat_default(system_prompt: str, messages: list) -> tuple[str, int | None]:
        last = messages[-1]["content"] if messages else ""
        return (f"Mock twin reply about: {last[:80]}", 12)

    set_profile_summary_generator(_default)
    set_chat_reply_generator(_chat_default)
    yield
    set_profile_summary_generator(None)
    set_chat_reply_generator(None)


@pytest.fixture()
def db_session() -> Session:
    """In-memory SQLite session with the full ORM schema."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # SQLite + Postgres UUID: store UUIDs as strings.
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[no-untyped-def]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """HTTP client with get_db overridden to the in-memory session.

    Also redirects ``SessionLocal`` (used by Celery tasks) at the same
    SQLite engine so eager tasks see API-created rows.
    """
    from sqlalchemy.orm import sessionmaker

    from src.db import session as session_mod

    factory = sessionmaker(bind=db_session.get_bind(), autoflush=False, autocommit=False)
    monkeypatch.setattr(session_mod, "SessionLocal", factory)

    def _override_get_db():  # type: ignore[no-untyped-def]
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

"""Tests for Phase 0 database models (Owner, OwnerSession, Profile).

Uses an in-memory SQLite engine so these run without a live Postgres
instance; the real schema is exercised via Alembic migrations against
Postgres (see docker-compose.yml + `nx run apps/backend:migrate`).
"""

import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.db.base import Base
from src.db.models import Owner, OwnerSession, Profile


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def test_create_owner(db_session: Session):
    owner = Owner(
        email="test@example.com",
        password_hash="hashed",
        first_name="Test",
        last_name="Owner",
    )
    db_session.add(owner)
    db_session.commit()

    fetched = db_session.query(Owner).filter_by(email="test@example.com").one()
    assert fetched.id is not None
    assert fetched.is_active is True
    assert fetched.email_verified is False


def test_owner_profile_relationship(db_session: Session):
    owner = Owner(
        email="profile@example.com",
        password_hash="hashed",
        first_name="Test",
        last_name="Owner",
    )
    owner.profile = Profile(headline="Engineer", skills=["Python"])
    db_session.add(owner)
    db_session.commit()

    fetched = db_session.query(Owner).filter_by(email="profile@example.com").one()
    assert fetched.profile.headline == "Engineer"
    assert fetched.profile.skills == ["Python"]


def test_owner_session_cascade_delete(db_session: Session):
    owner = Owner(
        email="session@example.com",
        password_hash="hashed",
        first_name="Test",
        last_name="Owner",
    )
    owner.sessions.append(
        OwnerSession(
            id=uuid.uuid4(),
            token="a-token",
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
    )
    db_session.add(owner)
    db_session.commit()

    db_session.delete(owner)
    db_session.commit()

    assert db_session.query(OwnerSession).count() == 0

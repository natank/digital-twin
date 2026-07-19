"""Seed the local development database with a sample owner and profile.

Usage: poetry run python scripts/seed_data.py
"""

from src.db.models import Owner, Profile
from src.db.session import SessionLocal

SEED_EMAIL = "owner@example.com"


def seed() -> None:
    """Insert a sample owner + profile if one doesn't already exist."""
    db = SessionLocal()
    try:
        existing = db.query(Owner).filter(Owner.email == SEED_EMAIL).first()
        if existing:
            print(f"Seed owner already exists: {SEED_EMAIL}")
            return

        owner = Owner(
            email=SEED_EMAIL,
            # Not a real hash — dev/seed data only, never used for login.
            password_hash="dev-seed-not-a-real-hash",
            first_name="Sample",
            last_name="Owner",
            is_active=True,
            email_verified=True,
        )
        owner.profile = Profile(
            headline="Software Engineer",
            bio="Sample seeded profile for local development.",
            skills=["Python", "TypeScript", "FastAPI"],
            experience_years=5,
        )
        db.add(owner)
        db.commit()
        print(f"Seeded owner: {SEED_EMAIL}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

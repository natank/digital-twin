"""Seed the local development database with a sample owner and profile.

Usage: poetry run python scripts/seed_data.py

Default credentials (dev only):
  email:    owner@example.com
  password: Owner123!
"""

from src.auth.security import hash_password
from src.db.models import Owner, Profile
from src.db.session import SessionLocal

SEED_EMAIL = "owner@example.com"
SEED_PASSWORD = "Owner123!"


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
            password_hash=hash_password(SEED_PASSWORD),
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
        print(f"Seeded owner: {SEED_EMAIL} (password: {SEED_PASSWORD})")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

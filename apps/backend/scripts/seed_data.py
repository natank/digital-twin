"""Seed the local development database with a sample owner and profile.

Usage: poetry run python scripts/seed_data.py

Default credentials (dev only):
  email:    owner@example.com
  password: Owner123!
"""

from src.auth.security import hash_password
from src.chat.prompts import DEFAULT_SYSTEM_PROMPT
from src.db.models import DigitalTwinConfig, Owner, Profile, PromptVersion
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
            # Ensure twin config exists for demos
            if (
                db.query(DigitalTwinConfig)
                .filter(DigitalTwinConfig.owner_id == existing.id)
                .first()
                is None
            ):
                _seed_config(db, existing)
                db.commit()
                print("Seeded DigitalTwinConfig for existing owner")
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
            profile_summary={
                "headline": "Software Engineer",
                "summary": (
                    "Sample owner used for local demos. Experienced with Python, "
                    "TypeScript, and FastAPI backends."
                ),
                "highlights": ["Built modular monolith platforms"],
                "skills": ["Python", "TypeScript", "FastAPI"],
                "experience_years": 5,
            },
            cv_extracted_text=(
                "Sample Owner\nSoftware Engineer\n"
                "Skills: Python, TypeScript, FastAPI\n"
                "Experience: 5 years building web APIs and AI assistants."
            ),
        )
        db.add(owner)
        db.flush()
        _seed_config(db, owner)
        db.commit()
        print(f"Seeded owner: {SEED_EMAIL} (password: {SEED_PASSWORD})")
        print("Seeded DigitalTwinConfig (tone=professional, sample topics)")
    finally:
        db.close()


def _seed_config(db, owner: Owner) -> None:
    cfg = DigitalTwinConfig(
        owner_id=owner.id,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        tone="professional",
        response_length="balanced",
        allowed_topics=["Python", "FastAPI", "software architecture"],
        forbidden_topics=["personal finances"],
        brand_guidelines="Mention open-source contributions when relevant.",
    )
    db.add(cfg)
    db.flush()
    db.add(
        PromptVersion(
            config_id=cfg.id,
            system_prompt=cfg.system_prompt,
            version_number=1,
        )
    )


if __name__ == "__main__":
    seed()

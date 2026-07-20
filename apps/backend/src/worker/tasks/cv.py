"""CV processing Celery tasks: extract text and (optionally) generate summary."""

from __future__ import annotations

import uuid

from backend_shared.logging import get_logger
from sqlalchemy.orm import Session

from src.worker.celery_app import celery_app

logger = get_logger(__name__)


def process_cv_job(
    db: Session,
    job_id: uuid.UUID,
    *,
    generate_summary: bool = False,
) -> dict[str, str]:
    """Run CV extraction (and optional summary) using the given DB session.

    Separated from the Celery wrapper so tests can drive the pipeline against
    the same in-memory database as the API.
    """
    from src.db.models import CVProcessingJob, Profile
    from src.profiles.extraction import extract_text
    from src.profiles.storage import download_bytes, parse_s3_key

    job = db.query(CVProcessingJob).filter(CVProcessingJob.id == job_id).first()
    if job is None:
        logger.error("cv job not found job_id=%s", job_id)
        return {"job_id": str(job_id), "status": "failed", "error": "job not found"}

    job.status = "processing"
    job.error_message = None
    db.add(job)
    db.commit()

    try:
        key = parse_s3_key(job.cv_file_path)
        raw = download_bytes(key)
        filename = key.rsplit("/", 1)[-1]
        # Strip uuid- prefix used in storage keys when present
        if "-" in filename:
            # key basename is "{uuid}-{original}"; keep original for extension sniff
            parts = filename.split("-", 5)
            if len(parts) >= 6:
                filename = parts[-1] if "." in parts[-1] else filename
            else:
                # uuid4 has 5 hyphens in str form... actually uuid is 8-4-4-4-12
                # our key is f"{uuid.uuid4()}-{filename}" so split after first 36 chars
                if len(filename) > 37 and filename[36] == "-":
                    filename = filename[37:]
        text = extract_text(raw, filename=filename)
    except Exception as exc:  # noqa: BLE001
        logger.exception("cv extraction failed job_id=%s", job_id)
        job.status = "failed"
        job.error_message = _safe_error_message(exc)
        db.add(job)
        db.commit()
        return {"job_id": str(job_id), "status": "failed", "error": job.error_message}

    job.extracted_text = text
    profile = db.query(Profile).filter(Profile.owner_id == job.owner_id).first()
    if profile is not None:
        profile.cv_extracted_text = text
        db.add(profile)

    if generate_summary and profile is not None:
        try:
            from src.llm.claude import generate_profile_summary

            summary = generate_profile_summary(text)
            profile.profile_summary = summary.get("profile_summary") or {
                k: v for k, v in summary.items() if k not in {"skills", "experience_years"}
            }
            if summary.get("skills") is not None:
                profile.skills = summary["skills"]
            if summary.get("experience_years") is not None:
                profile.experience_years = summary["experience_years"]
            db.add(profile)
        except Exception as exc:  # noqa: BLE001
            logger.exception("summary generation failed job_id=%s", job_id)
            job.error_message = f"Text extracted; summary failed: {_safe_error_message(exc)}"

    job.status = "completed"
    db.add(job)
    db.commit()

    if generate_summary and profile is not None and profile.profile_summary:
        try:
            from src.notifications.events import notify_profile_summary_ready

            notify_profile_summary_ready(job.owner_id, db=db)
        except Exception:  # noqa: BLE001
            logger.exception("summary_ready notification failed job_id=%s", job_id)

    logger.info("cv job completed job_id=%s", job_id)
    return {"job_id": str(job_id), "status": "completed"}


def _safe_error_message(exc: BaseException) -> str:
    msg = getattr(exc, "message", None) or str(exc) or exc.__class__.__name__
    return msg[:500]


def _run_process_cv(job_id: str, *, generate_summary: bool = False) -> dict[str, str]:
    """Open a DB session and run the pipeline (used by Celery workers)."""
    from src.db.session import SessionLocal

    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        logger.error("invalid job_id=%s", job_id)
        return {"job_id": job_id, "status": "failed", "error": "invalid job id"}

    db = SessionLocal()
    try:
        return process_cv_job(db, job_uuid, generate_summary=generate_summary)
    finally:
        db.close()


@celery_app.task(name="tasks.process_cv", bind=True, max_retries=2)
def process_cv(
    self: object,
    job_id: str,
    generate_summary: bool = False,
) -> dict[str, str]:
    """Process an uploaded CV: extract text; optional LLM summary (PR-010)."""
    del self
    return _run_process_cv(job_id, generate_summary=generate_summary)

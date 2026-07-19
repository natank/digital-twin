"""S3-compatible object storage for CV files (LocalStack in dev).

Encryption at rest: rely on bucket defaults in dev. Production should use
SSE-KMS / bucket policies — document when deploying (Phase 4).
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from functools import lru_cache
from typing import BinaryIO
from urllib.parse import quote

import boto3
from backend_shared.exceptions import ExternalServiceError, NotFoundError, ValidationError
from backend_shared.logging import get_logger
from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError

from src.settings import Settings, get_settings

logger = get_logger(__name__)

# Max CV size per PRD / PR-008: 10 MiB
MAX_CV_BYTES = 10 * 1024 * 1024

ALLOWED_CONTENT_TYPES: frozenset[str] = frozenset(
    {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    }
)

ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".pdf", ".docx", ".doc"})

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True)
class StoredObject:
    key: str
    bucket: str
    content_type: str
    size_bytes: int
    original_filename: str

    @property
    def s3_uri(self) -> str:
        return f"s3://{self.bucket}/{self.key}"


def _normalize_filename(filename: str) -> str:
    base = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1].strip()
    if not base:
        raise ValidationError("Filename is required", details={"field": "file"})
    cleaned = _SAFE_NAME.sub("_", base)
    if len(cleaned) > 200:
        cleaned = cleaned[-200:]
    return cleaned


def validate_cv_upload(*, filename: str, content_type: str | None, size: int) -> str:
    """Validate extension, content type, and size; return sanitized filename."""
    if size <= 0:
        raise ValidationError("Empty file", details={"field": "file"})
    if size > MAX_CV_BYTES:
        raise ValidationError(
            f"File exceeds maximum size of {MAX_CV_BYTES} bytes",
            details={"field": "file", "max_bytes": MAX_CV_BYTES, "size": size},
        )

    safe_name = _normalize_filename(filename)
    lower = safe_name.lower()
    ext = ""
    if "." in lower:
        ext = "." + lower.rsplit(".", 1)[-1]
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            "Unsupported file type. Allowed: PDF, DOCX",
            details={"field": "file", "extension": ext},
        )

    ct = (content_type or "").split(";")[0].strip().lower()
    # Browsers sometimes send application/octet-stream; trust extension then.
    if ct and ct not in ALLOWED_CONTENT_TYPES and ct != "application/octet-stream":
        raise ValidationError(
            "Unsupported content type. Allowed: PDF, DOCX",
            details={"field": "file", "content_type": ct},
        )
    return safe_name


def virus_scan_stub(filename: str, size: int) -> None:
    """Placeholder virus scan — log and skip in development."""
    logger.info(
        "virus scan skipped in dev filename=%s size=%s",
        filename,
        size,
    )


@lru_cache
def get_s3_client() -> BaseClient:
    """Return a cached boto3 S3 client configured for LocalStack or AWS."""
    settings = get_settings()
    kwargs: dict = {
        "service_name": "s3",
        "region_name": settings.aws_default_region,
        "aws_access_key_id": settings.aws_access_key_id,
        "aws_secret_access_key": settings.aws_secret_access_key,
    }
    endpoint = settings.aws_endpoint_url.strip() if settings.aws_endpoint_url else ""
    if endpoint:
        kwargs["endpoint_url"] = endpoint
    return boto3.client(**kwargs)


def ensure_bucket(client: BaseClient | None = None, settings: Settings | None = None) -> None:
    """Create the configured bucket if it does not exist (LocalStack convenience)."""
    cfg = settings or get_settings()
    s3 = client or get_s3_client()
    try:
        s3.head_bucket(Bucket=cfg.s3_bucket)
    except ClientError:
        try:
            s3.create_bucket(Bucket=cfg.s3_bucket)
            logger.info("created s3 bucket %s", cfg.s3_bucket)
        except ClientError as exc:
            # Race or already exists under a different error code.
            error_code = exc.response.get("Error", {}).get("Code", "")
            if error_code not in {"BucketAlreadyOwnedByYou", "BucketAlreadyExists"}:
                raise ExternalServiceError(
                    "Failed to ensure S3 bucket",
                    details={"bucket": cfg.s3_bucket, "code": error_code},
                ) from exc


def build_cv_key(owner_id: uuid.UUID, filename: str) -> str:
    """s3://{bucket}/cv-uploads/{owner_id}/{uuid}-{filename}"""
    return f"cv-uploads/{owner_id}/{uuid.uuid4()}-{filename}"


def upload_cv(
    *,
    owner_id: uuid.UUID,
    filename: str,
    content_type: str | None,
    body: bytes | BinaryIO,
    size: int | None = None,
    client: BaseClient | None = None,
    settings: Settings | None = None,
) -> StoredObject:
    """Validate and upload a CV object; return storage metadata."""
    cfg = settings or get_settings()
    s3 = client or get_s3_client()

    data = body if isinstance(body, (bytes, bytearray)) else body.read()
    if not isinstance(data, (bytes, bytearray)):
        raise ValidationError("Invalid file body", details={"field": "file"})
    data_bytes = bytes(data)
    byte_size = size if size is not None else len(data_bytes)
    if byte_size != len(data_bytes):
        byte_size = len(data_bytes)

    safe_name = validate_cv_upload(
        filename=filename,
        content_type=content_type,
        size=byte_size,
    )
    virus_scan_stub(safe_name, byte_size)

    ct = (content_type or "").split(";")[0].strip().lower() or "application/octet-stream"
    if ct == "application/octet-stream":
        if safe_name.lower().endswith(".pdf"):
            ct = "application/pdf"
        elif safe_name.lower().endswith(".docx"):
            ct = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    ensure_bucket(s3, cfg)
    key = build_cv_key(owner_id, safe_name)
    try:
        s3.put_object(
            Bucket=cfg.s3_bucket,
            Key=key,
            Body=data_bytes,
            ContentType=ct,
            Metadata={
                "owner_id": str(owner_id),
                "original_filename": quote(safe_name, safe="."),
            },
        )
    except (BotoCoreError, ClientError) as exc:
        logger.exception("S3 upload failed")
        raise ExternalServiceError(
            "Failed to store CV file",
            details={"bucket": cfg.s3_bucket},
        ) from exc

    return StoredObject(
        key=key,
        bucket=cfg.s3_bucket,
        content_type=ct,
        size_bytes=byte_size,
        original_filename=safe_name,
    )


def delete_object(
    key: str,
    *,
    client: BaseClient | None = None,
    settings: Settings | None = None,
) -> None:
    """Best-effort delete of a previous CV object."""
    cfg = settings or get_settings()
    s3 = client or get_s3_client()
    try:
        s3.delete_object(Bucket=cfg.s3_bucket, Key=key)
    except (BotoCoreError, ClientError):
        logger.warning("failed to delete previous CV object key=%s", key)


def download_bytes(
    key: str,
    *,
    client: BaseClient | None = None,
    settings: Settings | None = None,
) -> bytes:
    """Download object body by key."""
    cfg = settings or get_settings()
    s3 = client or get_s3_client()
    try:
        obj = s3.get_object(Bucket=cfg.s3_bucket, Key=key)
        body = obj["Body"].read()
        return bytes(body)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code in {"NoSuchKey", "404", "NotFound"}:
            raise NotFoundError("CV file not found in storage") from exc
        raise ExternalServiceError("Failed to download CV file") from exc
    except BotoCoreError as exc:
        raise ExternalServiceError("Failed to download CV file") from exc


def presigned_get_url(
    key: str,
    *,
    expires_in: int = 3600,
    client: BaseClient | None = None,
    settings: Settings | None = None,
) -> str:
    """Generate a time-limited GET URL for the CV object."""
    cfg = settings or get_settings()
    s3 = client or get_s3_client()
    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": cfg.s3_bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        return str(url)
    except (BotoCoreError, ClientError) as exc:
        raise ExternalServiceError("Failed to generate download URL") from exc


def parse_s3_key(cv_file_path: str, bucket: str | None = None) -> str:
    """Accept either a raw key or s3://bucket/key URI and return the key."""
    if cv_file_path.startswith("s3://"):
        without = cv_file_path[len("s3://") :]
        parts = without.split("/", 1)
        if len(parts) != 2 or not parts[1]:
            raise ValidationError("Invalid S3 URI for CV")
        return parts[1]
    return cv_file_path

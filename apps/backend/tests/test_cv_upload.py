"""CV upload + object storage tests (Phase 1 PR-008)."""

from __future__ import annotations

import io

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from src.profiles.storage import MAX_CV_BYTES, get_s3_client
from src.settings import get_settings

STRONG_PASSWORD = "SecurePass1!"

# Minimal valid-enough PDF header so content-type + extension checks pass.
MINI_PDF = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


def _register_login(client: TestClient, email: str) -> str:
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": STRONG_PASSWORD,
            "first_name": "C",
            "last_name": "V",
        },
    )
    login = client.post(
        "/auth/login",
        json={"email": email, "password": STRONG_PASSWORD},
    )
    assert login.status_code == 200, login.text
    return login.json()["data"]["access_token"]


@pytest.fixture()
def s3_moto(monkeypatch: pytest.MonkeyPatch):
    """moto S3 + reset cached boto3 client to use the mock.

    Clear AWS_ENDPOINT_URL so the app client does not target LocalStack
    while moto intercepts the default AWS endpoint.
    """
    monkeypatch.setenv("AWS_ENDPOINT_URL", "")
    get_settings.cache_clear()
    get_s3_client.cache_clear()
    with mock_aws():
        settings = get_settings()
        client = boto3.client(
            "s3",
            region_name=settings.aws_default_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
        client.create_bucket(Bucket=settings.s3_bucket)
        get_s3_client.cache_clear()
        yield client
        get_s3_client.cache_clear()
        get_settings.cache_clear()


def test_upload_cv_success(client: TestClient, s3_moto) -> None:
    token = _register_login(client, "cv-up@example.com")
    response = client.post(
        "/profiles/me/cv",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("resume.pdf", io.BytesIO(MINI_PDF), "application/pdf")},
    )
    assert response.status_code == 201, response.text
    data = response.json()["data"]
    assert data["filename"] == "resume.pdf"
    assert data["cv_file_path"].startswith("s3://")
    assert "cv-uploads/" in data["cv_file_path"]
    assert data["size_bytes"] == len(MINI_PDF)

    me = client.get("/profiles/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["data"]["has_cv"] is True

    # Object exists in moto bucket
    settings = get_settings()
    key = data["cv_file_path"].split(f"s3://{settings.s3_bucket}/", 1)[1]
    head = s3_moto.head_object(Bucket=settings.s3_bucket, Key=key)
    assert head["ContentLength"] == len(MINI_PDF)


def test_upload_rejects_oversize(client: TestClient, s3_moto) -> None:
    token = _register_login(client, "cv-big@example.com")
    big = b"%PDF-1.4\n" + (b"x" * (MAX_CV_BYTES + 1))
    response = client.post(
        "/profiles/me/cv",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("big.pdf", io.BytesIO(big), "application/pdf")},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_001"


def test_upload_rejects_bad_type(client: TestClient, s3_moto) -> None:
    token = _register_login(client, "cv-bad@example.com")
    response = client.post(
        "/profiles/me/cv",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 422


def test_get_cv_presigned_url(client: TestClient, s3_moto) -> None:
    token = _register_login(client, "cv-get@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    up = client.post(
        "/profiles/me/cv",
        headers=headers,
        files={"file": ("resume.pdf", io.BytesIO(MINI_PDF), "application/pdf")},
    )
    assert up.status_code == 201, up.text

    got = client.get("/profiles/me/cv", headers=headers)
    assert got.status_code == 200, got.text
    data = got.json()["data"]
    assert data["url"]
    assert data["expires_in_seconds"] == 3600
    assert data["cv_file_path"].startswith("s3://")


def test_get_cv_without_upload(client: TestClient, s3_moto) -> None:
    token = _register_login(client, "cv-none@example.com")
    response = client.get(
        "/profiles/me/cv",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_upload_requires_auth(client: TestClient) -> None:
    response = client.post(
        "/profiles/me/cv",
        files={"file": ("resume.pdf", io.BytesIO(MINI_PDF), "application/pdf")},
    )
    assert response.status_code == 401

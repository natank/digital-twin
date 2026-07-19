"""LLM profile summary tests (Phase 1 PR-010)."""

from __future__ import annotations

import io
from typing import Any

import boto3
import pytest
from docx import Document
from fastapi.testclient import TestClient
from moto import mock_aws

from src.llm.claude import (
    _normalize_summary,
    _parse_json_object,
    generate_profile_summary,
    set_profile_summary_generator,
)
from src.profiles.storage import get_s3_client
from src.settings import get_settings

STRONG_PASSWORD = "SecurePass1!"


def _docx_bytes(text: str) -> bytes:
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _register_login(client: TestClient, email: str) -> str:
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": STRONG_PASSWORD,
            "first_name": "Sum",
            "last_name": "Mary",
        },
    )
    login = client.post(
        "/auth/login",
        json={"email": email, "password": STRONG_PASSWORD},
    )
    assert login.status_code == 200, login.text
    return login.json()["data"]["access_token"]


def _mock_summary(cv_text: str) -> dict[str, Any]:
    return {
        "profile_summary": {
            "headline": "Mock Engineer",
            "summary": f"Summary from {len(cv_text)} chars of CV.",
            "highlights": ["Built digital twins"],
            "skills": ["Python", "FastAPI"],
            "experience_years": 7,
        },
        "skills": ["Python", "FastAPI"],
        "experience_years": 7,
    }


@pytest.fixture()
def mock_llm():
    set_profile_summary_generator(_mock_summary)
    yield
    set_profile_summary_generator(None)


@pytest.fixture()
def s3_moto(monkeypatch: pytest.MonkeyPatch):
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


def test_parse_json_object_plain() -> None:
    data = _parse_json_object('{"headline": "X", "skills": []}')
    assert data["headline"] == "X"


def test_parse_json_object_fenced() -> None:
    data = _parse_json_object('```json\n{"headline": "Y"}\n```')
    assert data["headline"] == "Y"


def test_normalize_summary() -> None:
    out = _normalize_summary(
        {
            "headline": "Lead Dev",
            "summary": "Does things.",
            "skills": ["Go", "Rust"],
            "experience_years": "12",
            "highlights": ["A"],
        }
    )
    assert out["skills"] == ["Go", "Rust"]
    assert out["experience_years"] == 12
    assert out["profile_summary"]["headline"] == "Lead Dev"


def test_generate_with_mock(mock_llm) -> None:
    result = generate_profile_summary("long cv text here")
    assert result["profile_summary"]["headline"] == "Mock Engineer"
    assert result["skills"] == ["Python", "FastAPI"]


def test_generate_empty_text_raises() -> None:
    with pytest.raises(Exception):
        generate_profile_summary("   ")


def test_process_cv_writes_summary(client: TestClient, s3_moto, mock_llm) -> None:
    token = _register_login(client, "sum-process@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    data = _docx_bytes("Alex Example\nStaff Engineer\nPython FastAPI")

    up = client.post(
        "/profiles/me/cv",
        headers=headers,
        files={
            "file": (
                "resume.docx",
                io.BytesIO(data),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert up.status_code == 201, up.text

    proc = client.post("/profiles/me/process-cv", headers=headers)
    assert proc.status_code == 202, proc.text
    assert proc.json()["data"]["status"] == "completed"

    summary = client.get("/profiles/me/summary", headers=headers)
    assert summary.status_code == 200, summary.text
    body = summary.json()["data"]
    assert body["profile_summary"]["headline"] == "Mock Engineer"
    assert body["skills"] == ["Python", "FastAPI"]
    assert body["experience_years"] == 7


def test_put_summary(client: TestClient, mock_llm) -> None:
    token = _register_login(client, "sum-put@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/profiles/me/summary",
        headers=headers,
        json={
            "profile_summary": {"headline": "Edited", "summary": "Owner text"},
            "skills": ["Rust"],
            "experience_years": 3,
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["profile_summary"]["headline"] == "Edited"
    assert data["skills"] == ["Rust"]
    assert data["experience_years"] == 3


def test_regenerate_requires_cv_text(client: TestClient, mock_llm) -> None:
    token = _register_login(client, "sum-regen-empty@example.com")
    response = client.post(
        "/profiles/me/summary/regenerate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_regenerate_success(client: TestClient, s3_moto, mock_llm) -> None:
    token = _register_login(client, "sum-regen@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    data = _docx_bytes("Pat Professional\nArchitect")
    client.post(
        "/profiles/me/cv",
        headers=headers,
        files={
            "file": (
                "cv.docx",
                io.BytesIO(data),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    # Process without relying on summary in process step — seed extraction only
    client.post("/profiles/me/process-cv", headers=headers)

    # Clear summary via PUT then regenerate
    client.put(
        "/profiles/me/summary",
        headers=headers,
        json={"profile_summary": {"headline": "Stale"}},
    )
    regen = client.post("/profiles/me/summary/regenerate", headers=headers)
    assert regen.status_code == 200, regen.text
    assert regen.json()["data"]["profile_summary"]["headline"] == "Mock Engineer"


def test_summary_unauthenticated(client: TestClient) -> None:
    assert client.get("/profiles/me/summary").status_code == 401

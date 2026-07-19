"""Phase 1 cross-module integration tests (PR-014).

Flow: register → login → (seed profile summary) → chat session → message → AI reply.
CV upload path is covered in test_profile_summary; here we focus on auth→chat.
"""

from __future__ import annotations

import io

import boto3
import pytest
from docx import Document
from fastapi.testclient import TestClient
from moto import mock_aws

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


def test_auth_profile_chat_e2e(client: TestClient, s3_moto) -> None:
    # 1) Register + login
    email = "e2e-owner@example.com"
    reg = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": STRONG_PASSWORD,
            "first_name": "E2E",
            "last_name": "Owner",
        },
    )
    assert reg.status_code == 201, reg.text
    owner_id = reg.json()["data"]["id"]

    login = client.post(
        "/auth/login",
        json={"email": email, "password": STRONG_PASSWORD},
    )
    assert login.status_code == 200, login.text
    token = login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2) Upload CV → process (eager) → summary present
    data = _docx_bytes("E2E Owner\nStaff Engineer\nSkills: Python, FastAPI, Chat systems")
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
    assert summary.status_code == 200
    assert summary.json()["data"]["profile_summary"] is not None

    # 3) Visitor chat session → message → AI reply
    session = client.post("/chat/sessions", json={"owner_id": owner_id})
    assert session.status_code == 201, session.text
    sid = session.json()["data"]["session_id"]

    msg = client.post(
        f"/chat/sessions/{sid}/messages",
        json={"content": "What skills do you have?"},
    )
    assert msg.status_code == 200, msg.text
    payload = msg.json()["data"]
    assert payload["visitor_message"]["content"] == "What skills do you have?"
    assert payload["reply"]["sender"] == "ai"
    assert payload["reply"]["content"]

    hist = client.get(f"/chat/sessions/{sid}/messages")
    assert len(hist.json()["data"]["messages"]) == 2

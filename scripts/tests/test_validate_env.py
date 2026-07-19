"""Unit tests for scripts/validate-env.py (no live services required)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATE_PATH = REPO_ROOT / "scripts" / "validate-env.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("validate_env", VALIDATE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_env"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def ve():
    return _load_module()


def _write_env(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_parse_env_file_strips_comments_and_quotes(ve, tmp_path: Path):
    env_path = _write_env(
        tmp_path / ".env.local",
        """
# comment
DATABASE_URL=postgresql+psycopg://u:p@localhost:5432/db
JWT_SECRET="quoted-secret"
export DEBUG=true

EMPTY_SKIP=
""".strip(),
    )
    parsed = ve.parse_env_file(env_path)
    assert parsed["DATABASE_URL"].startswith("postgresql+psycopg://")
    assert parsed["JWT_SECRET"] == "quoted-secret"
    assert parsed["DEBUG"] == "true"
    assert parsed["EMPTY_SKIP"] == ""


def test_main_passes_with_complete_env(ve, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    env_path = _write_env(
        tmp_path / ".env.local",
        """
DATABASE_URL=postgresql+psycopg://postgres:devpassword@localhost:5432/digital_twin_dev
REDIS_URL=redis://localhost:6379
JWT_SECRET=dev-secret-only-for-testing
JWT_EXPIRY=86400
DEBUG=true
LOG_LEVEL=DEBUG
S3_BUCKET=digital-twin-dev
AWS_ENDPOINT_URL=http://localhost:4566
VITE_API_URL=http://localhost:8000
CLAUDE_API_KEY=sk-test
""".strip(),
    )
    # Ensure process env does not override test file values for required keys.
    for key in ve.REQUIRED_VARS:
        monkeypatch.delenv(key, raising=False)

    code = ve.main(["--env-file", str(env_path)])
    assert code == 0


def test_main_fails_when_file_missing(ve, tmp_path: Path):
    missing = tmp_path / "does-not-exist.env"
    code = ve.main(["--env-file", str(missing)])
    assert code == 1


def test_main_fails_on_bad_database_url(ve, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    env_path = _write_env(
        tmp_path / ".env.local",
        """
DATABASE_URL=not-a-url
REDIS_URL=redis://localhost:6379
JWT_SECRET=dev-secret-only-for-testing
JWT_EXPIRY=86400
DEBUG=true
LOG_LEVEL=DEBUG
S3_BUCKET=digital-twin-dev
AWS_ENDPOINT_URL=http://localhost:4566
VITE_API_URL=http://localhost:8000
""".strip(),
    )
    for key in ve.REQUIRED_VARS:
        monkeypatch.delenv(key, raising=False)

    code = ve.main(["--env-file", str(env_path)])
    assert code == 1


def test_settings_loads_from_repo_root_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Smoke: backend Settings still constructs with defaults when no file is forced."""
    # Import from installed backend package path by adding apps/backend to sys.path.
    backend_root = REPO_ROOT / "apps" / "backend"
    sys.path.insert(0, str(backend_root))
    try:
        from src.settings import Settings

        # Clear any cached get_settings side effects by constructing Settings directly.
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("REDIS_URL", raising=False)
        settings = Settings()
        assert "postgresql" in settings.database_url
        assert settings.redis_url.startswith("redis://")
    finally:
        if str(backend_root) in sys.path:
            sys.path.remove(str(backend_root))

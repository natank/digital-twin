#!/usr/bin/env python3
"""Validate local development environment configuration.

Checks that ``.env.local`` exists (or can be derived from the process
environment), that required variables are present and well-formed, and
optionally that infrastructure services are reachable.

Usage:
    python3 scripts/validate-env.py
    python3 scripts/validate-env.py --check-services
    python3 scripts/validate-env.py --env-file /path/to/.env.local

Exit codes:
    0  — all required checks passed
    1  — one or more required checks failed
"""

from __future__ import annotations

import argparse
import os
import re
import socket
import sys
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENV_FILE = REPO_ROOT / ".env.local"
EXAMPLE_ENV_FILE = REPO_ROOT / ".env.example"

# Variables that must be set (non-empty) for local development.
REQUIRED_VARS: tuple[str, ...] = (
    "DATABASE_URL",
    "REDIS_URL",
    "JWT_SECRET",
    "JWT_EXPIRY",
    "DEBUG",
    "LOG_LEVEL",
    "S3_BUCKET",
    "AWS_ENDPOINT_URL",
    "VITE_API_URL",
)

# Variables that may be empty placeholders in Phase 0 but must still appear.
OPTIONAL_VARS: tuple[str, ...] = (
    "CLAUDE_API_KEY",
    "PUSHOVER_APP_TOKEN",
    "ENCRYPTION_KEY",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_DEFAULT_REGION",
    "VITE_DEBUG",
    "PYTHONUNBUFFERED",
)

# Values that are unsafe outside of local development.
INSECURE_JWT_SECRETS: frozenset[str] = frozenset(
    {
        "dev-secret-only-for-testing",
        "dev-secret-key-change-in-production",
        "changeme",
        "secret",
        "your-secret-key-here",
    }
)


class CheckResult:
    """Collects pass/fail/warn messages for a validation run."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.ok: list[str] = []

    def pass_(self, message: str) -> None:
        self.ok.append(message)

    def fail(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    @property
    def success(self) -> bool:
        return not self.errors


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a simple KEY=VALUE env file (no shell expansion)."""
    values: dict[str, str] = {}
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            raise ValueError(f"{path}:{lineno}: expected KEY=VALUE, got: {raw!r}")
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip matching single/double quotes.
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key] = value
    return values


def load_env(env_file: Path | None) -> tuple[dict[str, str], Path | None]:
    """Merge env-file values with process environment (process wins)."""
    file_values: dict[str, str] = {}
    used_file: Path | None = None
    if env_file is not None and env_file.is_file():
        file_values = parse_env_file(env_file)
        used_file = env_file
    merged = {**file_values, **{k: v for k, v in os.environ.items() if k in REQUIRED_VARS + OPTIONAL_VARS or k in file_values}}
    # Prefer process env for every key that is set there.
    for key in list(file_values) + list(REQUIRED_VARS) + list(OPTIONAL_VARS):
        if key in os.environ:
            merged[key] = os.environ[key]
    return merged, used_file


def _is_url_with_scheme(value: str, schemes: Iterable[str]) -> bool:
    try:
        parsed = urlparse(value)
    except Exception:
        return False
    return parsed.scheme in schemes and bool(parsed.netloc or parsed.path)


def validate_required(env: dict[str, str], result: CheckResult) -> None:
    for key in REQUIRED_VARS:
        value = env.get(key)
        if value is None or value.strip() == "":
            result.fail(f"Missing required variable: {key}")
        else:
            result.pass_(f"{key} is set")


def validate_optional_presence(env: dict[str, str], result: CheckResult, env_file: Path | None) -> None:
    """Warn when known optional keys are absent from the env file (not process)."""
    if env_file is None:
        return
    file_keys = set(parse_env_file(env_file))
    for key in OPTIONAL_VARS:
        if key not in file_keys and key not in os.environ:
            result.warn(f"Optional variable not present in env file: {key}")


def validate_formats(env: dict[str, str], result: CheckResult) -> None:
    database_url = env.get("DATABASE_URL", "")
    if database_url:
        if not _is_url_with_scheme(database_url, ("postgresql", "postgresql+psycopg", "postgres")):
            result.fail(
                "DATABASE_URL must be a PostgreSQL URL "
                "(e.g. postgresql+psycopg://user:pass@localhost:5432/digital_twin_dev)"
            )
        else:
            result.pass_("DATABASE_URL scheme looks valid")

    redis_url = env.get("REDIS_URL", "")
    if redis_url:
        if not _is_url_with_scheme(redis_url, ("redis", "rediss")):
            result.fail("REDIS_URL must be a redis:// or rediss:// URL")
        else:
            result.pass_("REDIS_URL scheme looks valid")

    jwt_secret = env.get("JWT_SECRET", "")
    if jwt_secret:
        if jwt_secret in INSECURE_JWT_SECRETS:
            result.warn(
                "JWT_SECRET is a known development placeholder — fine for local "
                "dev, replace before staging/production"
            )
        elif len(jwt_secret) < 16:
            result.warn("JWT_SECRET is shorter than 16 characters")
        else:
            result.pass_("JWT_SECRET is set to a non-placeholder value")

    jwt_expiry = env.get("JWT_EXPIRY", "")
    if jwt_expiry:
        if not re.fullmatch(r"\d+", jwt_expiry):
            result.fail("JWT_EXPIRY must be an integer number of seconds")
        else:
            result.pass_("JWT_EXPIRY is an integer")

    log_level = env.get("LOG_LEVEL", "")
    if log_level and log_level.upper() not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        result.fail(f"LOG_LEVEL has unexpected value: {log_level!r}")
    elif log_level:
        result.pass_("LOG_LEVEL is valid")

    debug = env.get("DEBUG", "")
    if debug and debug.lower() not in {"true", "false", "1", "0", "yes", "no"}:
        result.fail(f"DEBUG must be a boolean-like value, got: {debug!r}")
    elif debug:
        result.pass_("DEBUG is boolean-like")

    vite_api = env.get("VITE_API_URL", "")
    if vite_api:
        if not _is_url_with_scheme(vite_api, ("http", "https")):
            result.fail("VITE_API_URL must be an http(s) URL")
        else:
            result.pass_("VITE_API_URL scheme looks valid")

    aws_endpoint = env.get("AWS_ENDPOINT_URL", "")
    if aws_endpoint:
        if not _is_url_with_scheme(aws_endpoint, ("http", "https")):
            result.fail("AWS_ENDPOINT_URL must be an http(s) URL")
        else:
            result.pass_("AWS_ENDPOINT_URL scheme looks valid")


def _host_port_from_url(url: str, default_port: int) -> tuple[str, int] | None:
    try:
        parsed = urlparse(url)
    except Exception:
        return None
    host = parsed.hostname
    if not host:
        return None
    port = parsed.port or default_port
    return host, port


def _can_connect(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def check_services(env: dict[str, str], result: CheckResult) -> None:
    """Best-effort TCP reachability checks for local infrastructure."""
    database_url = env.get("DATABASE_URL", "")
    redis_url = env.get("REDIS_URL", "")
    aws_endpoint = env.get("AWS_ENDPOINT_URL", "")

    checks: list[tuple[str, str, int]] = []
    if database_url:
        hp = _host_port_from_url(database_url, 5432)
        if hp:
            checks.append(("PostgreSQL", *hp))
    if redis_url:
        hp = _host_port_from_url(redis_url, 6379)
        if hp:
            checks.append(("Redis", *hp))
    if aws_endpoint:
        hp = _host_port_from_url(aws_endpoint, 4566)
        if hp:
            checks.append(("LocalStack", *hp))

    for name, host, port in checks:
        if _can_connect(host, port):
            result.pass_(f"{name} is reachable at {host}:{port}")
        else:
            result.fail(f"{name} is not reachable at {host}:{port}")


def print_report(result: CheckResult, env_file: Path | None) -> None:
    print("=== Environment validation ===")
    if env_file is not None:
        print(f"Env file: {env_file}")
    else:
        print("Env file: (none — using process environment only)")
    print()

    for message in result.ok:
        print(f"  OK   {message}")
    for message in result.warnings:
        print(f"  WARN {message}")
    for message in result.errors:
        print(f"  FAIL {message}")

    print()
    if result.success:
        print("Result: PASSED" + (" with warnings" if result.warnings else ""))
    else:
        print(f"Result: FAILED ({len(result.errors)} error(s))")
        if not (DEFAULT_ENV_FILE.is_file() or env_file):
            print()
            print(f"Hint: copy the template and re-run:")
            print(f"  cp {EXAMPLE_ENV_FILE.relative_to(REPO_ROOT)} .env.local")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--env-file",
        type=Path,
        default=DEFAULT_ENV_FILE,
        help=f"Path to env file (default: {DEFAULT_ENV_FILE})",
    )
    parser.add_argument(
        "--check-services",
        action="store_true",
        help="Also check that Postgres, Redis, and LocalStack are reachable",
    )
    parser.add_argument(
        "--allow-missing-file",
        action="store_true",
        help="Do not fail if the env file is missing (use process env only)",
    )
    args = parser.parse_args(argv)

    result = CheckResult()
    env_file: Path | None = args.env_file

    if not env_file.is_file():
        if args.allow_missing_file:
            result.warn(f"Env file not found: {env_file}")
            env_file = None
        else:
            result.fail(f"Env file not found: {env_file}")
            if EXAMPLE_ENV_FILE.is_file():
                result.warn(f"Create one with: cp {EXAMPLE_ENV_FILE} {args.env_file}")
            print_report(result, None)
            return 1

    try:
        env, used_file = load_env(env_file)
    except ValueError as exc:
        result.fail(str(exc))
        print_report(result, env_file)
        return 1

    validate_required(env, result)
    validate_optional_presence(env, result, used_file)
    validate_formats(env, result)

    if args.check_services:
        check_services(env, result)

    print_report(result, used_file)
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())

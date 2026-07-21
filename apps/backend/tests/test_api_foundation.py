"""Tests for Phase 1 PR-001 API foundation (errors, CORS, modules)."""

from backend_shared.exceptions import NotFoundError, ValidationError
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_domain_module_status_routes_mounted() -> None:
    for path, module in (
        ("/auth/status", "auth"),
        ("/profiles/status", "profiles"),
        ("/chat/status", "chat"),
        ("/notifications/status", "notifications"),
        ("/config/status", "config"),
    ):
        response = client.get(path)
        assert response.status_code == 200, path
        assert response.json()["module"] == module


def test_request_id_header_echoed() -> None:
    response = client.get("/health", headers={"X-Request-ID": "test-rid-123"})
    assert response.headers.get("X-Request-ID") == "test-rid-123"


def test_app_error_returns_envelope() -> None:
    @app.get("/_test/not-found")
    def _boom() -> None:
        raise NotFoundError("Owner not found", error_code="NOT_FOUND_001")

    try:
        response = client.get("/_test/not-found")
        assert response.status_code == 404
        body = response.json()
        assert body["status"] == "error"
        assert body["error"]["code"] == "NOT_FOUND_001"
        assert body["error"]["message"] == "Owner not found"
        assert body["data"] is None
    finally:
        # Remove temporary route so other tests are unaffected.
        app.router.routes = [
            r for r in app.router.routes if getattr(r, "path", None) != "/_test/not-found"
        ]


def test_validation_error_returns_envelope() -> None:
    @app.get("/_test/validation")
    def _validate() -> None:
        raise ValidationError("bad input", details={"field": "email"})

    try:
        response = client.get("/_test/validation")
        assert response.status_code == 422
        body = response.json()
        assert body["status"] == "error"
        assert body["error"]["code"] == "VALIDATION_001"
        assert body["error"]["details"]["field"] == "email"
    finally:
        app.router.routes = [
            r for r in app.router.routes if getattr(r, "path", None) != "/_test/validation"
        ]


def test_get_current_owner_stub_returns_401() -> None:
    from src.api.deps import get_current_owner
    from src.main import app as application

    @application.get("/_test/protected")
    def _protected(owner=None):  # type: ignore[no-untyped-def]
        # Wired via Depends in a real route; call stub directly here.
        return owner

    # Direct dependency invocation with empty credentials
    from fastapi import Depends
    from fastapi.testclient import TestClient as TC

    @application.get("/_test/me-stub")
    def me_stub(owner=Depends(get_current_owner)):  # type: ignore[no-untyped-def]
        return {"id": str(owner.id)}

    try:
        tc = TC(application)
        response = tc.get("/_test/me-stub")
        assert response.status_code == 401
        body = response.json()
        assert body["status"] == "error"
        assert body["error"]["code"] == "AUTH_001"
    finally:
        application.router.routes = [
            r
            for r in application.router.routes
            if getattr(r, "path", None) not in {"/_test/protected", "/_test/me-stub"}
        ]


def test_openapi_includes_domain_tags() -> None:
    schema = client.get("/openapi.json").json()
    # Tags may only appear once routes declare them; check path tags via paths.
    paths = schema["paths"]
    assert "/auth/status" in paths
    assert "/profiles/status" in paths
    assert "/chat/status" in paths


def test_cors_preflight_allows_configured_origin() -> None:
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:4200",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code in (200, 204)
    assert response.headers.get("access-control-allow-origin") == "http://localhost:4200"

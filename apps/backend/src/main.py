"""FastAPI application entrypoint."""

from backend_shared.logging import configure_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.router import api_router
from src.core.errors import register_exception_handlers
from src.core.middleware import RequestIdMiddleware
from src.settings import get_settings

settings = get_settings()
configure_logging(level=settings.log_level)

app = FastAPI(
    title="Digital Twin API",
    version="0.1.0",
    description="API for the Digital Twin AI Assistant platform (modular monolith).",
)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

register_exception_handlers(app)
app.include_router(api_router)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Basic liveness check for local dev and container orchestration."""
    return {"status": "healthy"}

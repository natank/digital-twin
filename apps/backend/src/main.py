"""FastAPI application entrypoint."""

from fastapi import FastAPI

app = FastAPI(title="Digital Twin API")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Basic liveness check for local dev and container orchestration."""
    return {"status": "healthy"}

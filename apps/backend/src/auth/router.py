"""Auth HTTP routes — shell for PR-001; endpoints land in PR-002+."""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/status", include_in_schema=True)
def auth_module_status() -> dict[str, str]:
    """Lightweight marker that the auth module router is mounted."""
    return {"module": "auth", "status": "ready"}

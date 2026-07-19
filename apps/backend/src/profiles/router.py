"""Profile HTTP routes — shell for PR-001; endpoints land in PR-007+."""

from fastapi import APIRouter

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("/status")
def profiles_module_status() -> dict[str, str]:
    """Lightweight marker that the profiles module router is mounted."""
    return {"module": "profiles", "status": "ready"}

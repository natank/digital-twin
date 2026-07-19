"""Chat HTTP routes — shell for PR-001; endpoints land in PR-011+."""

from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/status")
def chat_module_status() -> dict[str, str]:
    """Lightweight marker that the chat module router is mounted."""
    return {"module": "chat", "status": "ready"}

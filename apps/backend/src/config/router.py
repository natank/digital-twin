"""Config HTTP routes — owner-scoped twin configuration."""

from __future__ import annotations

from backend_shared.schemas import ApiResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_owner, get_db
from src.config.schemas import ConfigResponse, ConfigUpdateRequest
from src.config.service import config_to_dict, get_or_create_config, update_config
from src.db.models import Owner

router = APIRouter(prefix="/config", tags=["Config"])


@router.get("/status")
def config_module_status() -> dict[str, str]:
    """Lightweight marker that the config module router is mounted."""
    return {"module": "config", "status": "ready"}


@router.get("/me", response_model=ApiResponse[ConfigResponse])
def get_my_config(
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[ConfigResponse]:
    """Return the owner's twin config (auto-created with defaults if missing)."""
    row = get_or_create_config(db, owner)
    return ApiResponse.ok(ConfigResponse.model_validate(config_to_dict(row)))


@router.put("/me", response_model=ApiResponse[ConfigResponse])
def put_my_config(
    body: ConfigUpdateRequest,
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[ConfigResponse]:
    """Partial update of tone, length, topics, prompt, brand guidelines."""
    row = update_config(
        db,
        owner,
        system_prompt=body.system_prompt,
        tone=body.tone,
        response_length=body.response_length,
        allowed_topics=body.allowed_topics,
        forbidden_topics=body.forbidden_topics,
        brand_guidelines=body.brand_guidelines,
        fields_set=set(body.model_fields_set),
    )
    return ApiResponse.ok(ConfigResponse.model_validate(config_to_dict(row)))

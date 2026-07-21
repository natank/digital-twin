"""Config HTTP routes — owner-scoped twin configuration."""

from __future__ import annotations

from backend_shared.schemas import ApiResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_owner, get_db
from src.chat.prompts import format_profile_summary
from src.config.schemas import (
    ConfigResponse,
    ConfigUpdateRequest,
    PromptPreviewRequest,
    PromptPreviewResponse,
    PromptVersionListResponse,
    PromptVersionResponse,
    SystemPromptResponse,
    SystemPromptUpdateRequest,
)
from src.config.service import (
    config_to_dict,
    current_version_number,
    get_or_create_config,
    list_prompt_versions,
    restore_prompt_version,
    update_config,
)
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


@router.get("/me/system-prompt", response_model=ApiResponse[SystemPromptResponse])
def get_system_prompt(
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[SystemPromptResponse]:
    """Return current system prompt template and latest version number."""
    row = get_or_create_config(db, owner)
    return ApiResponse.ok(
        SystemPromptResponse(
            system_prompt=row.system_prompt,
            version_number=current_version_number(db, row),
        )
    )


@router.put("/me/system-prompt", response_model=ApiResponse[SystemPromptResponse])
def put_system_prompt(
    body: SystemPromptUpdateRequest,
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[SystemPromptResponse]:
    """Update system prompt template; appends a new PromptVersion."""
    row = update_config(
        db,
        owner,
        system_prompt=body.system_prompt,
        fields_set={"system_prompt"},
    )
    return ApiResponse.ok(
        SystemPromptResponse(
            system_prompt=row.system_prompt,
            version_number=current_version_number(db, row),
        )
    )


@router.get(
    "/me/system-prompt/versions",
    response_model=ApiResponse[PromptVersionListResponse],
)
def get_prompt_versions(
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[PromptVersionListResponse]:
    """List prompt history newest-first."""
    versions = list_prompt_versions(db, owner)
    return ApiResponse.ok(
        PromptVersionListResponse(
            versions=[
                PromptVersionResponse(
                    version_number=v.version_number,
                    system_prompt=v.system_prompt,
                    created_at=v.created_at,
                )
                for v in versions
            ]
        )
    )


@router.post(
    "/me/system-prompt/restore/{version_number}",
    response_model=ApiResponse[SystemPromptResponse],
)
def restore_version(
    version_number: int,
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[SystemPromptResponse]:
    """Restore a historical prompt (creates a new version with that content)."""
    row = restore_prompt_version(db, owner, version_number)
    return ApiResponse.ok(
        SystemPromptResponse(
            system_prompt=row.system_prompt,
            version_number=current_version_number(db, row),
        )
    )


@router.post(
    "/me/system-prompt/preview",
    response_model=ApiResponse[PromptPreviewResponse],
)
def preview_prompt(
    body: PromptPreviewRequest,
    owner: Owner = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiResponse[PromptPreviewResponse]:
    """Render placeholders and sample a reply (mocked LLM in CI)."""
    from src.llm.claude import generate_chat_reply

    profile = owner.profile
    owner_name = f"{owner.first_name} {owner.last_name}".strip() or owner.email
    summary_text = format_profile_summary(
        profile.profile_summary if profile else None,
        skills=profile.skills if profile else None,
    )
    try:
        rendered = body.system_prompt.format(
            owner_name=owner_name,
            profile_summary=summary_text,
        )
    except KeyError:
        # Unknown placeholders left intact for owner preview
        rendered = body.system_prompt.replace("{owner_name}", owner_name).replace(
            "{profile_summary}", summary_text
        )

    messages = [{"role": "user", "content": body.sample_question}]
    reply, _tokens = generate_chat_reply(
        system_prompt=rendered,
        messages=messages,
    )
    return ApiResponse.ok(
        PromptPreviewResponse(
            rendered_system_prompt=rendered,
            sample_reply=reply,
        )
    )

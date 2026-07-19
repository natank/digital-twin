"""Claude (Anthropic) client wrapper for profile summary generation.

Prompt + output schema
----------------------
System: professional résumé analyst.
User: raw CV text (truncated).
Model must return **JSON only** matching:

```json
{
  "headline": "short professional headline",
  "summary": "2-4 paragraph professional summary",
  "skills": ["skill1", "skill2"],
  "experience_years": 10,
  "highlights": ["achievement 1", "achievement 2"]
}
```

Stored on ``Profile.profile_summary`` as the full object (minus optional
skills/years which are also copied onto top-level profile columns).

Tests inject a mock via ``set_profile_summary_generator`` so CI never
calls the live Anthropic API.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from typing import Any

from backend_shared.exceptions import ExternalServiceError, ValidationError
from backend_shared.logging import get_logger

from src.settings import Settings, get_settings

logger = get_logger(__name__)

# Max CV chars sent to the model (cost/latency control).
MAX_CV_CHARS = 60_000

PROFILE_SUMMARY_SYSTEM = """You are an expert résumé analyst. Extract a structured
professional profile from the CV text. Respond with a single JSON object only
(no markdown fences, no commentary) using this schema:
{
  "headline": "string — short professional headline",
  "summary": "string — 2-4 sentence professional overview",
  "skills": ["string", "..."],
  "experience_years": <integer or null>,
  "highlights": ["string", "..."]
}
Be accurate. Do not invent employers, degrees, or skills not supported by the text.
If experience years are unclear, use null.
"""

ProfileSummaryGenerator = Callable[[str], dict[str, Any]]

_override_generator: ProfileSummaryGenerator | None = None


def set_profile_summary_generator(fn: ProfileSummaryGenerator | None) -> None:
    """Install a test double for summary generation (None restores default)."""
    global _override_generator
    _override_generator = fn


def _truncate_cv(text: str) -> str:
    if len(text) <= MAX_CV_CHARS:
        return text
    return text[:MAX_CV_CHARS] + "\n\n[truncated]"


def _parse_json_object(raw: str) -> dict[str, Any]:
    """Parse model output into a dict, tolerating optional markdown fences."""
    cleaned = raw.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
    if fence:
        cleaned = fence.group(1).strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ExternalServiceError(
            "LLM returned invalid JSON for profile summary",
            details={"reason": str(exc)},
        ) from exc
    if not isinstance(data, dict):
        raise ExternalServiceError("LLM summary must be a JSON object")
    return data


def _normalize_summary(data: dict[str, Any]) -> dict[str, Any]:
    """Shape model output into profile fields + nested profile_summary."""
    skills = data.get("skills")
    if skills is not None and not isinstance(skills, list):
        skills = [str(skills)]
    if skills is not None:
        skills = [str(s).strip() for s in skills if str(s).strip()][:100]

    years = data.get("experience_years")
    if years is not None:
        try:
            years = int(years)
        except (TypeError, ValueError):
            years = None
        if years is not None and (years < 0 or years > 80):
            years = None

    profile_summary = {
        "headline": data.get("headline") or data.get("title"),
        "summary": data.get("summary") or data.get("bio") or data.get("overview"),
        "highlights": data.get("highlights") or data.get("achievements") or [],
        "skills": skills or [],
        "experience_years": years,
    }
    # Drop null-ish empty strings for cleanliness
    if not profile_summary["headline"]:
        profile_summary["headline"] = None
    if not profile_summary["summary"]:
        profile_summary["summary"] = None

    return {
        "profile_summary": profile_summary,
        "skills": skills,
        "experience_years": years,
    }


def _call_anthropic(cv_text: str, settings: Settings) -> str:
    """Call Anthropic Messages API; return assistant text."""
    api_key = (settings.claude_api_key or "").strip()
    if not api_key or api_key in {"sk-test", "test", "changeme"}:
        raise ExternalServiceError(
            "Claude API is not configured",
            details={"hint": "Set CLAUDE_API_KEY for live summary generation"},
        )

    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover
        raise ExternalServiceError("anthropic package is not installed") from exc

    client = anthropic.Anthropic(api_key=api_key, timeout=60.0)
    try:
        message = client.messages.create(
            model=settings.claude_model,
            max_tokens=2048,
            system=PROFILE_SUMMARY_SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Extract a structured profile summary from this CV text:\n\n"
                        f"{_truncate_cv(cv_text)}"
                    ),
                }
            ],
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Anthropic API call failed")
        raise ExternalServiceError(
            "Failed to generate profile summary via Claude",
            details={"reason": str(exc)[:200]},
        ) from exc

    parts: list[str] = []
    for block in message.content:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    if not parts:
        raise ExternalServiceError("Claude returned an empty response")
    return "\n".join(parts)


def generate_profile_summary(
    cv_text: str,
    *,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Generate structured profile summary from extracted CV text.

    Returns dict with keys: ``profile_summary``, ``skills``, ``experience_years``.
    """
    text = (cv_text or "").strip()
    if not text:
        raise ValidationError(
            "CV text is required to generate a summary",
            details={"field": "cv_extracted_text"},
        )

    if _override_generator is not None:
        raw = _override_generator(text)
        if isinstance(raw, dict) and "profile_summary" in raw:
            return raw
        if isinstance(raw, dict):
            return _normalize_summary(raw)
        raise ExternalServiceError("Mock summary generator returned invalid data")

    cfg = settings or get_settings()
    raw_text = _call_anthropic(text, cfg)
    data = _parse_json_object(raw_text)
    return _normalize_summary(data)

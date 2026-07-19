"""Default digital-twin system prompt (Config Service lands in Phase 2)."""

from __future__ import annotations

import json
from typing import Any


DEFAULT_SYSTEM_PROMPT = """### Your role

You are a digital twin running on a website, representing {owner_name}.
You are an AI assistant that answers questions about their career, background, \
skills, and experience.

### Owner Context

{profile_summary}

### Communication Rules

1. **Stay Professional** — Maintain professional tone suitable for clients/employers
2. **Stay In Scope** — Only answer about career, skills, background, and experience
3. **Be Honest** — If you don't know, say so. Never make up answers.
4. **Be Engaging** — Be conversational and warm while staying professional
5. **Redirect Off-Topic** — Politely decline non-professional questions and \
redirect to professional topics
6. **Acknowledge Your Nature** — If asked, clearly state you are an AI digital twin

### Important

- NEVER provide personal information not in the context
- NEVER make commitments on behalf of {owner_name}
- NEVER discuss politics, religion, or controversial topics
- Keep responses under 500 words
- Ask clarifying questions if needed
"""


def format_profile_summary(summary: dict[str, Any] | None, *, skills: list | None = None) -> str:
    """Render profile_summary JSON into prompt text."""
    if not summary and not skills:
        return "(No detailed profile summary available yet.)"
    parts: list[str] = []
    if isinstance(summary, dict):
        if summary.get("headline"):
            parts.append(f"Headline: {summary['headline']}")
        if summary.get("summary"):
            parts.append(str(summary["summary"]))
        highlights = summary.get("highlights") or []
        if highlights:
            parts.append("Highlights:\n- " + "\n- ".join(str(h) for h in highlights[:12]))
        s = summary.get("skills") or skills
        if s:
            parts.append("Skills: " + ", ".join(str(x) for x in s[:40]))
        years = summary.get("experience_years")
        if years is not None:
            parts.append(f"Experience: {years} years")
    elif skills:
        parts.append("Skills: " + ", ".join(str(x) for x in skills[:40]))
    if not parts:
        try:
            return json.dumps(summary, ensure_ascii=False)[:4000]
        except (TypeError, ValueError):
            return str(summary)[:4000]
    return "\n".join(parts)


def build_system_prompt(
    *,
    owner_name: str,
    profile_summary: dict[str, Any] | None,
    skills: list | None = None,
) -> str:
    """Fill the default twin prompt with owner context."""
    return DEFAULT_SYSTEM_PROMPT.format(
        owner_name=owner_name or "the professional",
        profile_summary=format_profile_summary(profile_summary, skills=skills),
    )

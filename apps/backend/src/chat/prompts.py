"""Default digital-twin system prompt and rendering helpers."""

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

_TONE_LINES = {
    "professional": "Use a professional, polished voice suitable for clients and employers.",
    "casual": "Use a casual, approachable conversational style while staying respectful.",
    "technical": "Use a technical, precise voice with concrete engineering detail when relevant.",
    "friendly": "Use a warm, friendly tone while remaining professionally appropriate.",
}

_LENGTH_LINES = {
    "concise": "Prefer concise answers (a few short paragraphs or less).",
    "balanced": "Use a balanced response length — informative but not verbose.",
    "detailed": "Provide detailed answers with examples when helpful (still under 500 words).",
}


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


def render_prompt_template(
    template: str,
    *,
    owner_name: str,
    profile_summary: dict[str, Any] | None,
    skills: list | None = None,
) -> str:
    """Fill {owner_name} and {profile_summary} placeholders safely."""
    name = owner_name or "the professional"
    summary = format_profile_summary(profile_summary, skills=skills)
    try:
        return template.format(owner_name=name, profile_summary=summary)
    except (KeyError, ValueError):
        return template.replace("{owner_name}", name).replace("{profile_summary}", summary)


def build_system_prompt(
    *,
    owner_name: str,
    profile_summary: dict[str, Any] | None,
    skills: list | None = None,
    template: str | None = None,
    tone: str | None = None,
    response_length: str | None = None,
    brand_guidelines: str | None = None,
    allowed_topics: list[str] | None = None,
    forbidden_topics: list[str] | None = None,
) -> str:
    """Render twin system prompt from template + style/topic overlays."""
    base = render_prompt_template(
        template or DEFAULT_SYSTEM_PROMPT,
        owner_name=owner_name,
        profile_summary=profile_summary,
        skills=skills,
    )
    extras: list[str] = []
    if tone:
        line = _TONE_LINES.get(tone.lower())
        if line:
            extras.append(f"### Tone\n{line}")
    if response_length:
        line = _LENGTH_LINES.get(response_length.lower())
        if line:
            extras.append(f"### Response length\n{line}")
    if brand_guidelines and brand_guidelines.strip():
        extras.append(f"### Brand guidelines\n{brand_guidelines.strip()}")
    if allowed_topics:
        extras.append(
            "### Preferred topics\nPrefer discussing: "
            + ", ".join(str(t) for t in allowed_topics[:40])
        )
    if forbidden_topics:
        extras.append(
            "### Forbidden topics\nDo not discuss: "
            + ", ".join(str(t) for t in forbidden_topics[:40])
        )
    if extras:
        return base.rstrip() + "\n\n" + "\n\n".join(extras)
    return base

"""Lightweight off-topic / boundary heuristics for visitor messages.

Full LLM boundary enforcement is encoded in the system prompt; this module
provides a cheap pre-check so clearly out-of-scope content gets a polite
redirect without calling Claude.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Patterns that are clearly outside professional career chat.
_OFF_TOPIC_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\b(who will win|sports betting|casino|gambling)\b",
        r"\b(write me (a |an )?(poem|essay|homework|exam))\b",
        r"\b(how to (make|build|hack) (a |an )?(bomb|weapon|malware|virus))\b",
        r"\b(medical (advice|diagnosis)|prescribe|dosage)\b",
        r"\b(legal advice|sue |lawsuit)\b",
        r"\b(password|ssn|social security|credit card)\b",
        r"\b(dating|hookup|onlyfans)\b",
        r"\b(crypto tip|stock tip|insider trade)\b",
    )
)

# Soft career-related keywords — if present, skip hard redirect even if mixed.
_CAREER_HINTS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\b(experience|skill|resume|cv|career|job|role|project|work|background)\b",
        r"\b(education|degree|engineer|developer|manager|portfolio)\b",
        r"\b(hire|interview|open to work|availability)\b",
    )
)

REDIRECT_MESSAGE = (
    "I'm here to answer questions about this professional's career, skills, "
    "and experience. I can't help with that topic — feel free to ask about "
    "their background, projects, or expertise instead."
)

# After this many redirects in one session, flag the conversation.
FLAG_AFTER_VIOLATIONS = 3


@dataclass(frozen=True)
class BoundaryResult:
    off_topic: bool
    redirect_message: str | None = None


def check_message_boundary(
    content: str,
    *,
    forbidden_topics: list[str] | None = None,
    allowed_topics: list[str] | None = None,
) -> BoundaryResult:
    """Return whether the visitor message should be politely redirected.

    ``forbidden_topics`` / ``allowed_topics`` come from owner DigitalTwinConfig
    when available (Phase 2). Built-in patterns still apply.
    """
    text = (content or "").strip()
    if not text:
        return BoundaryResult(off_topic=False)

    lower = text.lower()
    if forbidden_topics:
        for topic in forbidden_topics:
            t = (topic or "").strip().lower()
            if t and t in lower:
                return BoundaryResult(off_topic=True, redirect_message=REDIRECT_MESSAGE)

    has_career = any(p.search(text) for p in _CAREER_HINTS)
    if allowed_topics and not has_career:
        # If owner listed preferred topics and message matches none of them
        # and also hits a hard off-topic pattern, redirect (keep soft).
        pass

    hits = [p.pattern for p in _OFF_TOPIC_PATTERNS if p.search(text)]
    if hits and not has_career:
        return BoundaryResult(off_topic=True, redirect_message=REDIRECT_MESSAGE)
    return BoundaryResult(off_topic=False)

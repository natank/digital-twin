"""Default digital twin configuration values."""

from __future__ import annotations

from src.chat.prompts import DEFAULT_SYSTEM_PROMPT

TONES = frozenset({"professional", "casual", "technical", "friendly"})
RESPONSE_LENGTHS = frozenset({"concise", "balanced", "detailed"})

DEFAULT_TONE = "professional"
DEFAULT_RESPONSE_LENGTH = "balanced"
DEFAULT_PROMPT_TEMPLATE = DEFAULT_SYSTEM_PROMPT

"""Pluggable email backends (console for development)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from backend_shared.logging import get_logger

from src.settings import get_settings

logger = get_logger(__name__)


class EmailSender(Protocol):
    """Minimal email port used by auth flows."""

    def send(self, *, to: str, subject: str, body: str) -> None:
        """Send a plain-text email."""


@dataclass
class ConsoleEmailSender:
    """Log emails instead of delivering them (local/dev/tests)."""

    sent: list[dict[str, str]] = field(default_factory=list)

    def send(self, *, to: str, subject: str, body: str) -> None:
        record = {"to": to, "subject": subject, "body": body}
        self.sent.append(record)
        logger.info("email[console] to=%s subject=%s\n%s", to, subject, body)


_default_sender: EmailSender | None = None


def get_email_sender() -> EmailSender:
    """Return the process-wide email sender (console unless configured later)."""
    global _default_sender
    if _default_sender is None:
        backend = get_settings().email_backend.lower()
        if backend != "console":
            logger.warning("Unknown EMAIL_BACKEND=%s; using console", backend)
        _default_sender = ConsoleEmailSender()
    return _default_sender


def set_email_sender(sender: EmailSender | None) -> None:
    """Override the email sender (tests)."""
    global _default_sender
    _default_sender = sender

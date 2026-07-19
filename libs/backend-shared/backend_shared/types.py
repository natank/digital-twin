"""Shared enums and type aliases used across backend modules.

Values mirror the enums documented in docs/TECHNICAL_DESIGN.md so that
database columns, API payloads, and notification logic all agree.
"""

from enum import Enum, IntEnum


class MessageSender(str, Enum):
    """Who produced a chat message."""

    VISITOR = "visitor"
    AI = "ai"


class ProcessingStatus(str, Enum):
    """Lifecycle of an async job (e.g. CV processing)."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class NotificationType(str, Enum):
    """Events that can trigger an owner notification."""

    CONVERSATION_STARTED = "conversation_started"
    HIGH_INTENT_DETECTED = "high_intent_detected"
    CONVERSATION_ENDED = "conversation_ended"
    SUMMARY_READY = "profile_summary_ready"
    ERROR_OCCURRED = "error_occurred"


class NotificationPriority(IntEnum):
    """Pushover priority levels (values are defined by the Pushover API)."""

    LOW = -1
    NORMAL = 0
    HIGH = 1
    EMERGENCY = 2


class DeliveryStatus(str, Enum):
    """Delivery state of an outbound notification."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    EXPIRED = "expired"


class ResponseTone(str, Enum):
    """Configurable digital-twin response tone (docs/PRD.md E5-S2)."""

    PROFESSIONAL = "professional"
    CASUAL = "casual"
    TECHNICAL = "technical"
    FRIENDLY = "friendly"


class ResponseLength(str, Enum):
    """Configurable digital-twin response length (docs/PRD.md E5-S2)."""

    CONCISE = "concise"
    BALANCED = "balanced"
    DETAILED = "detailed"

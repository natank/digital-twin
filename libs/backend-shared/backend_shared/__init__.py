"""Shared backend utilities for the Digital Twin platform.

Stateless, reusable building blocks for the backend's domain modules:
exceptions, the API response envelope, logging setup, encryption/validation
helpers, and shared enums.

Deliberately excluded: database sessions and application settings. Those
live in ``apps/backend/src`` (see docs/phase-0/PR_BREAKDOWN.md, PR-005
notes) so this library stays free of configuration dependencies.
"""

from backend_shared.exceptions import (
    AppError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DatabaseError,
    ExternalServiceError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from backend_shared.logging import configure_logging, get_logger
from backend_shared.schemas import (
    ApiResponse,
    BaseSchema,
    ErrorDetail,
    PaginationMeta,
    ResponseMeta,
)
from backend_shared.types import (
    DeliveryStatus,
    MessageSender,
    NotificationPriority,
    NotificationType,
    ProcessingStatus,
    ResponseLength,
    ResponseTone,
)
from backend_shared.utils import (
    decrypt_field,
    encrypt_field,
    generate_encryption_key,
    validate_email,
    validate_password_strength,
)

__all__ = [
    # exceptions
    "AppError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "DatabaseError",
    "ExternalServiceError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    # logging
    "configure_logging",
    "get_logger",
    # schemas
    "ApiResponse",
    "BaseSchema",
    "ErrorDetail",
    "PaginationMeta",
    "ResponseMeta",
    # types
    "DeliveryStatus",
    "MessageSender",
    "NotificationPriority",
    "NotificationType",
    "ProcessingStatus",
    "ResponseLength",
    "ResponseTone",
    # utils
    "decrypt_field",
    "encrypt_field",
    "generate_encryption_key",
    "validate_email",
    "validate_password_strength",
]

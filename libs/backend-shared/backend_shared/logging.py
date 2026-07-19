"""Structured JSON logging configuration.

Matches the approach in docs/TECHNICAL_DESIGN.md ("Monitoring &
Observability"): JSON to stdout, so a log shipper can parse records without
regex.
"""

import logging
import sys

from pythonjsonlogger.json import JsonFormatter

# Included on every record so log aggregators get consistent fields.
_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configure_logging(level: str = "INFO", *, json_output: bool = True) -> None:
    """Configure the root logger.

    Call once at application startup, before other loggers are used.

    Args:
        level: Standard level name ("DEBUG", "INFO", ...). Unrecognized
            values fall back to INFO.
        json_output: JSON records when True; plain text when False, which is
            easier to read when running locally.
    """
    handler = logging.StreamHandler(sys.stdout)
    if json_output:
        handler.setFormatter(JsonFormatter(_LOG_FORMAT))
    else:
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))

    root = logging.getLogger()
    # Replace existing handlers so repeated calls don't duplicate output.
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger; use ``get_logger(__name__)``."""
    return logging.getLogger(name)

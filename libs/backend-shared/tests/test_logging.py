"""Tests for logging configuration."""

import json
import logging

from backend_shared.logging import configure_logging, get_logger


def test_json_output_is_parseable(capsys):
    configure_logging(level="INFO", json_output=True)
    get_logger("test.module").info("hello")

    record = json.loads(capsys.readouterr().out.strip())
    assert record["message"] == "hello"
    assert record["levelname"] == "INFO"
    assert record["name"] == "test.module"


def test_plain_output_is_not_json(capsys):
    configure_logging(level="INFO", json_output=False)
    get_logger("test.module").info("hello")

    out = capsys.readouterr().out
    assert "hello" in out
    assert not out.strip().startswith("{")


def test_level_is_applied(capsys):
    configure_logging(level="WARNING")
    logger = get_logger("test.module")
    logger.info("suppressed")
    logger.warning("emitted")

    out = capsys.readouterr().out
    assert "suppressed" not in out
    assert "emitted" in out


def test_unknown_level_falls_back_to_info():
    configure_logging(level="NOT_A_LEVEL")
    assert logging.getLogger().level == logging.INFO


def test_repeated_configuration_does_not_duplicate_handlers():
    configure_logging()
    configure_logging()
    assert len(logging.getLogger().handlers) == 1


def test_get_logger_returns_named_logger():
    assert get_logger("a.b.c").name == "a.b.c"

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for the KOIOS logging utility."""

import json
import logging
from pathlib import Path
from unittest.mock import PropertyMock, StringIO, patch

import pytest

# Import the module/class to test
from subsystems.KOIOS.core.logging import KoiosLogger

# Define a temporary log directory/file for testing
TEST_LOG_DIR = Path("./temp_test_logs")
TEST_LOG_FILE = TEST_LOG_DIR / "test_egos.log"


@pytest.fixture(autouse=True)
def manage_koios_logger_state():
    """Fixture to manage KoiosLogger state and test log files around each test."""
    # Setup: Reset state before each test
    KoiosLogger._initialized = False
    KoiosLogger._log_level = logging.INFO
    KoiosLogger._use_json_logging = True
    KoiosLogger._log_to_file = False  # Disable file logging by default

    # Clean up any potential log files/dirs from previous runs
    if TEST_LOG_FILE.exists():
        try:
            TEST_LOG_FILE.unlink()
        except OSError:
            pass  # Ignore if deletion fails
    if TEST_LOG_DIR.exists():
        try:
            TEST_LOG_DIR.rmdir()
        except OSError:
            pass  # Ignore if deletion fails

    # Ensure root logger handlers are cleared
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    root_logger.handlers.clear()

    yield  # Test runs here

    # Teardown: Clean up files/dirs and reset state again
    if TEST_LOG_FILE.exists():
        try:
            TEST_LOG_FILE.unlink()
        except OSError:
            pass
    if TEST_LOG_DIR.exists():
        try:
            TEST_LOG_DIR.rmdir()
        except OSError:
            pass
    KoiosLogger._initialized = False
    # Restore original root handlers if needed, or just clear
    root_logger.handlers.clear()
    # If preserving original state was critical:
    # root_logger.handlers = original_handlers


# Note: Can keep unittest.mock.patch or use pytest-mock's mocker fixture
@patch("logging.StreamHandler.stream", new_callable=PropertyMock)
def test_get_logger_initializes_and_returns_logger(mock_stream):
    """Test that get_logger initializes the system and returns a logger."""
    assert not KoiosLogger._initialized
    logger = KoiosLogger.get_logger("TEST.Module")
    assert KoiosLogger._initialized
    assert isinstance(logger, logging.Logger)
    assert logger.name == "TEST.Module"
    assert logger.level == logging.INFO  # Should inherit root level


@patch("sys.stdout", new_callable=StringIO)  # Capture stdout
def test_json_logging_format_console(mock_stdout):
    """Test that logs are formatted as JSON to console when enabled."""
    KoiosLogger._use_json_logging = True
    logger = KoiosLogger.get_logger("TEST.JSON")
    test_message = "Testing JSON output"
    logger.info(test_message)

    # Get output and parse JSON
    output = mock_stdout.getvalue().strip()
    try:
        log_json = json.loads(output)
        assert log_json["message"] == test_message
        assert log_json["level"] == "INFO"
        assert log_json["name"] == "TEST.JSON"
        assert log_json["subsystem"] == "TEST"
        assert log_json["module"] == "JSON"
        assert "timestamp" in log_json
    except json.JSONDecodeError:
        pytest.fail(f"Log output was not valid JSON: {output}")


@patch("sys.stdout", new_callable=StringIO)
def test_standard_logging_format_console(mock_stdout):
    """Test that logs use standard format when JSON is disabled."""
    KoiosLogger._use_json_logging = False
    KoiosLogger._log_level = logging.DEBUG  # Use debug to ensure message appears
    logger = KoiosLogger.get_logger("TEST.Standard")
    test_message = "Testing standard output"

    # Temporarily patch the default format for predictability if needed
    format_patch = patch(
        "subsystems.KOIOS.core.logging.DEFAULT_LOG_FORMAT", "%(levelname)s:%(name)s:%(message)s"
    )
    with format_patch:
        # Re-initialize to apply the non-JSON format
        KoiosLogger._initialized = False
        logger = KoiosLogger.get_logger("TEST.Standard")
        logger.debug(test_message)

    output = mock_stdout.getvalue().strip()
    assert "{" not in output  # Should not be JSON
    assert f"DEBUG:TEST.Standard:{test_message}" in output


@patch("subsystems.KOIOS.core.logging.LOG_FILE_DIR", TEST_LOG_DIR)
@patch("subsystems.KOIOS.core.logging.LOG_FILE_PATH", TEST_LOG_FILE)
def test_file_logging_enabled():
    """Test that logs are written to a file when enabled."""
    KoiosLogger._log_to_file = True
    KoiosLogger._use_json_logging = True  # Use JSON for easier parsing
    logger = KoiosLogger.get_logger("TEST.FileLog")
    test_message = "Testing file logging"

    logger.warning(test_message)

    # Ensure handlers are flushed if necessary
    # logging.shutdown() might be more robust if needed

    assert TEST_LOG_DIR.exists()
    assert TEST_LOG_FILE.exists()

    with open(TEST_LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        try:
            log_json = json.loads(content)
            assert log_json["message"] == test_message
            assert log_json["level"] == "WARNING"
            assert log_json["name"] == "TEST.FileLog"
        except json.JSONDecodeError:
            pytest.fail(f"File log output was not valid JSON: {content}")


@patch("sys.stdout", new_callable=StringIO)
def test_extra_data_in_json(mock_stdout):
    """Test that extra data is included in JSON logs."""
    KoiosLogger._use_json_logging = True
    logger = KoiosLogger.get_logger("TEST.Extra")
    extra_info = {"user_id": 123, "request_id": "abc-123"}
    logger.info("Message with extra", extra=extra_info)

    output = mock_stdout.getvalue().strip()
    try:
        log_json = json.loads(output)
        assert "extra" in log_json
        assert log_json["extra"] == extra_info
        assert log_json["message"] == "Message with extra"
    except json.JSONDecodeError:
        pytest.fail(f"Log output was not valid JSON: {output}")


@patch("sys.stdout", new_callable=StringIO)
def test_exception_logging_json(mock_stdout):
    """Test that exception info is included in JSON logs."""
    KoiosLogger._use_json_logging = True
    logger = KoiosLogger.get_logger("TEST.Exception")
    try:
        raise ValueError("Test exception")
    except ValueError:
        logger.error("An error occurred", exc_info=True)

    output = mock_stdout.getvalue().strip()
    try:
        log_json = json.loads(output)
        assert log_json["message"] == "An error occurred"
        assert log_json["level"] == "ERROR"
        assert "exception" in log_json
        assert isinstance(log_json["exception"], str)
        assert "ValueError: Test exception" in log_json["exception"]
        assert "Traceback" in log_json["exception"]
    except json.JSONDecodeError:
        pytest.fail(f"Log output was not valid JSON: {output}")


# ✧༺❀༻∞ EGOS ∞༺❀༻✧

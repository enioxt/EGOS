#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - KOIOS Logging Utility
=====================================

Provides a standardized way to configure and obtain loggers across EGOS subsystems,
ensuring consistent formatting and output as defined in KOIOS standards.

Version: 1.0.0
Last Updated: 2025-04-07
"""

import json
import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import sys
from typing import Any, Dict, Optional

# Module-level set to track configured loggers
# Note: This is currently unused but could be leveraged for more complex state management.
# _configured_loggers = set()

# --- Configuration --- #
# TODO: Load configuration from a KOIOS config file (e.g., koios_config.yaml)
DEFAULT_LOG_LEVEL = logging.INFO
# Consider making format strings constants if reused heavily
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
JSON_LOG_FORMAT = None  # JSON Formatter handles its own structure
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
# Define paths relative to a potential project root or make configurable
LOG_FILE_DIR = Path("./logs")
LOG_FILE_NAME = "egos_system.log"
LOG_WHEN = "midnight"  # Options: S, M, H, D, W0-W6, midnight
LOG_INTERVAL = 1
LOG_BACKUP_COUNT = 7  # Number of old log files to keep
STRUCTURED_LOGGING = True  # Default to JSON logging

# Ensure log directory exists
LOG_FILE_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE_PATH = LOG_FILE_DIR / LOG_FILE_NAME


class JsonFormatter(logging.Formatter):
    """Formats log records as JSON strings according to KOIOS standards.

    Includes standard LogRecord attributes as well as derived fields like
    subsystem and module, and handles exception formatting and extra data.
    """

    # Standard fields desired in the JSON output
    _DEFAULT_FIELDS = (
        "timestamp",
        "level",
        "name",  # Full logger name (e.g., SUBSYSTEM.Module)
        "message",
        "subsystem",  # Derived from the first part of the name
        "module",  # Derived from the second part of the name (if exists)
        "pathname",  # Full path of the source file
        "lineno",  # Line number in the source file
        "funcName",  # Name of the function/method logging the message
        "exception",  # Formatted exception info if present
        "extra",  # Additional contextual data passed to the logger
    )

    def __init__(
        self,
        fmt: Optional[
            Dict[str, str]
        ] = None,  # fmt is ignored for JSON, but kept for signature compatibility
        datefmt: Optional[str] = DEFAULT_DATE_FORMAT,
        style: str = "%",  # style is ignored for JSON
        validate: bool = True,  # validate added in Python 3.8
        *,  # Keyword-only arguments below (Python 3.8+)
        defaults: Optional[Dict[str, Any]] = None,  # Python 3.10+
    ):
        """Initializes the JSON formatter.

        Args:
            fmt: Style format string (ignored for JSON).
            datefmt: Date format string for the 'timestamp' field.
            style: Style character (ignored for JSON).
            validate: If True, performs validation checks (Python 3.8+).
            defaults: Default values for LogRecord attributes (Python 3.10+).
        """
        # Initialize with a basic format string for compatibility if needed, but we override format()
        super().__init__(fmt="%(message)s", datefmt=datefmt)
        # Store desired fields
        self.fields_to_log = self._DEFAULT_FIELDS
        # Store other parameters if needed for advanced logic later
        self._validate = validate
        self._defaults = defaults

    def format(self, record: logging.LogRecord) -> str:
        """Formats the LogRecord instance into a JSON string.

        Args:
            record: The logging.LogRecord instance to format.

        Returns:
            A JSON string representation of the log record.
        """
        log_entry: Dict[str, Any] = {}

        # Extract subsystem and module from logger name
        name_parts = record.name.split(".", 1)
        subsystem = name_parts[0] if name_parts else record.name
        module = name_parts[1] if len(name_parts) > 1 else ""

        # Populate the log entry based on desired fields
        for field in self.fields_to_log:
            value = None
            if field == "timestamp":
                value = self.formatTime(record, self.datefmt)
            elif field == "level":
                value = record.levelname
            elif field == "name":
                value = record.name
            elif field == "message":
                # Ensure message is properly formatted (handles args)
                record.message = record.getMessage()
                value = record.message
            elif field == "subsystem":
                value = subsystem
            elif field == "module":
                value = module
            elif field == "exception":
                if record.exc_info:
                    value = self.formatException(record.exc_info)
            elif field == "extra":
                # Safely extract extra data, exclude standard attrs and already processed fields
                standard_attrs = set(logging.LogRecord.__dict__.keys())
                extra_data = {
                    k: v
                    for k, v in record.__dict__.items()
                    if k not in standard_attrs and k not in log_entry
                }
                if extra_data:
                    value = extra_data  # Store the dict directly
            else:
                # Get standard LogRecord attributes
                value = getattr(record, field, None)

            # Only add the field if it has a value (or handle specifically if None is desired)
            if value is not None:
                log_entry[field] = value

        try:
            # Ensure ensure_ascii=False for broader character support
            # Use default=str for basic handling of non-serializable types
            return json.dumps(log_entry, ensure_ascii=False, default=str)
        except TypeError as e:
            # Fallback for complex non-serializable types
            error_log = {
                "timestamp": self.formatTime(record, self.datefmt),
                "level": "ERROR",
                "name": "JsonFormatter.Error",
                "message": f"Failed to serialize log record: {e}",
                "original_record_name": record.name,
                # Avoid trying to serialize the problematic record itself
            }
            return json.dumps(error_log, ensure_ascii=False)


class KoiosLogger:
    """Provides a standardized way to get loggers within the EGOS system.

    Acts as a factory and configuration point for logging, ensuring consistent
    formatting (standard or JSON) and level settings across subsystems based on
    initial configuration or subsequent calls to `configure()`.

    Usage:
        KoiosLogger.configure(level=logging.DEBUG, use_json=True, log_to_file=True)
        logger = KoiosLogger.get_logger("SUBSYSTEM.ModuleName")
        logger.info("This is an info message.", extra={"request_id": "123"})
    """

    _initialized: bool = False
    _log_level: int = DEFAULT_LOG_LEVEL
    _date_format: str = DEFAULT_DATE_FORMAT
    _use_json_logging: bool = STRUCTURED_LOGGING
    _log_to_file: bool = True  # Default to enabling file logging
    _file_path: Path = LOG_FILE_PATH

    @classmethod
    def _initialize(cls) -> None:
        """Sets up the root logger configuration based on class attributes.

        Called implicitly by `get_logger` if not already initialized.
        Configures console and (if enabled) file handlers with the selected formatter.
        Future: Load settings from a central KOIOS configuration.
        """
        if cls._initialized:
            return

        root_logger = logging.getLogger()  # Get the root logger
        root_logger.setLevel(cls._log_level)  # Set level on root

        # Clear existing handlers to avoid duplicates on re-initialization (e.g., during tests)
        if root_logger.hasHandlers():
            root_logger.handlers.clear()

        # --- Select Formatter ---
        if cls._use_json_logging:
            formatter = JsonFormatter(datefmt=cls._date_format)
            format_description = "JSON"
        else:
            formatter = logging.Formatter(DEFAULT_LOG_FORMAT, datefmt=cls._date_format)
            format_description = f"Standard ('{DEFAULT_LOG_FORMAT}')"

        # --- Configure Console Handler ---
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        # Optionally set a different level for console vs file
        # stream_handler.setLevel(logging.WARNING)
        root_logger.addHandler(stream_handler)
        handler_descriptions = ["StreamHandler(stdout)"]

        # --- Configure File Handler (Optional) ---
        if cls._log_to_file:
            try:
                # Ensure log directory exists
                cls._file_path.parent.mkdir(parents=True, exist_ok=True)

                file_handler = TimedRotatingFileHandler(
                    cls._file_path,
                    when=LOG_WHEN,
                    interval=LOG_INTERVAL,
                    backupCount=LOG_BACKUP_COUNT,
                    encoding="utf-8",
                )
                file_handler.setFormatter(formatter)
                # File handler level could be different, e.g., log more details to file
                # file_handler.setLevel(logging.DEBUG)
                root_logger.addHandler(file_handler)
                handler_descriptions.append(f"TimedRotatingFileHandler({cls._file_path})")
            except Exception as e:
                # Log error to console if file handler fails
                # Use a temporary basic config for this critical error message
                logging.basicConfig(
                    level=logging.ERROR, format="%(levelname)s:KoiosLoggerSetup: %(message)s"
                )
                logging.error(
                    f"Failed to initialize file logging to {cls._file_path}: {e}", exc_info=True
                )
                # Ensure the flag reflects reality if file logging failed
                cls._log_to_file = False

        cls._initialized = True

        # Log initialization details using the newly configured logger
        # Use a distinct logger name for initialization messages
        init_logger = logging.getLogger("KoiosLogger.Setup")
        init_logger.info(
            "KoiosLogger initialized.",
            extra={
                "config": {
                    "level": logging.getLevelName(cls._log_level),
                    "formatter": format_description,
                    "handlers": handler_descriptions,
                    "log_to_file": cls._log_to_file,
                    "file_path": str(cls._file_path) if cls._log_to_file else None,
                }
            },
        )

    @classmethod
    def get_logger(cls, name: Optional[str] = None) -> logging.Logger:
        """Gets a logger instance with the specified name.

        Ensures the logging system is initialized before returning the logger.
        Loggers inherit the level and handlers from the root logger.

        Args:
            name: The hierarchical name for the logger (e.g., "NEXUS.Core").
                  If None, returns the root logger.

        Returns:
            A configured logger instance.
        """
        if not cls._initialized:
            cls._initialize()

        # Return the specific logger; it will inherit handlers/level from the root
        return logging.getLogger(name)

    @classmethod
    def configure(
        cls,
        level: int = logging.INFO,
        use_json: bool = True,
        log_to_file: bool = True,
        date_format: Optional[str] = None,
        file_path: Optional[str] = None,
        log_when: str = "midnight",
        log_interval: int = 1,
        backup_count: int = 7,
    ) -> None:
        """Reconfigures the KoiosLogger settings.

        Allows changing the log level, format (JSON vs standard), file logging,
        date format, and file rotation parameters after initial setup.
        This will reset the initialization flag and apply the new settings
        the next time `get_logger` is called.

        Args:
            level: The minimum logging level (e.g., logging.DEBUG, logging.INFO).
            use_json: True to use JSON format, False for standard format.
            log_to_file: True to enable logging to a file, False otherwise.
            date_format: Optional custom date format string for logs.
            file_path: Optional path to the log file (overrides default).
            log_when: Rollover interval type ('S', 'M', 'H', 'D', 'midnight', 'W0'-'W6').
            log_interval: Rollover interval multiplier.
            backup_count: Number of backup log files to keep.
        """
        cls._log_level = level
        cls._use_json_logging = use_json
        cls._log_to_file = log_to_file
        cls._date_format = date_format if date_format is not None else DEFAULT_DATE_FORMAT

        # Update file path settings only if file logging is enabled
        if cls._log_to_file:
            global LOG_FILE_PATH, LOG_WHEN, LOG_INTERVAL, LOG_BACKUP_COUNT
            if file_path:
                cls._file_path = Path(file_path)
                # Update global for consistency if needed, though class attr is primary
                LOG_FILE_PATH = cls._file_path
            else:
                cls._file_path = LOG_FILE_PATH  # Use default if not provided

            # Update rotation globals (or store on class if preferred)
            LOG_WHEN = log_when
            LOG_INTERVAL = log_interval
            LOG_BACKUP_COUNT = backup_count
        else:
            # Ensure file path isn't used if file logging is off
            cls._file_path = None  # Or keep the default path but don't use it

        # Reset initialization status so changes take effect on next get_logger call
        cls._initialized = False

        # Log reconfiguration attempt (using a temporary basic logger if needed)
        temp_logger = logging.getLogger("KoiosLogger.Reconfigure")
        temp_logger.info(
            f"KoiosLogger reconfigured: Level={logging.getLevelName(level)}, JSON={use_json}, FileLog={log_to_file}"
        )
        # Force re-initialization immediately if desired, or let get_logger handle it
        # cls._initialize()


# --- Standalone Function (Consider if needed vs. class method) ---


def get_koios_logger(
    name: str,
    # config: Optional[Dict[str, Any]] = None, # Removed complex config dict for simplicity
    level: Optional[int] = None,
    # log_format: Optional[str] = None, # Format handled by KoiosLogger.configure
    # date_format: Optional[str] = None, # Handled by KoiosLogger.configure
    # log_to_console: bool = True, # Handled by KoiosLogger setup
    # log_file: Optional[str] = None, # Handled by KoiosLogger.configure
) -> logging.Logger:
    """Provides a simple way to get a Koios-configured logger.

    This acts as a convenience wrapper around `KoiosLogger.get_logger`.
    It ensures the KoiosLogger system is initialized with defaults or previous
    configuration before returning the requested logger.
    It primarily exists for potentially simpler usage patterns where explicit
    configuration via `KoiosLogger.configure` is not immediately needed.

    Args:
        name: The hierarchical name for the logger (e.g., "NEXUS.Core").
        level: Optional specific level for this logger (overrides root if higher).
               Setting level here only affects this specific logger, not the handlers.

    Returns:
        A configured logger instance obtained via KoiosLogger.
    """
    # Ensure KoiosLogger system is initialized (idempotent check inside get_logger)
    logger = KoiosLogger.get_logger(name)

    # Optionally set a specific level for *this* logger instance
    if level is not None:
        logger.setLevel(level)

    return logger


# Example Usage (can be run if script is executed directly):
# if __name__ == "__main__":
#     # Configure once (optional, defaults are used otherwise)
#     KoiosLogger.configure(level=logging.DEBUG, use_json=True, log_to_file=True)

#     # Get loggers
#     logger1 = get_koios_logger("MY_SUBSYSTEM.ModuleA")
#     logger2 = get_koios_logger("MY_SUBSYSTEM.ModuleB", level=logging.INFO)
#     core_logger = KoiosLogger.get_logger("CORE.System") # Can also use class method directly

#     # Log messages
#     logger1.debug("This is a debug message from ModuleA.")
#     logger1.info("Informational message.", extra={"user": "test", "id": 123})
#     logger2.info("Info message from ModuleB (logger level INFO).")
#     logger2.warning("Warning message from ModuleB.")
#     core_logger.critical("Critical system event!")

#     try:
#         1 / 0
#     except ZeroDivisionError:
#         core_logger.error("An exception occurred", exc_info=True)

#     print(f"Logs should be in console and optionally in {LOG_FILE_PATH}")


# ✧༺❀༻∞ EGOS ∞༺❀༻✧

"""
KoiosLogger - Standardized logging for EGOS Dashboard
Implements KOIOS logging standards for consistent log format and management.
"""

from datetime import datetime
import logging
import os
from typing import Any, Dict, Optional

# Configure basic logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = os.environ.get("EGOS_LOG_LEVEL", "INFO").upper()
LOG_DIR = os.environ.get("EGOS_LOG_DIR", "logs")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)


class KoiosLogger:
    """
    Standardized logger for EGOS components following KOIOS standards.
    Provides structured logging with consistent formatting and context management.
    """

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get a configured logger instance with the specified name.

        Args:
            name: Logger name, typically in format 'SUBSYSTEM.Component'

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)

        # Only configure handlers if not already configured
        if not logger.handlers:
            # Set logger level to capture everything from INFO upwards
            logger.setLevel(logging.INFO)  # Capture INFO and above for the logger itself

            # Create console handler - Set to WARNING level for less terminal noise
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)  # Only show WARNING and above on console
            console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
            logger.addHandler(console_handler)

            # Create file handler - Keep at INFO level for detailed file logs
            log_file = os.path.join(
                LOG_DIR, f"egos_dashboard_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)  # Keep file log detailed
            file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
            logger.addHandler(file_handler)

        return logger

    @staticmethod
    def log_ai_interaction(
        logger: logging.Logger,
        model: str,
        prompt: str,
        response: str,
        parameters: Optional[Dict[str, Any]] = None,
        purpose: str = "",
    ) -> None:
        """
        Log an interaction with an AI model following EGOS AI interaction logging standards.

        Args:
            logger: Logger instance
            model: Name of the AI model used
            prompt: The prompt sent to the model
            response: The response received from the model
            parameters: Parameters used in the API call
            purpose: Purpose of the interaction
        """
        log_context = {
            "model": model,
            "parameters": parameters or {},
            "purpose": purpose,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(
            f"AI Interaction: {purpose}",
            extra={"ai_interaction": log_context, "prompt": prompt, "response": response},
        )

    @staticmethod
    def log_user_action(
        logger: logging.Logger,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous",
    ) -> None:
        """
        Log a user action in the dashboard.

        Args:
            logger: Logger instance
            action: Description of the action taken
            details: Additional details about the action
            user_id: Identifier for the user (default: anonymous)
        """
        log_data = {
            "user_id": user_id,
            "action": action,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"User Action: {action}", extra={"user_action": log_data})

    @staticmethod
    def log_system_event(
        logger: logging.Logger,
        event_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a system event.

        Args:
            logger: Logger instance
            event_type: Type of system event
            message: Description of the event
            details: Additional details about the event
        """
        log_data = {
            "event_type": event_type,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"System Event: {message}", extra={"system_event": log_data})

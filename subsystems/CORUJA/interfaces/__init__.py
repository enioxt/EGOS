"""CORUJA Interfaces

This module defines the interfaces used by the CORUJA subsystem,
including model interfaces and other abstract base classes.
"""

# Export the ModelInterface and related exceptions
from subsystems.CORUJA.interfaces.model_interface import (
    AICommunicationError,
    AIConfigurationError,
    AIError,
    AIResponseError,
    ModelInterface as AIModelInterface,  # Alias for compatibility
)

__all__ = [
    "AIModelInterface",
    "AICommunicationError",
    "AIConfigurationError",
    "AIResponseError",
    "AIError",
]

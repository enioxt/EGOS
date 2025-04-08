"""CORUJA Subsystem - EVA & GUARANI CORUJA (Coordinated Orchestration of Reasoning Units for Joint Assistance)

This subsystem is responsible for coordinating the AI capabilities of the EGOS system,
including prompt management, model interfaces, and orchestration of AI assistants.
"""

# Import and expose key modules
import subsystems.CORUJA.core
import subsystems.CORUJA.interfaces
import subsystems.CORUJA.models

# Define which modules are exposed as part of the public API
__all__ = ["models", "interfaces", "core"]

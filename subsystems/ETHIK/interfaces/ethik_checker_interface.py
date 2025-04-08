"""Defines the abstract interface for ETHIK checking components."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

# Import ModelResponse for type hinting
from subsystems.CORUJA.interfaces.model_interface import ModelResponse

# Import ETHIK exceptions
# Import PDD schema for type hinting guidelines
from subsystems.KOIOS.schemas.pdd_schema import PddEthikGuidelines


class EthikCheckerInterface(ABC):
    """Abstract Base Class for components that perform ethical checks.

    Defines the standard contract for checking input data and model responses
    against ethical guidelines defined in PDDs or system policies.
    """

    @abstractmethod
    def check_and_sanitize_input(
        self,
        data: Dict[str, Any],
        guidelines: Optional[PddEthikGuidelines],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Checks input data against guidelines and potentially sanitizes it.

        Args:
            data: The input data dictionary intended for prompt rendering.
            guidelines: The PddEthikGuidelines object from the relevant PDD,
                        if any.
            context: Request context metadata (e.g., user_id, session_id).

        Returns:
            The (potentially sanitized or modified) input data dictionary.

        Raises:
            EthikViolationError: If an unrecoverable violation is detected in
                                 the input that prevents safe processing
                                 (e.g., forbidden content).
            EthikProcessingError: For other errors during the checking process.
        """
        pass

    @abstractmethod
    def check_and_filter_output(
        self,
        response: ModelResponse,
        guidelines: Optional[PddEthikGuidelines],
        context: Dict[str, Any],
    ) -> ModelResponse:
        """Checks model response against guidelines and potentially filters/modifies it.

        Args:
            response: The ModelResponse object received from the
                      ModelInterface.
            guidelines: The PddEthikGuidelines object from the relevant PDD,
                        if any.
            context: Request context metadata.

        Returns:
            The (potentially filtered or modified) ModelResponse object.
            Modifications might include filtering text, adding warnings, or
            setting the error field.

        Raises:
            EthikProcessingError: For errors during the checking process
                                  (Violations should typically be handled by
                                  modifying the response, not raising).
        """
        pass

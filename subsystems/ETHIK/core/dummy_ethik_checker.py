# subsystems/ETHIK/core/dummy_ethik_checker.py

"""Provides a dummy implementation of the EthikCheckerInterface for testing/development."""

import logging
from typing import Any, Dict, Optional

from subsystems.CORUJA.interfaces.model_interface import ModelResponse

# Import ETHIK exceptions if needed for simulation
from subsystems.ETHIK.interfaces.ethik_checker_interface import EthikCheckerInterface
from subsystems.KOIOS.schemas.pdd_schema import PddEthikGuidelines

# TODO: Replace with KoiosLogger once available and integrated
logger = logging.getLogger(__name__)  # Use __name__ for standard logger naming


class DummyEthikChecker(EthikCheckerInterface):
    """A non-functional placeholder implementation of EthikCheckerInterface.

    Logs calls but does not perform any actual checks or modifications.
    Used for initial integration testing or when ETHIK checks are disabled.
    """

    def __init__(self):
        """Initialize the DummyEthikChecker."""
        logger.info("DummyEthikChecker initialized. No actual checks will be performed.")

    async def check_and_sanitize_input(
        self,
        data: Dict[str, Any],
        guidelines: Optional[PddEthikGuidelines],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Logs the call and returns the input data unmodified."""
        guidelines_present = guidelines is not None
        context_keys = list(context.keys()) if context else []
        logger.debug(
            f"Dummy check_and_sanitize_input called. "
            f"Guidelines present: {guidelines_present}. Context keys: {context_keys}"
        )
        # Example simulation logic (commented out):
        # if guidelines and guidelines.pii_handling == 'error_if_present':
        #     if "sensitive_data_key" in data:
        #         raise EthikViolationError(
        #             "Simulated PII detection", violation_type="PII_DETECTED"
        #         )
        return data

    async def check_and_filter_output(
        self,
        response: ModelResponse,
        guidelines: Optional[PddEthikGuidelines],
        context: Dict[str, Any],
    ) -> ModelResponse:
        """Logs the call and returns the response object unmodified."""
        guidelines_present = guidelines is not None
        context_keys = list(context.keys()) if context else []
        logger.debug(
            f"Dummy check_and_filter_output called. "
            f"Guidelines present: {guidelines_present}. Context keys: {context_keys}"
        )
        # Example simulation logic (commented out):
        # if guidelines and guidelines.forbidden_topics:
        #     if any(topic in response.text for topic in guidelines.forbidden_topics):
        #         logger.warning("Simulated forbidden topic. Filtering response.")
        #         response.text = "[Content filtered by DummyEthikChecker]"
        #         response.error = "Content matched forbidden topic guideline."
        #         response.finish_reason = "content_filter_ethik"
        return response

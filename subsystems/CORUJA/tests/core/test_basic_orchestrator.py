# subsystems/CORUJA/tests/core/test_basic_orchestrator.py

"""Unit tests for the BasicOrchestrator."""

import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Imports for classes under test and dependencies
from subsystems.CORUJA.core.basic_orchestrator import BasicOrchestrator
from subsystems.CORUJA.core.prompt_manager import PddNotFoundError, PromptManager
from subsystems.CORUJA.interfaces import AIModelInterface
from subsystems.CORUJA.interfaces.model_interface import (
    ModelApiException,
    ModelResponse,
    ModelSafetyError,
)
from subsystems.ETHIK.exceptions import EthikViolationError
from subsystems.ETHIK.interfaces.ethik_checker_interface import EthikCheckerInterface
from subsystems.KOIOS.schemas.pdd_schema import (
    PddMetadata,
    PddParameter,
    PromptDesignDocument,
)

# --- Add project root to PYTHONPATH --- Start ---
# This needs to happen before tests run if not running via discover from root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# --- Add project root to PYTHONPATH --- End -----


# Mock KoiosLogger to prevent actual logging during tests
mock_logger = MagicMock()

# Dummy classes or mocks for dependencies


# Test Suite
class TestBasicOrchestrator(unittest.TestCase):
    """Test suite for the BasicOrchestrator."""

    # --- Removed Inner Mock Class Definitions --- #

    def setUp(self):
        """Set up common test resources."""
        # Use MagicMock with spec for dependencies
        self.mock_prompt_manager = MagicMock(spec=PromptManager)
        # Use AsyncMock for the model interface as it has async methods
        self.mock_model_interface = AsyncMock(spec=AIModelInterface)
        self.mock_ethik_checker = MagicMock(spec=EthikCheckerInterface)

        # Patch KoiosLogger to avoid actual logging during tests
        self.patcher = patch("subsystems.CORUJA.core.basic_orchestrator.KoiosLogger")
        self.mock_koios_logger_class = self.patcher.start()
        self.mock_logger_instance = MagicMock()
        self.mock_koios_logger_class.get_logger.return_value = self.mock_logger_instance

        # Create a default PDD for testing
        self.test_pdd = PromptDesignDocument(
            id="test_pdd_v1",
            name="Test PDD",
            description="A PDD for testing purposes.",
            version="1.0",
            parameters=[
                PddParameter(name="input_text", description="Input", type="string", required=True),
                PddParameter(
                    name="max_length",
                    description="Max len",
                    type="integer",
                    required=False,
                    default=100,
                ),
            ],
            template="Summarize: {input_text} in {max_length} words.",
            model_configuration={"temperature": 0.8},  # Use renamed field
            metadata=PddMetadata(),  # Use dummy if PddMetadata not imported
        )
        # Ensure metadata is a dict if the class definition failed
        if not isinstance(self.test_pdd.metadata, dict):
            self.test_pdd.metadata = {}
        self.test_pdd.ethik_guidelines = None  # Add if not present in dummy

        # Create a default successful model response
        self.success_model_response = ModelResponse(
            text="Successful summary.", model_name="test_model", finish_reason="stop"
        )

        # Configure default mock returns directly on mock methods
        self.mock_prompt_manager.get_pdd.return_value = self.test_pdd
        # For AsyncMock, return_value is used directly for the awaitable result
        self.mock_model_interface.execute_prompt.return_value = self.success_model_response
        # Configure pass-through behavior for ETHIK checker by default
        self.mock_ethik_checker.check_and_sanitize_input.side_effect = (
            lambda data, *args, **kwargs: data
        )
        self.mock_ethik_checker.check_and_filter_output.side_effect = (
            lambda response, *args, **kwargs: response
        )

    def tearDown(self):
        """Clean up resources after tests."""
        self.patcher.stop()

    # --- Initialization Tests ---

    def test_initialization_success(self):
        """Test successful initialization."""
        orchestrator = BasicOrchestrator(
            prompt_manager=self.mock_prompt_manager,
            model_interface=self.mock_model_interface,
            ethik_checker=self.mock_ethik_checker,
        )
        self.assertIsNotNone(orchestrator)
        self.assertEqual(orchestrator.prompt_manager, self.mock_prompt_manager)
        self.assertEqual(orchestrator.model_interface, self.mock_model_interface)
        self.assertEqual(orchestrator.ethik_checker, self.mock_ethik_checker)
        self.mock_koios_logger_class.get_logger.assert_called_once_with("CORUJA.BasicOrchestrator")
        self.mock_logger_instance.info.assert_called()

    def test_initialization_no_ethik(self):
        """Test successful initialization without an ETHIK checker."""
        orchestrator = BasicOrchestrator(
            prompt_manager=self.mock_prompt_manager,
            model_interface=self.mock_model_interface,
            ethik_checker=None,
        )
        self.assertIsNotNone(orchestrator)
        self.assertIsNone(orchestrator.ethik_checker)
        self.mock_logger_instance.info.assert_called()

    def test_initialization_missing_prompt_manager(self):
        """Test ValueError if PromptManager is missing."""
        with self.assertRaises(ValueError):
            BasicOrchestrator(prompt_manager=None, model_interface=self.mock_model_interface)

    def test_initialization_missing_model_interface(self):
        """Test ValueError if ModelInterface is missing."""
        with self.assertRaises(ValueError):
            BasicOrchestrator(prompt_manager=self.mock_prompt_manager, model_interface=None)

    # --- Process Request - Standard Path Tests ---

    @patch(
        "subsystems.CORUJA.core.basic_orchestrator.BasicOrchestrator._validate_parameters",
        return_value={"input_text": "Test input", "max_length": 50},
    )
    @patch(
        "subsystems.CORUJA.core.basic_orchestrator.BasicOrchestrator._render_prompt",
        return_value="Rendered prompt",
    )
    @patch("subsystems.CORUJA.core.basic_orchestrator.BasicOrchestrator._log_interaction")
    def test_process_request_success_standard_path(self, mock_log, mock_render, mock_validate):
        """Test the successful processing flow for the standard LLM path."""
        orchestrator = BasicOrchestrator(
            prompt_manager=self.mock_prompt_manager,
            model_interface=self.mock_model_interface,
            ethik_checker=self.mock_ethik_checker,
        )

        input_data = {"input_text": "Test input"}
        runtime_params = {"temperature": 0.9}  # Override PDD temp
        request_context = {"user_id": "test_user"}

        async def run_test():
            response = await orchestrator.process_request(
                pdd_id="test_pdd_v1",
                input_data=input_data,
                model_params=runtime_params,
                request_context=request_context,
            )

            # Assertions
            self.assertEqual(response, self.success_model_response)
            self.assertIsNone(response.error)

            # Check mock calls
            self.mock_prompt_manager.get_pdd.assert_called_once_with("test_pdd_v1")
            mock_validate.assert_called_once_with(self.test_pdd.parameters, input_data)
            # Check ETHIK input call args
            self.mock_ethik_checker.check_and_sanitize_input.assert_called_once_with(
                data=mock_validate.return_value,  # Check it got the validated params
                guidelines=self.test_pdd.ethik_guidelines,
                context=request_context,  # Check original context was passed
            )
            mock_render.assert_called_once_with(
                self.test_pdd.template,
                # Use the *return value* of the validated parameters mock,
                # as that's what the sanitize side_effect returns.
                mock_validate.return_value,
            )
            self.mock_model_interface.execute_prompt.assert_called_once()
            # Check merged params passed to execute_prompt
            call_args, call_kwargs = self.mock_model_interface.execute_prompt.call_args
            expected_merged_params = {
                "temperature": 0.9,
                "max_output_tokens": 1024,  # Assuming default is applied
            }
            self.assertEqual(call_kwargs.get("params"), expected_merged_params)
            self.assertEqual(call_kwargs.get("prompt"), "Rendered prompt")
            # Check context passed to model (should include pdd_id and original context)
            expected_model_context = {
                "pdd_id": "test_pdd_v1",
                "pdd_version": self.test_pdd.version,
                **request_context,  # Merge original context
            }
            self.assertEqual(call_kwargs.get("context"), expected_model_context)

            # Check ETHIK output call args
            self.mock_ethik_checker.check_and_filter_output.assert_called_once_with(
                response=self.success_model_response,  # Check it got the raw model response
                guidelines=self.test_pdd.ethik_guidelines,
                context=expected_model_context,  # Check augmented context was passed
            )
            # Check log interaction call
            mock_log.assert_called_once_with(
                self.test_pdd,  # pdd
                mock_validate.return_value,  # input_data
                expected_merged_params,  # model_params
                self.success_model_response,  # response
                expected_model_context,  # context
            )

        asyncio.run(run_test())

    # --- Process Request - Error Handling Tests ---

    def test_process_request_pdd_not_found(self):
        """Test handling when the requested PDD is not found."""
        self.mock_prompt_manager.get_pdd.side_effect = PddNotFoundError("test_pdd_v1")
        orchestrator = BasicOrchestrator(self.mock_prompt_manager, self.mock_model_interface)

        async def run_test():
            response = await orchestrator.process_request("test_pdd_v1", {"input_text": ""})
            self.assertIsNotNone(response.error)
            self.assertIn("PDD not found", response.error)
            self.mock_logger_instance.error.assert_called_once()

        asyncio.run(run_test())

    @patch(
        "subsystems.CORUJA.core.basic_orchestrator.BasicOrchestrator._validate_parameters",
        side_effect=ValueError("Missing required param"),
    )
    def test_process_request_validation_error(self, mock_validate):
        """Test handling of input validation errors."""
        orchestrator = BasicOrchestrator(self.mock_prompt_manager, self.mock_model_interface)

        async def run_test():
            response = await orchestrator.process_request("test_pdd_v1", {"wrong_param": ""})
            self.assertIsNotNone(response.error)
            self.assertIn("Input/Template error", response.error)
            self.assertIn("Missing required param", response.error)
            self.mock_logger_instance.error.assert_called_once()

        asyncio.run(run_test())

    def test_process_request_pre_ethik_violation(self):
        """Test handling of pre-prompt ETHIK violations."""
        self.mock_ethik_checker.check_and_sanitize_input.side_effect = EthikViolationError(
            "PII detected"
        )
        orchestrator = BasicOrchestrator(
            self.mock_prompt_manager, self.mock_model_interface, self.mock_ethik_checker
        )

        async def run_test():
            response = await orchestrator.process_request(
                "test_pdd_v1", {"input_text": "Contains PII"}
            )
            self.assertIsNotNone(response.error)
            self.assertIn("ETHIK input violation", response.error)
            self.assertEqual(response.finish_reason, "ethik_violation_input")
            self.mock_logger_instance.warning.assert_called()

        asyncio.run(run_test())

    @patch(
        "subsystems.CORUJA.core.basic_orchestrator.BasicOrchestrator._validate_parameters",
        return_value={"input_text": "Test"},
    )
    @patch(
        "subsystems.CORUJA.core.basic_orchestrator.BasicOrchestrator._render_prompt",
        return_value="Rendered",
    )
    def test_process_request_model_safety_error(self, mock_render, mock_validate):
        """Test handling of ModelSafetyError from the model interface."""
        self.mock_model_interface.execute_prompt.side_effect = ModelSafetyError("Content blocked")
        orchestrator = BasicOrchestrator(self.mock_prompt_manager, self.mock_model_interface)

        async def run_test():
            response = await orchestrator.process_request("test_pdd_v1", {"input_text": "Risky"})
            self.assertIsNotNone(response.error)
            self.assertIn("Content safety issue", response.error)
            self.mock_logger_instance.warning.assert_called()

        asyncio.run(run_test())

    @patch(
        "subsystems.CORUJA.core.basic_orchestrator.BasicOrchestrator._validate_parameters",
        return_value={"input_text": "Test"},
    )
    @patch(
        "subsystems.CORUJA.core.basic_orchestrator.BasicOrchestrator._render_prompt",
        return_value="Rendered",
    )
    def test_process_request_model_api_error(self, mock_render, mock_validate):
        """Test handling of ModelApiException from the model interface."""
        self.mock_model_interface.execute_prompt.side_effect = ModelApiException(
            "Connection failed"
        )
        orchestrator = BasicOrchestrator(self.mock_prompt_manager, self.mock_model_interface)

        async def run_test():
            response = await orchestrator.process_request("test_pdd_v1", {"input_text": "Normal"})
            self.assertIsNotNone(response.error)
            self.assertIn("Model API error", response.error)
            self.assertIn("Connection failed", response.error)
            self.mock_logger_instance.error.assert_called()

        asyncio.run(run_test())

    @patch(
        "subsystems.CORUJA.core.basic_orchestrator.BasicOrchestrator._validate_parameters",
        return_value={"input_text": "Test"},
    )
    @patch(
        "subsystems.CORUJA.core.basic_orchestrator.BasicOrchestrator._render_prompt",
        return_value="Rendered",
    )
    def test_process_request_post_ethik_error_flagged(self, mock_render, mock_validate):
        """Test handling when post-response ETHIK flags an error."""

        # Define a side effect function for the mock
        def mock_filter_output(response, *args, **kwargs):
            # Modify the response object passed in
            response.text = "Filtered content"
            response.error = "Output violated policy X"
            response.finish_reason = "ethik_violation_output"
            # We don't explicitly set pdd_id here, assuming it's already on the response
            return response  # Return the modified original object

        # Set the side effect for the mock
        self.mock_ethik_checker.check_and_filter_output.side_effect = mock_filter_output
        orchestrator = BasicOrchestrator(
            self.mock_prompt_manager, self.mock_model_interface, self.mock_ethik_checker
        )

        # Expected state of the original response object *after* modification
        expected_modified_response = self.success_model_response  # Start with the original
        expected_modified_response.text = "Filtered content"
        expected_modified_response.error = "Output violated policy X"
        expected_modified_response.finish_reason = "ethik_violation_output"

        async def run_test():
            response = await orchestrator.process_request("test_pdd_v1", {"input_text": "Test"})
            # Assert against the expected state of the *modified* original response
            self.assertEqual(response, expected_modified_response)
            self.assertIsNotNone(response.error)
            self.assertEqual(response.finish_reason, "ethik_violation_output")
            # Check that the original response object was indeed passed to the mock
            self.mock_ethik_checker.check_and_filter_output.assert_called_once_with(
                response=self.success_model_response,  # Check it got the original obj
                guidelines=self.test_pdd.ethik_guidelines,
                context=unittest.mock.ANY,  # Context might have been augmented
            )

        asyncio.run(run_test())

    # --- TODO: Add tests for Specialized Handler Path ---
    # These would involve mocking the handler import and its process method.
    # Example skeleton:
    # @patch(
    #     'subsystems.CORUJA.core.basic_orchestrator.importlib.import_module'
    # ) # If dynamic import is used
    # def test_process_request_specialized_handler_success(...):
    #     # Setup PDD with handler_type='specialized_crew' and handler_reference
    #     # Mock the handler class and its process method
    #     # Assert handler.process is called, check final response


if __name__ == "__main__":
    unittest.main()

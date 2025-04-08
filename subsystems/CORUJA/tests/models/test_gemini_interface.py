# subsystems/CORUJA/tests/models/test_gemini_interface.py
"""
Unit tests for the GeminiModelInterface.
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Add project root to PYTHONPATH to ensure modules can be found
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Define mock objects for Google's libraries and APIs
mock_genai = MagicMock()
mock_genai_types = MagicMock()
mock_genai.types = mock_genai_types
mock_generative_model_instance = MagicMock()
mock_genai.GenerativeModel.return_value = mock_generative_model_instance


# Define mock exception types for Google API exceptions
class MockGoogleAPIError(Exception):
    """Base mock exception for Google API errors."""

    pass


class MockPermissionDenied(MockGoogleAPIError):
    """Mock exception for permission denied errors."""

    pass


class MockResourceExhausted(MockGoogleAPIError):
    """Mock exception for resource exhausted (rate limit) errors."""

    pass


class MockInvalidArgument(MockGoogleAPIError):
    """Mock exception for invalid argument errors."""

    pass


class MockDeadlineExceeded(MockGoogleAPIError):
    """Mock exception for timeout errors."""

    pass


# Create a mock for google_exceptions module
mock_google_exceptions = MagicMock()
mock_google_exceptions.GoogleAPIError = MockGoogleAPIError
mock_google_exceptions.PermissionDenied = MockPermissionDenied
mock_google_exceptions.ResourceExhausted = MockResourceExhausted
mock_google_exceptions.InvalidArgument = MockInvalidArgument
mock_google_exceptions.DeadlineExceeded = MockDeadlineExceeded


# Apply patches to replace actual modules with mocks in the target module
@patch.dict(os.environ, {"GOOGLE_API_KEY": "test_api_key"}, clear=True)
@patch("subsystems.CORUJA.models.gemini_interface.genai", mock_genai)
@patch("subsystems.CORUJA.models.gemini_interface.google_exceptions", mock_google_exceptions)
@patch("subsystems.CORUJA.models.gemini_interface.GOOGLE_AI_AVAILABLE", True)
class TestGeminiModelInterface(unittest.TestCase):
    """Test suite for GeminiModelInterface."""

    def setUp(self):
        """Reset mocks before each test."""
        mock_genai.reset_mock()
        mock_generative_model_instance.reset_mock()
        mock_google_exceptions.reset_mock()

        # Set default mock behaviors
        mock_generative_model_instance.generate_content_async = AsyncMock()
        mock_generative_model_instance.count_tokens = MagicMock(
            return_value=MagicMock(total_tokens=10)
        )

    # --- Initialization Tests --- #

    def test_initialization_success(
        self, mock_GOOGLE_AI_AVAILABLE, mock_google_exceptions, mock_genai
    ):
        """Test successful initialization with API key."""
        from subsystems.CORUJA.models.gemini_interface import GeminiModelInterface

        interface = GeminiModelInterface(api_key="test_key")
        mock_genai.configure.assert_called_once_with(api_key="test_key")
        mock_genai.GenerativeModel.assert_called_once()
        self.assertEqual(interface.model_name, GeminiModelInterface.DEFAULT_MODEL_NAME)

    def test_initialization_success_with_env_var(
        self, mock_GOOGLE_AI_AVAILABLE, mock_google_exceptions, mock_genai
    ):
        """Test successful initialization using environment variable API key."""
        from subsystems.CORUJA.models.gemini_interface import GeminiModelInterface

        interface = GeminiModelInterface(api_key=None, model_name="gemini-test-model")
        mock_genai.configure.assert_called_once_with(api_key="test_api_key")
        mock_genai.GenerativeModel.assert_called_once_with("gemini-test-model")
        self.assertEqual(interface.model_name, "gemini-test-model")

    @patch.dict(os.environ, {}, clear=True)  # Clear env var for this test only
    def test_initialization_no_api_key(
        self, mock_env, mock_GOOGLE_AI_AVAILABLE, mock_google_exceptions, mock_genai
    ):
        """Test initialization fails if no API key is provided or found."""
        from subsystems.CORUJA.models.gemini_interface import (
            AIConfigurationError,
            GeminiModelInterface,
        )

        with self.assertRaises(AIConfigurationError):
            GeminiModelInterface(api_key=None)

    @patch("subsystems.CORUJA.models.gemini_interface.GOOGLE_AI_AVAILABLE", False)
    def test_initialization_library_not_available(
        self, mock_patch_available, mock_GOOGLE_AI_AVAILABLE, mock_google_exceptions, mock_genai
    ):
        """Test initialization fails if google-generativeai is not installed."""
        from subsystems.CORUJA.models.gemini_interface import (
            AIConfigurationError,
            GeminiModelInterface,
        )

        with self.assertRaises(AIConfigurationError):
            GeminiModelInterface(api_key="test_key")

    def test_initialization_permission_denied(
        self, mock_GOOGLE_AI_AVAILABLE, mock_google_exceptions, mock_genai
    ):
        """Test initialization handles PermissionDenied during model init."""
        from subsystems.CORUJA.models.gemini_interface import (
            AIConfigurationError,
            GeminiModelInterface,
        )

        # Use the mock exception defined above
        mock_genai.GenerativeModel.side_effect = mock_google_exceptions.PermissionDenied(
            "mock permission denied"
        )

        with self.assertRaises(AIConfigurationError):
            GeminiModelInterface(api_key="test_key")

    # --- generate_response Tests --- #

    def test_generate_response_success(
        self, mock_GOOGLE_AI_AVAILABLE, mock_google_exceptions, mock_genai
    ):
        """Test successful response generation."""
        from subsystems.CORUJA.models.gemini_interface import GeminiModelInterface

        interface = GeminiModelInterface(api_key="test_key")

        # Configure the mock response object
        mock_response = MagicMock()
        mock_response.parts = [MagicMock(text="Generated Content")]
        mock_response.prompt_feedback = None
        mock_generative_model_instance.generate_content_async.return_value = mock_response

        # Mock the candidate structure
        mock_candidate = MagicMock()
        mock_candidate.finish_reason.name = "STOP"
        mock_candidate.content.parts = [MagicMock(text="Generated Content")]
        mock_response.candidates = [mock_candidate]

        async def run_test():
            response = await interface.generate_response("Test Prompt")
            self.assertEqual(response, "Generated Content")
            mock_generative_model_instance.generate_content_async.assert_called_once()

        asyncio.run(run_test())

    def test_generate_response_with_params(
        self, mock_GOOGLE_AI_AVAILABLE, mock_google_exceptions, mock_genai
    ):
        """Test generation with specific parameters like temperature."""
        from subsystems.CORUJA.models.gemini_interface import GeminiModelInterface

        interface = GeminiModelInterface(api_key="test_key")

        # Configure mock response
        mock_response = MagicMock()
        mock_candidate = MagicMock()
        mock_candidate.finish_reason.name = "STOP"
        mock_candidate.content.parts = [MagicMock(text="Generated with params")]
        mock_response.candidates = [mock_candidate]
        mock_response.prompt_feedback = None
        mock_generative_model_instance.generate_content_async.return_value = mock_response

        async def run_test():
            # Pass generation parameters
            response = await interface.generate_response(
                "Test Prompt", temperature=0.7, max_output_tokens=200
            )
            self.assertEqual(response, "Generated with params")

            # Check that generate_content_async was called
            mock_generative_model_instance.generate_content_async.assert_called_once()

        # Use standard mocking rather than patching generation config constructor
        asyncio.run(run_test())

    def test_generate_response_safety_block(
        self, mock_GOOGLE_AI_AVAILABLE, mock_google_exceptions, mock_genai
    ):
        """Test handling of safety-blocked prompts."""
        from subsystems.CORUJA.models.gemini_interface import (
            AIResponseError,
            GeminiModelInterface,
            ModelSafetyError,
        )

        interface = GeminiModelInterface(api_key="test_key")

        # Create mock response with safety block
        mock_response = MagicMock()
        mock_feedback = MagicMock()
        mock_feedback.block_reason.name = "SAFETY"
        mock_response.prompt_feedback = mock_feedback
        mock_response.candidates = []
        mock_generative_model_instance.generate_content_async.return_value = mock_response

        # Make execute_prompt raise ModelSafetyError which is caught in generate_response
        mock_generative_model_instance.generate_content_async.side_effect = ModelSafetyError(
            "Safety block"
        )

        async def run_test():
            with self.assertRaises(AIResponseError):
                await interface.generate_response("Blocked Prompt")

        asyncio.run(run_test())

    def test_generate_response_api_error(
        self, mock_GOOGLE_AI_AVAILABLE, mock_google_exceptions, mock_genai
    ):
        """Test handling of API errors."""
        from subsystems.CORUJA.models.gemini_interface import (
            AICommunicationError,
            GeminiModelInterface,
        )

        interface = GeminiModelInterface(api_key="test_key")

        # Simulate API error
        mock_generative_model_instance.generate_content_async.side_effect = (
            mock_google_exceptions.GoogleAPIError("API error")
        )

        async def run_test():
            with self.assertRaises(AICommunicationError):
                await interface.generate_response("Error Prompt")

        asyncio.run(run_test())

    def test_generate_response_timeout(
        self, mock_GOOGLE_AI_AVAILABLE, mock_google_exceptions, mock_genai
    ):
        """Test handling of timeout errors."""
        from subsystems.CORUJA.models.gemini_interface import (
            AICommunicationError,
            GeminiModelInterface,
        )

        interface = GeminiModelInterface(api_key="test_key")

        # Simulate timeout error
        mock_generative_model_instance.generate_content_async.side_effect = (
            mock_google_exceptions.DeadlineExceeded("Timeout")
        )

        async def run_test():
            with self.assertRaises(AICommunicationError):
                await interface.generate_response("Timeout Prompt")

        asyncio.run(run_test())

    def test_generate_response_rate_limit(
        self, mock_GOOGLE_AI_AVAILABLE, mock_google_exceptions, mock_genai
    ):
        """Test handling of rate limit errors."""
        from subsystems.CORUJA.models.gemini_interface import AIResponseError, GeminiModelInterface

        interface = GeminiModelInterface(api_key="test_key")

        # Simulate rate limit error
        mock_generative_model_instance.generate_content_async.side_effect = (
            mock_google_exceptions.ResourceExhausted("Rate limit")
        )

        async def run_test():
            with self.assertRaises(AIResponseError):
                await interface.generate_response("Rate Limited Prompt")

        asyncio.run(run_test())

    # --- count_tokens Tests --- #

    def test_count_tokens_success(
        self, mock_GOOGLE_AI_AVAILABLE, mock_google_exceptions, mock_genai
    ):
        """Test successful token counting."""
        from subsystems.CORUJA.models.gemini_interface import GeminiModelInterface

        interface = GeminiModelInterface(api_key="test_key")
        mock_token_count_response = MagicMock(total_tokens=42)
        mock_generative_model_instance.count_tokens.return_value = mock_token_count_response

        token_count = interface.count_tokens("Some text")
        self.assertEqual(token_count, 42)
        mock_generative_model_instance.count_tokens.assert_called_once_with("Some text")

    def test_count_tokens_api_error(
        self, mock_GOOGLE_AI_AVAILABLE, mock_google_exceptions, mock_genai
    ):
        """Test token counting handles GoogleAPIError."""
        from subsystems.CORUJA.models.gemini_interface import (
            AICommunicationError,
            GeminiModelInterface,
        )

        interface = GeminiModelInterface(api_key="test_key")
        mock_generative_model_instance.count_tokens.side_effect = (
            mock_google_exceptions.GoogleAPIError("mock API error")
        )

        with self.assertRaises(AICommunicationError):
            interface.count_tokens("Some text")

    @patch("subsystems.CORUJA.models.gemini_interface.GOOGLE_AI_AVAILABLE", False)
    def test_count_tokens_library_not_available(
        self, mock_patch_available, mock_GOOGLE_AI_AVAILABLE, mock_google_exceptions, mock_genai
    ):
        """Test count_tokens fails if google-generativeai is not installed."""
        from subsystems.CORUJA.models.gemini_interface import (
            AIConfigurationError,
            GeminiModelInterface,
        )

        interface = GeminiModelInterface(api_key="test_key")
        with self.assertRaises(AIConfigurationError):
            interface.count_tokens("Some text")


if __name__ == "__main__":
    unittest.main()

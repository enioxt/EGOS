"""Unit tests for the BasicEthikChecker."""

import pytest

from subsystems.CORUJA.interfaces.model_interface import ModelResponse
from subsystems.ETHIK.core.basic_ethik_checker import BasicEthikChecker
from subsystems.ETHIK.exceptions import EthikViolationError
from subsystems.KOIOS.schemas.pdd_schema import PddEthikGuidelines

# --- Test Fixtures ---


@pytest.fixture
def checker() -> BasicEthikChecker:
    """Provides a BasicEthikChecker instance for testing."""
    return BasicEthikChecker()


@pytest.fixture
def allow_all_guidelines() -> PddEthikGuidelines:
    """Guidelines that permit all PII and have no forbidden topics."""
    return PddEthikGuidelines(pii_handling="allow", forbidden_topics=[])


@pytest.fixture
def error_on_pii_guidelines() -> PddEthikGuidelines:
    """Guidelines that raise an error if PII is detected."""
    return PddEthikGuidelines(pii_handling="error_if_present", forbidden_topics=[])


@pytest.fixture
def redact_pii_guidelines() -> PddEthikGuidelines:
    """Guidelines that redact PII if detected."""
    return PddEthikGuidelines(pii_handling="redact_if_strict", forbidden_topics=[])


@pytest.fixture
def log_only_pii_guidelines() -> PddEthikGuidelines:
    """Guidelines that only log PII detection."""
    return PddEthikGuidelines(pii_handling="log_only", forbidden_topics=[])


@pytest.fixture
def block_keywords_guidelines() -> PddEthikGuidelines:
    """Guidelines that block specific keywords."""
    return PddEthikGuidelines(pii_handling="allow", forbidden_topics=["secret project", "badword"])


@pytest.fixture
def mock_context() -> dict:
    """Provides a simple mock context dictionary."""
    return {"pdd_id": "test_pdd_123", "user_id": "test_user"}


# --- Test Cases ---


class TestBasicEthikCheckerInput:
    """Tests for the check_and_sanitize_input method."""

    def test_input_no_guidelines(self, checker, mock_context):
        input_data = {"text": "Hello world"}
        result = checker.check_and_sanitize_input(input_data, None, mock_context)
        assert result == input_data  # Should return original data

    def test_input_allow_all_clean(self, checker, allow_all_guidelines, mock_context):
        input_data = {"text": "This is clean text."}
        result = checker.check_and_sanitize_input(input_data, allow_all_guidelines, mock_context)
        assert result == input_data

    def test_input_allow_all_with_pii(self, checker, allow_all_guidelines, mock_context):
        input_data = {"email": "test@example.com", "phone": "123-456-7890"}
        result = checker.check_and_sanitize_input(input_data, allow_all_guidelines, mock_context)
        assert result == input_data  # PII allowed, data unchanged

    def test_input_error_on_pii_clean(self, checker, error_on_pii_guidelines, mock_context):
        input_data = {"text": "Clean input."}
        result = checker.check_and_sanitize_input(input_data, error_on_pii_guidelines, mock_context)
        assert result == input_data

    def test_input_error_on_pii_present(self, checker, error_on_pii_guidelines, mock_context):
        input_data = {"details": "My email is test@example.com"}
        with pytest.raises(EthikViolationError) as exc_info:
            checker.check_and_sanitize_input(input_data, error_on_pii_guidelines, mock_context)
        assert "PII (EMAIL) detected" in str(exc_info.value)
        assert exc_info.value.violation_type == "INPUT_VIOLATION"

    def test_input_redact_pii_clean(self, checker, redact_pii_guidelines, mock_context):
        input_data = {"text": "No PII here."}
        result = checker.check_and_sanitize_input(input_data, redact_pii_guidelines, mock_context)
        assert result == input_data

    def test_input_redact_pii_present(self, checker, redact_pii_guidelines, mock_context):
        input_data = {"contact": "Reach me at test@example.com or 555-123-4567."}
        expected_redacted = "Reach me at [EMAIL_REDACTED] or [PHONE_USA_REDACTED]."
        result = checker.check_and_sanitize_input(input_data, redact_pii_guidelines, mock_context)
        assert result["contact"] == expected_redacted

    def test_input_log_only_pii_present(self, checker, log_only_pii_guidelines, mock_context):
        # We can't easily test the log output here without more complex mocking,
        # but we verify the data is unchanged and no error is raised.
        input_data = {"email": "logger@example.com"}
        result = checker.check_and_sanitize_input(input_data, log_only_pii_guidelines, mock_context)
        assert result == input_data  # Data should be unchanged

    def test_input_no_forbidden_keywords(self, checker, block_keywords_guidelines, mock_context):
        input_data = {"topic": "Discussing public features."}
        result = checker.check_and_sanitize_input(
            input_data, block_keywords_guidelines, mock_context
        )
        assert result == input_data

    def test_input_with_forbidden_keywords(self, checker, block_keywords_guidelines, mock_context):
        input_data = {"comment": "This involves the secret project."}
        with pytest.raises(EthikViolationError) as exc_info:
            checker.check_and_sanitize_input(input_data, block_keywords_guidelines, mock_context)
        assert "Forbidden keyword(s) (secret project) detected" in str(exc_info.value)
        assert exc_info.value.violation_type == "INPUT_VIOLATION"

    def test_input_uses_default_keywords_if_none_in_guidelines(self, checker, mock_context):
        # Guidelines allow PII but don't specify forbidden topics
        guidelines = PddEthikGuidelines(pii_handling="allow", forbidden_topics=None)
        input_data = {"text": "Planning some illegal activity."}  # Matches default keyword
        with pytest.raises(EthikViolationError) as exc_info:
            checker.check_and_sanitize_input(input_data, guidelines, mock_context)
        assert "illegal activity" in str(exc_info.value)


class TestBasicEthikCheckerOutput:
    """Tests for the check_and_filter_output method."""

    def test_output_no_guidelines(self, checker, mock_context):
        response = ModelResponse(text="Some output text.")
        result = checker.check_and_filter_output(response, None, mock_context)
        assert result == response  # Should return original response
        assert result.error is None
        assert result.finish_reason is None  # Or original if it had one

    def test_output_no_text(self, checker, block_keywords_guidelines, mock_context):
        response = ModelResponse(text="")  # Empty text
        result = checker.check_and_filter_output(response, block_keywords_guidelines, mock_context)
        assert result == response

    def test_output_allow_all_clean(self, checker, allow_all_guidelines, mock_context):
        response = ModelResponse(text="Perfectly fine output.")
        result = checker.check_and_filter_output(response, allow_all_guidelines, mock_context)
        assert result == response

    def test_output_block_keywords_clean(self, checker, block_keywords_guidelines, mock_context):
        response = ModelResponse(text="This output is acceptable.")
        result = checker.check_and_filter_output(response, block_keywords_guidelines, mock_context)
        assert result == response

    def test_output_block_keywords_present(self, checker, block_keywords_guidelines, mock_context):
        response = ModelResponse(text="This mentions the secret project.")
        result = checker.check_and_filter_output(response, block_keywords_guidelines, mock_context)
        assert result.text == "[Output filtered due to content policy violation]"
        assert "secret project" in result.error
        assert result.finish_reason == "content_filter_ethik"

    def test_output_uses_default_keywords(self, checker, mock_context):
        # Guidelines allow PII but don't specify forbidden topics
        guidelines = PddEthikGuidelines(pii_handling="allow", forbidden_topics=None)
        response = ModelResponse(text="Output includes hate speech example.")  # Matches default
        result = checker.check_and_filter_output(response, guidelines, mock_context)
        assert result.text == "[Output filtered due to content policy violation]"
        assert "hate speech" in result.error
        assert result.finish_reason == "content_filter_ethik"

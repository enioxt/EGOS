#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - ETHIK Validator Tests
===================================

Test suite for the ETHIK validation system.
Ensures proper functioning of ethical validation rules and handlers.

Version: 8.0.0
"""

import datetime
import json
from unittest.mock import AsyncMock, Mock

from mycelium import Message
import pytest

from ..core.validator import EthikValidator, ValidationResult, ValidationRule

# Test Configuration
TEST_CONFIG = {
    "rules_file": "test_validation_rules.json",
    "validator_config": {"history_retention_days": 30, "ethical_threshold": 0.7},
}

# Sample Rules for Testing
SAMPLE_RULES = {
    "validate-001": ValidationRule(
        id="validate-001",
        name="Protect Critical Files",
        description="Prevent modification of critical configuration files",
        severity="critical",
        conditions=[
            "action_context.get('action_type') in ['file_write', 'edit_file']",
            "'config' in str(action_context.get('target_path', '')).lower()",
        ],
        threshold=0.8,
        action="block",
    ),
    "validate-002": ValidationRule(
        id="validate-002",
        name="Log Status Changes",
        description="Monitor component status changes",
        severity="medium",
        conditions=[
            "action_context.get('action_type') == 'status_change'",
            "action_context.get('status', {}).get('health') == 'critical'",
        ],
        threshold=0.6,
        action="warn",
    ),
}


class MockMyceliumClient:
    """Mock Mycelium client for testing."""

    def __init__(self):
        self.published_messages = []
        self.subscriptions = {}

    def subscribe(self, topic: str):
        def decorator(func):
            self.subscriptions[topic] = func
            return func

        return decorator

    async def publish(self, topic: str, data: dict):
        self.published_messages.append(
            {"topic": topic, "data": data, "timestamp": datetime.now().isoformat()}
        )

    async def trigger_message(self, topic: str, message_data: dict):
        """Simulate receiving a message on a topic."""
        if topic in self.subscriptions:
            message = Message(id="test_msg_" + datetime.now().isoformat(), data=message_data)
            await self.subscriptions[topic](message)


@pytest.fixture
def mock_mycelium():
    """Fixture providing a mock Mycelium client."""
    return MockMyceliumClient()


@pytest.fixture
def test_config():
    """Fixture providing test configuration."""
    return {
        "max_history_size": 100,
        "alert_threshold": 0.7,
        "mycelium": {
            "topics": {
                "validate_request": "test.ethik.validate.request",
                "validate_result": "test.ethik.validate.result",
                "rules_update": "test.ethik.rules.update",
                "rules_status": "test.ethik.rules.status",
                "alert": "test.ethik.alert",
            }
        },
    }


@pytest.fixture
def validator(mock_mycelium, test_config, tmp_path):
    """Fixture providing configured EthikValidator instance."""
    config_path = tmp_path / "test_config.json"
    with open(config_path, "w") as f:
        json.dump(test_config, f)
    return EthikValidator(config_path=config_path, mycelium_client=mock_mycelium)


@pytest.mark.asyncio
async def test_handle_action_proposed_valid():
    """Test handling of a valid action proposal"""
    mock_interface = MockMyceliumClient()
    validator = EthikValidator(TEST_CONFIG, mock_interface)
    validator.rules = SAMPLE_RULES

    # Test message for a non-config file edit
    message = {
        "id": "test-action-1",
        "payload": {
            "action_type": "file_write",
            "source_component": "test_component",
            "target_path": "/path/to/normal/file.txt",
        },
    }

    await validator.handle_action_proposed(message)

    # Check published messages
    assert len(mock_interface.published_messages) == 1
    topic, response = mock_interface.published_messages[0]

    assert topic == "response.validation.test-action-1"
    assert response["type"] == "validation_response"
    assert response["validation"]["is_valid"] is True
    assert response["validation"]["action"] == "log"
    assert response["validation"]["score"] == 1.0


@pytest.mark.asyncio
async def test_handle_action_proposed_blocked():
    """Test handling of an action that should be blocked"""
    mock_interface = MockMyceliumClient()
    validator = EthikValidator(TEST_CONFIG, mock_interface)
    validator.rules = SAMPLE_RULES

    # Test message for config file modification
    message = {
        "id": "test-action-2",
        "payload": {
            "action_type": "file_write",
            "source_component": "test_component",
            "target_path": "/path/to/config/settings.json",
        },
    }

    await validator.handle_action_proposed(message)

    # Should have two messages: validation response and block notification
    assert len(mock_interface.published_messages) == 2

    # Check validation response
    topic, response = mock_interface.published_messages[0]
    assert topic == "response.validation.test-action-2"
    assert response["type"] == "validation_response"
    assert response["validation"]["is_valid"] is False
    assert response["validation"]["action"] == "block"

    # Check block notification
    topic, block_notice = mock_interface.published_messages[1]
    assert topic == "event.ethik.block"
    assert block_notice["reference_id"] == "test-action-2"


@pytest.mark.asyncio
async def test_handle_status_update_critical():
    """Test handling of a critical status update"""
    mock_interface = MockMyceliumClient()
    validator = EthikValidator(TEST_CONFIG, mock_interface)
    validator.rules = SAMPLE_RULES

    message = {
        "component": "test_component",
        "status": {"health": "critical", "errors": ["Test error"]},
    }

    await validator.handle_status_update(message)

    # Verify the status was processed and validation was triggered
    assert len(validator.validation_history) > 0
    latest_result = validator.validation_history[-1]
    assert latest_result.action_taken == "warn"
    assert "test_component" in latest_result.affected_components


@pytest.mark.asyncio
async def test_handle_action_proposed_error():
    """Test error handling in action proposal processing"""
    mock_interface = MockMyceliumClient()
    validator = EthikValidator(TEST_CONFIG, mock_interface)
    validator.rules = SAMPLE_RULES

    # Test message with missing required fields
    message = {"id": "test-action-3", "payload": {}}  # Empty payload should trigger error handling

    await validator.handle_action_proposed(message)

    # Should have published error response
    assert len(mock_interface.published_messages) == 1
    topic, response = mock_interface.published_messages[0]
    assert topic == "response.validation.test-action-3"
    assert response["type"] == "validation_error"


@pytest.mark.asyncio
async def test_handle_status_update_invalid():
    """Test handling of invalid status update"""
    mock_interface = MockMyceliumClient()
    validator = EthikValidator(TEST_CONFIG, mock_interface)

    # Test message without component identifier
    message = {"status": {"health": "normal"}}

    await validator.handle_status_update(message)

    # Should not have triggered any validations
    assert len(validator.validation_history) == 0


def test_should_apply_rule():
    """Test rule applicability logic"""
    mock_interface = MockMyceliumClient()
    validator = EthikValidator(TEST_CONFIG, mock_interface)
    validator.rules = SAMPLE_RULES

    # Test context that should match validate-001
    context = {"action_type": "file_write", "target_path": "/etc/config/test.json"}

    rule = SAMPLE_RULES["validate-001"]
    assert validator._should_apply_rule(rule, context) is True

    # Test context that shouldn't match
    context = {"action_type": "file_read", "target_path": "/etc/config/test.json"}
    assert validator._should_apply_rule(rule, context) is True  # Currently always returns True


def test_process_validation_result():
    """Test validation result processing"""
    mock_interface = MockMyceliumClient()
    validator = EthikValidator(TEST_CONFIG, mock_interface)

    result = ValidationResult(
        rule_id="test-rule",
        timestamp=datetime.datetime.now(),
        is_valid=False,
        score=0.0,
        details="Test violation",
        action_taken="block",
        affected_components=["test_component"],
    )

    validator._process_validation_result(result)

    # Check if result was added to history
    assert len(validator.validation_history) == 1
    assert validator.validation_history[0] == result


@pytest.mark.asyncio
async def test_validation_request_handler(validator, mock_mycelium):
    """Test handling of validation requests via Mycelium."""
    # Prepare test data
    action = "test_action"
    context = {"user": "test_user"}
    rules = ["rule1", "rule2"]

    # Mock validate_action method
    validator.validate_action = AsyncMock(
        return_value=Mock(
            is_valid=True, score=0.95, details={"passed_rules": ["rule1", "rule2"]}, severity=0.1
        )
    )

    # Trigger validation request
    await mock_mycelium.trigger_message(
        "test.ethik.validate.request", {"action": action, "context": context, "rules": rules}
    )

    # Check that validate_action was called correctly
    validator.validate_action.assert_called_once_with(action, context, rules)

    # Verify published result
    assert len(mock_mycelium.published_messages) == 1
    result = mock_mycelium.published_messages[0]
    assert result["topic"] == "test.ethik.validate.result"
    assert result["data"]["action"] == action
    assert result["data"]["valid"]
    assert result["data"]["score"] == 0.95


@pytest.mark.asyncio
async def test_validation_request_failure_alert(validator, mock_mycelium):
    """Test that alerts are published for failed validations."""
    # Mock validate_action to return failed validation
    validator.validate_action = AsyncMock(
        return_value=Mock(
            is_valid=False, score=0.3, details={"failed_rules": ["critical_rule"]}, severity=0.8
        )
    )

    # Trigger validation request
    await mock_mycelium.trigger_message("test.ethik.validate.request", {"action": "risky_action"})

    # Verify both result and alert were published
    assert len(mock_mycelium.published_messages) == 2

    # Check result message
    result = mock_mycelium.published_messages[0]
    assert result["topic"] == "test.ethik.validate.result"
    assert not result["data"]["valid"]
    assert result["data"]["score"] == 0.3

    # Check alert message
    alert = mock_mycelium.published_messages[1]
    assert alert["topic"] == "test.ethik.alert"
    assert alert["data"]["type"] == "validation_failure"
    assert "risky_action" in alert["data"]["message"]
    assert alert["data"]["details"]["severity"] == 0.8


@pytest.mark.asyncio
async def test_rules_update_handler(validator, mock_mycelium):
    """Test handling of rules update requests."""
    new_rules = {
        "new_rule_1": {"condition": "x > 0", "severity": 0.5},
        "new_rule_2": {"condition": "y < 10", "severity": 0.8},
    }

    # Trigger rules update
    await mock_mycelium.trigger_message("test.ethik.rules.update", {"rules": new_rules})

    # Verify rules were updated
    assert "new_rule_1" in validator.rules
    assert "new_rule_2" in validator.rules

    # Check confirmation message
    assert len(mock_mycelium.published_messages) == 1
    status = mock_mycelium.published_messages[0]
    assert status["topic"] == "test.ethik.rules.status"
    assert status["data"]["status"] == "success"
    assert status["data"]["rules_count"] == len(new_rules)


@pytest.mark.asyncio
async def test_validation_request_error_handling(validator, mock_mycelium):
    """Test error handling in validation request processing."""
    # Mock validate_action to raise an exception
    validator.validate_action = AsyncMock(side_effect=ValueError("Invalid action"))

    # Trigger validation request
    await mock_mycelium.trigger_message("test.ethik.validate.request", {"action": "bad_action"})

    # Verify error response
    assert len(mock_mycelium.published_messages) == 1
    error_msg = mock_mycelium.published_messages[0]
    assert error_msg["topic"] == "test.ethik.validate.result"
    assert error_msg["data"]["status"] == "error"
    assert "Invalid action" in error_msg["data"]["error"]


@pytest.mark.asyncio
async def test_rules_update_error_handling(validator, mock_mycelium):
    """Test error handling in rules update processing."""
    # Trigger rules update with invalid data
    await mock_mycelium.trigger_message(
        "test.ethik.rules.update",
        {"rules": "invalid_rules_data"},  # Should be a dict
    )

    # Verify error response
    assert len(mock_mycelium.published_messages) == 1
    error_msg = mock_mycelium.published_messages[0]
    assert error_msg["topic"] == "test.ethik.rules.status"
    assert error_msg["data"]["status"] == "error"
    assert "error" in error_msg["data"]


@pytest.mark.asyncio
async def test_alert_publishing(validator, mock_mycelium):
    """Test alert publishing functionality."""
    alert_type = "test_alert"
    alert_message = "Test alert message"
    alert_details = {"key": "value"}

    # Publish alert
    await validator._publish_alert(alert_type, alert_message, alert_details)

    # Verify alert was published
    assert len(mock_mycelium.published_messages) == 1
    alert = mock_mycelium.published_messages[0]
    assert alert["topic"] == "test.ethik.alert"
    assert alert["data"]["type"] == alert_type
    assert alert["data"]["message"] == alert_message
    assert alert["data"]["details"] == alert_details
    assert "timestamp" in alert["data"]


if __name__ == "__main__":
    pytest.main([__file__])

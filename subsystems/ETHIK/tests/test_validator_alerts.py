#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - ETHIK Validator Alert Tests
=========================================

Test suite for ETHIK validation alert system.
Ensures proper functioning of the alert mechanism.

Version: 8.0.0
"""

import asyncio
from typing import Any, Dict

import pytest

from ..core.validator import EthikValidator
from .test_validator import SAMPLE_RULES, TEST_CONFIG, MockMyceliumInterface


@pytest.mark.asyncio
async def test_alert_on_block():
    """Test alert generation for blocked actions"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)
    validator.rules = SAMPLE_RULES

    # Trigger a validation that should be blocked
    message = {
        "id": "test-block-1",
        "payload": {
            "action_type": "file_write",
            "source_component": "test_component",
            "target_path": "/path/to/config/critical.json",
        },
    }

    await validator.handle_action_proposed(message)

    # Wait for alert task to complete
    await asyncio.sleep(0.1)

    # Check published messages
    alert_messages = [
        msg for topic, msg in mock_interface.published_messages if msg.get("type") == "ethik_alert"
    ]

    assert len(alert_messages) == 1
    alert = alert_messages[0]
    assert alert["severity"] == "critical"
    assert alert["details"]["action"] == "block"
    assert "config" in alert["details"]["description"].lower()


@pytest.mark.asyncio
async def test_alert_on_warning():
    """Test alert generation for warning conditions"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)
    validator.rules = SAMPLE_RULES

    # Trigger a validation that should generate a warning
    message = {
        "component": "test_component",
        "status": {"health": "critical", "errors": ["Test error"]},
    }

    await validator.handle_status_update(message)

    # Wait for alert task to complete
    await asyncio.sleep(0.1)

    # Check published messages
    alert_messages = [
        msg for topic, msg in mock_interface.published_messages if msg.get("type") == "ethik_alert"
    ]

    assert len(alert_messages) == 1
    alert = alert_messages[0]
    assert alert["severity"] == "warning"
    assert alert["details"]["action"] == "warn"


@pytest.mark.asyncio
async def test_concurrent_alerts():
    """Test handling of multiple concurrent alerts"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)
    validator.rules = SAMPLE_RULES

    # Create multiple validation tasks
    tasks = []
    for i in range(5):
        message = {
            "id": f"test-concurrent-{i}",
            "payload": {
                "action_type": "file_write",
                "source_component": f"component_{i}",
                "target_path": "/path/to/config/test.json",
            },
        }
        tasks.append(validator.handle_action_proposed(message))

    # Run all tasks concurrently
    await asyncio.gather(*tasks)

    # Wait for alert tasks to complete
    await asyncio.sleep(0.1)

    # Check alerts
    alert_messages = [
        msg for topic, msg in mock_interface.published_messages if msg.get("type") == "ethik_alert"
    ]

    assert len(alert_messages) == 5
    # Verify each alert has unique source component
    components = set(alert["details"]["affected_components"][0] for alert in alert_messages)
    assert len(components) == 5


@pytest.mark.asyncio
async def test_alert_error_handling():
    """Test handling of errors during alert sending"""

    class FailingMyceliumInterface(MockMyceliumInterface):
        async def publish(self, topic: str, message: Dict[str, Any]):
            if message.get("type") == "ethik_alert":
                raise Exception("Test publish failure")
            await super().publish(topic, message)

    mock_interface = FailingMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)
    validator.rules = SAMPLE_RULES

    # Trigger validation that should generate alert
    message = {
        "id": "test-error-1",
        "payload": {
            "action_type": "file_write",
            "source_component": "test_component",
            "target_path": "/path/to/config/test.json",
        },
    }

    # Should not raise exception despite publish failure
    await validator.handle_action_proposed(message)

    # Verify validation response was still sent
    validation_responses = [
        msg
        for topic, msg in mock_interface.published_messages
        if msg.get("type") == "validation_response"
    ]
    assert len(validation_responses) == 1


@pytest.mark.asyncio
async def test_alert_cleanup():
    """Test cleanup of completed alert tasks"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)
    validator.rules = SAMPLE_RULES

    # Generate some alerts
    for i in range(3):
        message = {
            "id": f"test-cleanup-{i}",
            "payload": {
                "action_type": "file_write",
                "source_component": f"component_{i}",
                "target_path": "/path/to/config/test.json",
            },
        }
        await validator.handle_action_proposed(message)

    # Wait for tasks to complete
    await asyncio.sleep(0.1)

    # Check that completed tasks are cleaned up
    active_tasks = [task for task in validator.active_validations.values() if not task.done()]
    assert len(active_tasks) == 0


if __name__ == "__main__":
    pytest.main([__file__])

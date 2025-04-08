#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - ETHIK Validator Concurrency Tests
===============================================

Test suite for concurrent validation handling.
Ensures proper behavior under concurrent validation requests.

Version: 8.0.0
"""

import asyncio

import pytest

from ..core.validator import EthikValidator, ValidationResult
from .test_validator import SAMPLE_RULES, TEST_CONFIG, MockMyceliumInterface


@pytest.mark.asyncio
async def test_concurrent_validation_requests():
    """Test handling multiple validation requests concurrently"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)
    validator.rules = SAMPLE_RULES.copy()

    # Create multiple action contexts
    contexts = [
        {
            "action_type": f"test_action_{i}",
            "source_component": f"test_component_{i}",
            "target_path": f"/test/path_{i}",
            "timestamp": "2024-03-15T12:00:00Z",
        }
        for i in range(5)
    ]

    # Create tasks for concurrent validation
    tasks = [asyncio.create_task(validator.validate_action(context)) for context in contexts]

    # Wait for all validations to complete
    results = await asyncio.gather(*tasks)

    # Check results
    assert len(results) == 5
    for result in results:
        assert isinstance(result, ValidationResult)
        assert result.is_valid in [True, False]


@pytest.mark.asyncio
async def test_concurrent_rule_updates():
    """Test handling rule updates during validation"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)
    validator.rules = SAMPLE_RULES.copy()

    # Create validation task
    context = {
        "action_type": "test_action",
        "source_component": "test_component",
        "target_path": "/test/path",
        "timestamp": "2024-03-15T12:00:00Z",
    }

    validation_task = asyncio.create_task(validator.validate_action(context))

    # Add new rule during validation
    new_rule = {
        "id": "concurrent-rule",
        "name": "Concurrent Test Rule",
        "description": "Rule added during validation",
        "severity": "high",
        "conditions": ["True"],
        "threshold": 0.8,
        "action": "warn",
    }
    validator.add_rule(new_rule)

    # Wait for validation to complete
    result = await validation_task

    # Check that validation completed successfully
    assert isinstance(result, ValidationResult)
    assert result.is_valid in [True, False]

    # Check that new rule was added
    assert "concurrent-rule" in validator.rules


@pytest.mark.asyncio
async def test_concurrent_history_access():
    """Test concurrent access to validation history"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)

    # Create tasks for concurrent history access
    async def add_and_read_history():
        # Add result to history
        result = ValidationResult(
            rule_id="test-rule",
            timestamp="2024-03-15T12:00:00Z",
            is_valid=True,
            score=1.0,
            details="Test result",
            action_taken="log",
            affected_components=["test"],
        )
        validator._process_validation_result(result)

        # Read history
        return validator.get_validation_history()

    # Create multiple concurrent tasks
    tasks = [asyncio.create_task(add_and_read_history()) for _ in range(5)]

    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)

    # Check that all tasks completed successfully
    for history in results:
        assert isinstance(history, list)
        assert len(history) > 0


@pytest.mark.asyncio
async def test_concurrent_alert_generation():
    """Test concurrent generation of alerts"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)

    # Create multiple validation results that should trigger alerts
    results = [
        ValidationResult(
            rule_id=f"test-rule-{i}",
            timestamp="2024-03-15T12:00:00Z",
            is_valid=False,
            score=0.0,
            details=f"Critical issue {i}",
            action_taken="block",
            affected_components=[f"component-{i}"],
        )
        for i in range(5)
    ]

    # Process results concurrently
    tasks = [asyncio.create_task(validator._send_alert(result)) for result in results]

    # Wait for all alerts to be sent
    await asyncio.gather(*tasks)

    # Check that all alerts were published
    assert len(mock_interface.published_messages) == 5
    for msg in mock_interface.published_messages:
        assert msg["topic"].startswith("alert.ethik")


@pytest.mark.asyncio
async def test_validation_timeout():
    """Test handling of validation timeout"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(
        {**TEST_CONFIG, "validator_config": {"validation_timeout": 0.1}},  # 100ms timeout
        mock_interface,
    )

    # Add a rule that takes too long to evaluate
    slow_rule = {
        "id": "slow-rule",
        "name": "Slow Rule",
        "description": "Rule that takes too long",
        "severity": "medium",
        "conditions": ["await asyncio.sleep(0.2); True"],  # Will exceed timeout
        "threshold": 0.5,
        "action": "warn",
    }
    validator.add_rule(slow_rule)

    # Try to validate with the slow rule
    context = {"action_type": "test_action", "source_component": "test_component"}

    with pytest.raises(asyncio.TimeoutError):
        await validator.validate_action(context)


@pytest.mark.asyncio
async def test_concurrent_component_status():
    """Test concurrent component status updates"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)

    # Create multiple status updates
    status_updates = [
        {
            "component": f"component-{i}",
            "status": "critical" if i % 2 == 0 else "healthy",
            "timestamp": "2024-03-15T12:00:00Z",
        }
        for i in range(5)
    ]

    # Process status updates concurrently
    tasks = [
        asyncio.create_task(validator.handle_status_update(update)) for update in status_updates
    ]

    # Wait for all updates to complete
    await asyncio.gather(*tasks)

    # Check component statuses
    for i in range(5):
        component = f"component-{i}"
        expected_status = "critical" if i % 2 == 0 else "healthy"
        assert validator.component_health.get(component) == expected_status


if __name__ == "__main__":
    pytest.main([__file__])

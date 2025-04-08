#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - ETHIK Validator Severity Tests
===========================================

Test suite for validation severity handling.
Ensures proper handling of different severity levels.

Version: 8.0.0
"""

import pytest

from ..core.validator import EthikValidator
from .test_validator import TEST_CONFIG, MockMyceliumInterface


def test_critical_severity():
    """Test handling of critical severity rules"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)

    # Add critical rule
    critical_rule = {
        "id": "critical-rule",
        "name": "Critical Test Rule",
        "description": "Rule with critical severity",
        "severity": "critical",
        "conditions": ["True"],
        "threshold": 0.95,
        "action": "block",
    }
    validator.add_rule(critical_rule)

    # Test context that should trigger the rule
    context = {
        "action_type": "critical_action",
        "source_component": "test_component",
        "target_path": "/critical/path",
        "timestamp": "2024-03-15T12:00:00Z",
    }

    # Validate action
    result = validator.validate_action(context)

    # Check result
    assert not result.is_valid
    assert result.action_taken == "block"
    assert result.score == 0.0

    # Check alert was sent
    assert len(mock_interface.published_messages) > 0
    alert = mock_interface.published_messages[-1]
    assert alert["topic"] == "alert.ethik.critical"


def test_high_severity():
    """Test handling of high severity rules"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)

    # Add high severity rule
    high_rule = {
        "id": "high-rule",
        "name": "High Test Rule",
        "description": "Rule with high severity",
        "severity": "high",
        "conditions": ["True"],
        "threshold": 0.8,
        "action": "warn",
    }
    validator.add_rule(high_rule)

    # Test context
    context = {
        "action_type": "high_risk_action",
        "source_component": "test_component",
        "target_path": "/high/risk/path",
        "timestamp": "2024-03-15T12:00:00Z",
    }

    # Validate action
    result = validator.validate_action(context)

    # Check result
    assert not result.is_valid
    assert result.action_taken == "warn"
    assert result.score < 0.8

    # Check alert was sent
    assert len(mock_interface.published_messages) > 0
    alert = mock_interface.published_messages[-1]
    assert alert["topic"] == "alert.ethik.high"


def test_medium_severity():
    """Test handling of medium severity rules"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)

    # Add medium severity rule
    medium_rule = {
        "id": "medium-rule",
        "name": "Medium Test Rule",
        "description": "Rule with medium severity",
        "severity": "medium",
        "conditions": ["True"],
        "threshold": 0.6,
        "action": "log",
    }
    validator.add_rule(medium_rule)

    # Test context
    context = {
        "action_type": "medium_risk_action",
        "source_component": "test_component",
        "target_path": "/medium/risk/path",
        "timestamp": "2024-03-15T12:00:00Z",
    }

    # Validate action
    result = validator.validate_action(context)

    # Check result
    assert result.is_valid  # Medium severity shouldn't block
    assert result.action_taken == "log"
    assert result.score >= 0.6


def test_low_severity():
    """Test handling of low severity rules"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)

    # Add low severity rule
    low_rule = {
        "id": "low-rule",
        "name": "Low Test Rule",
        "description": "Rule with low severity",
        "severity": "low",
        "conditions": ["True"],
        "threshold": 0.4,
        "action": "log",
    }
    validator.add_rule(low_rule)

    # Test context
    context = {
        "action_type": "low_risk_action",
        "source_component": "test_component",
        "target_path": "/low/risk/path",
        "timestamp": "2024-03-15T12:00:00Z",
    }

    # Validate action
    result = validator.validate_action(context)

    # Check result
    assert result.is_valid  # Low severity shouldn't block
    assert result.action_taken == "log"
    assert result.score >= 0.4


def test_multiple_severity_levels():
    """Test handling multiple rules with different severities"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)

    # Add rules with different severities
    rules = {
        "critical": {
            "id": "critical-rule",
            "name": "Critical Rule",
            "description": "Critical severity rule",
            "severity": "critical",
            "conditions": ["True"],
            "threshold": 0.95,
            "action": "block",
        },
        "high": {
            "id": "high-rule",
            "name": "High Rule",
            "description": "High severity rule",
            "severity": "high",
            "conditions": ["True"],
            "threshold": 0.8,
            "action": "warn",
        },
        "medium": {
            "id": "medium-rule",
            "name": "Medium Rule",
            "description": "Medium severity rule",
            "severity": "medium",
            "conditions": ["True"],
            "threshold": 0.6,
            "action": "log",
        },
    }

    for rule in rules.values():
        validator.add_rule(rule)

    # Test context
    context = {
        "action_type": "test_action",
        "source_component": "test_component",
        "target_path": "/test/path",
        "timestamp": "2024-03-15T12:00:00Z",
    }

    # Validate action
    result = validator.validate_action(context)

    # Check that highest severity rule takes precedence
    assert not result.is_valid
    assert result.action_taken == "block"  # Critical rule's action
    assert result.score == 0.0


def test_severity_threshold_override():
    """Test severity threshold override behavior"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(
        {
            **TEST_CONFIG,
            "validator_config": {
                "severity_thresholds": {
                    "critical": 0.99,  # Higher than default
                    "high": 0.85,  # Higher than default
                    "medium": 0.7,  # Higher than default
                    "low": 0.5,  # Higher than default
                }
            },
        },
        mock_interface,
    )

    # Add rule that would normally trigger
    rule = {
        "id": "threshold-test",
        "name": "Threshold Test Rule",
        "description": "Rule for testing thresholds",
        "severity": "high",
        "conditions": ["True"],
        "threshold": 0.8,  # Below new high severity threshold
        "action": "warn",
    }
    validator.add_rule(rule)

    # Test context
    context = {
        "action_type": "test_action",
        "source_component": "test_component",
        "target_path": "/test/path",
        "timestamp": "2024-03-15T12:00:00Z",
    }

    # Validate action
    result = validator.validate_action(context)

    # Check that rule wasn't applied due to higher threshold
    assert result.is_valid
    assert result.action_taken == "none"
    assert result.score > 0.8


def test_severity_escalation():
    """Test severity escalation based on repeated violations"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)

    # Add medium severity rule
    rule = {
        "id": "escalation-test",
        "name": "Escalation Test Rule",
        "description": "Rule for testing severity escalation",
        "severity": "medium",
        "conditions": ["True"],
        "threshold": 0.6,
        "action": "log",
        "escalation": {"count": 3, "window": "1h", "target_severity": "high"},
    }
    validator.add_rule(rule)

    # Create context
    context = {
        "action_type": "test_action",
        "source_component": "test_component",
        "target_path": "/test/path",
        "timestamp": "2024-03-15T12:00:00Z",
    }

    # Trigger rule multiple times
    for _ in range(4):
        result = validator.validate_action(context)

    # Check that severity was escalated
    assert not result.is_valid
    assert result.action_taken == "warn"  # Escalated to high severity action
    assert result.score < 0.8  # High severity threshold


if __name__ == "__main__":
    pytest.main([__file__])

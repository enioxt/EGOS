#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - ETHIK Validator Rule Tests
========================================

Test suite for ETHIK validation rule management.
Ensures proper loading and application of rules.

Version: 8.0.0
"""

import datetime
import json
from unittest.mock import mock_open, patch

import pytest

from ..core.validator import EthikValidator, ValidationResult, ValidationRule
from .test_validator import SAMPLE_RULES, TEST_CONFIG, MockMyceliumInterface


def test_load_rules_from_file():
    """Test loading rules from a JSON file"""
    mock_interface = MockMyceliumInterface()

    # Create test rules file content
    test_rules_content = {
        "rules": [
            {
                "id": "test-rule-001",
                "name": "Test Rule",
                "description": "Test rule for loading",
                "severity": "medium",
                "conditions": ["True"],
                "threshold": 0.5,
                "action": "warn",
            }
        ]
    }

    # Mock file operations
    with (
        patch("builtins.open", mock_open(read_data=json.dumps(test_rules_content))),
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.is_file", return_value=True),
    ):
        validator = EthikValidator(TEST_CONFIG, mock_interface)

        assert len(validator.rules) == 1
        assert "test-rule-001" in validator.rules
        rule = validator.rules["test-rule-001"]
        assert rule.name == "Test Rule"
        assert rule.severity == "medium"


def test_load_rules_file_not_found():
    """Test handling of missing rules file"""
    mock_interface = MockMyceliumInterface()

    # Mock file operations - file doesn't exist
    with patch("pathlib.Path.exists", return_value=False):
        validator = EthikValidator(TEST_CONFIG, mock_interface)
        assert len(validator.rules) == 0


def test_load_rules_invalid_json():
    """Test handling of invalid JSON in rules file"""
    mock_interface = MockMyceliumInterface()

    # Mock file operations with invalid JSON
    with (
        patch("builtins.open", mock_open(read_data="invalid json")),
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.is_file", return_value=True),
    ):
        validator = EthikValidator(TEST_CONFIG, mock_interface)
        assert len(validator.rules) == 0


def test_add_rule():
    """Test adding a new rule"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)

    new_rule = {
        "id": "new-rule-001",
        "name": "New Test Rule",
        "description": "Test adding new rule",
        "severity": "high",
        "conditions": ["True"],
        "threshold": 0.8,
        "action": "warn",
    }

    validator.add_rule(new_rule)

    assert "new-rule-001" in validator.rules
    rule = validator.rules["new-rule-001"]
    assert rule.name == "New Test Rule"
    assert rule.severity == "high"


def test_remove_rule():
    """Test removing a rule"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)
    validator.rules = SAMPLE_RULES.copy()

    initial_count = len(validator.rules)
    validator.remove_rule("validate-001")

    assert len(validator.rules) == initial_count - 1
    assert "validate-001" not in validator.rules


def test_history_retention():
    """Test validation history retention"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(
        {**TEST_CONFIG, "validator_config": {"history_retention_days": 1}}, mock_interface
    )

    # Add some old results
    old_date = datetime.datetime.now() - datetime.timedelta(days=2)
    old_result = ValidationResult(
        rule_id="test-rule",
        timestamp=old_date,
        is_valid=True,
        score=1.0,
        details="Old result",
        action_taken="log",
        affected_components=["test"],
    )
    validator.validation_history.append(old_result)

    # Add some recent results
    new_result = ValidationResult(
        rule_id="test-rule",
        timestamp=datetime.datetime.now(),
        is_valid=True,
        score=1.0,
        details="New result",
        action_taken="log",
        affected_components=["test"],
    )
    validator._process_validation_result(new_result)

    # Check that old results were cleaned up
    assert len(validator.validation_history) == 1
    assert validator.validation_history[0].details == "New result"


def test_get_validation_history_filters():
    """Test filtering of validation history"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(TEST_CONFIG, mock_interface)

    # Add some test results
    now = datetime.datetime.now()
    results = [
        ValidationResult(
            rule_id=f"test-rule-{i}",
            timestamp=now - datetime.timedelta(hours=i),
            is_valid=True,
            score=1.0,
            details=f"Result {i}",
            action_taken="log",
            affected_components=[f"component-{i % 2}"],  # Alternate between two components
        )
        for i in range(5)
    ]

    for result in results:
        validator.validation_history.append(result)

    # Test component filter
    component_results = validator.get_validation_history(component="component-0")
    assert len(component_results) == 3  # Should get results for component-0

    # Test time filter
    time_results = validator.get_validation_history(
        start_time=now - datetime.timedelta(hours=2), end_time=now
    )
    assert len(time_results) == 3  # Should get last 3 hours of results


def test_rule_severity_threshold():
    """Test rule severity threshold handling"""
    mock_interface = MockMyceliumInterface()
    validator = EthikValidator(
        {**TEST_CONFIG, "validator_config": {"ethical_threshold": 0.9}}, mock_interface
    )

    # Add rules with different thresholds
    rules = {
        "high-threshold": ValidationRule(
            id="high-threshold",
            name="High Threshold Rule",
            description="Rule with high threshold",
            severity="medium",
            conditions=["True"],
            threshold=0.95,
            action="warn",
        ),
        "low-threshold": ValidationRule(
            id="low-threshold",
            name="Low Threshold Rule",
            description="Rule with low threshold",
            severity="medium",
            conditions=["True"],
            threshold=0.5,
            action="warn",
        ),
    }
    validator.rules = rules

    # Test context
    context = {"action_type": "test", "source_component": "test"}

    # High threshold rule should be applied
    assert validator._should_apply_rule(rules["high-threshold"], context) is True

    # Low threshold rule should not be applied
    assert validator._should_apply_rule(rules["low-threshold"], context) is False


if __name__ == "__main__":
    pytest.main([__file__])

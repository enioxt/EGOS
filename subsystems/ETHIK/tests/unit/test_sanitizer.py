#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the ETHIK Sanitizer
============================

Comprehensive test suite for the enhanced sanitization system.
"""

from datetime import datetime, timedelta
import json

import pytest

from ..sanitizers.ethik_sanitizer import EthikSanitizer, SanitizationResult, SanitizationRule

# Test configuration
TEST_CONFIG = {
    "cache_retention_hours": 1,
    "history_retention_days": 1,
    "ethical_threshold": 0.7,
    "max_cache_size": 10,
    "sanitization_levels": {"strict": 0.9, "normal": 0.7, "lenient": 0.5},
    "performance": {
        "parallel_processing": {"enabled": True, "max_workers": 2},
        "caching": {"strategy": "priority_queue", "max_size": 5},
    },
    "integrations": {"websocket": {"enabled": False}},
}


@pytest.fixture
def sanitizer():
    """Create a sanitizer instance for testing"""
    return EthikSanitizer()


@pytest.fixture
def config_file(tmp_path):
    """Create a temporary config file"""
    config_path = tmp_path / "test_config.json"
    with open(config_path, "w") as f:
        json.dump(TEST_CONFIG, f)
    return str(config_path)


def test_sanitizer_initialization(sanitizer):
    """Test sanitizer initialization"""
    assert sanitizer.rules is not None
    assert len(sanitizer.rules) >= 3  # At least default rules
    assert sanitizer.content_cache is not None
    assert sanitizer.sanitization_history is not None


def test_default_rules(sanitizer):
    """Test default sanitization rules"""
    assert "sanitize-001" in sanitizer.rules  # Ethical Language
    assert "sanitize-002" in sanitizer.rules  # Privacy Protection
    assert "sanitize-003" in sanitizer.rules  # Inclusive Language
    assert "sanitize-004" in sanitizer.rules  # Code Aesthetics
    assert "sanitize-005" in sanitizer.rules  # Documentation Harmony
    assert "sanitize-006" in sanitizer.rules  # Deep Empathy
    assert "sanitize-007" in sanitizer.rules  # Resource Efficiency


@pytest.mark.parametrize(
    "content,expected_changes",
    [
        ("I hate this code", True),  # Ethical Language
        ("email@example.com", True),  # Privacy Protection
        ("Hey guys, check this", True),  # Inclusive Language
        ("This is ugly code", True),  # Code Aesthetics
        ("This is unclear", True),  # Documentation Harmony
        ("This is obviously simple", True),  # Deep Empathy
        ("This is a memory intensive operation", True),  # Resource Efficiency
        ("This is fine code", False),  # No changes needed
    ],
)
def test_content_sanitization(sanitizer, content, expected_changes):
    """Test content sanitization with various inputs"""
    result = sanitizer.sanitize_content(content)
    assert isinstance(result, SanitizationResult)
    assert bool(result.changes_made) == expected_changes
    assert result.ethical_score > 0
    assert result.is_clean == (not expected_changes)


def test_cache_functionality(sanitizer):
    """Test caching system"""
    content = "This is a test content"

    # First call should process content
    result1 = sanitizer.sanitize_content(content)
    assert result1.content_id in sanitizer.content_cache

    # Second call should use cache
    result2 = sanitizer.sanitize_content(content)
    assert result1.content_id == result2.content_id
    assert result1.timestamp == result2.timestamp


def test_cache_priority(sanitizer):
    """Test cache priority queue"""
    # Fill cache beyond max size
    for i in range(TEST_CONFIG["max_cache_size"] + 2):
        content = f"Test content {i}"
        result = sanitizer.sanitize_content(content)
        result.ethical_score = 0.5 + (i * 0.1)  # Varying scores
        sanitizer._update_cache(result)

    assert len(sanitizer.content_cache) <= TEST_CONFIG["max_cache_size"]


@pytest.mark.asyncio
async def test_async_sanitization(sanitizer):
    """Test asynchronous content sanitization"""
    content = "This needs sanitization"
    result = await sanitizer.sanitize_content_async(content)
    assert isinstance(result, SanitizationResult)
    assert result.sanitized_content != content


def test_rule_conditions(sanitizer):
    """Test rule condition evaluation"""
    # Technical context should skip some rules
    content = "This code is ugly"
    context = {"file_type": "code"}
    sanitizer.sanitize_content(content, context)
    assert any(rule.id == "sanitize-004" for rule in sanitizer.rules.values())


def test_performance_metrics(sanitizer):
    """Test performance metrics tracking"""
    content = "This needs heavy processing"
    result = sanitizer.sanitize_content(content)
    assert "processing_time" in result.performance_metrics
    assert "rules_applied" in result.performance_metrics
    assert "cpu_usage" in result.resource_usage


def test_sanitization_history(sanitizer):
    """Test sanitization history tracking"""
    content = "Test content"
    sanitizer.sanitize_content(content)
    assert len(sanitizer.sanitization_history) > 0

    # Test history filtering
    start_time = datetime.now() - timedelta(hours=1)
    end_time = datetime.now() + timedelta(hours=1)
    filtered = sanitizer.get_sanitization_history(start_time, end_time)
    assert len(filtered) > 0


def test_custom_rule_addition(sanitizer):
    """Test adding custom sanitization rules"""
    new_rule = SanitizationRule(
        id="test-rule",
        name="Test Rule",
        description="Test rule for testing",
        severity="medium",
        patterns=[r"\btest\b"],
        replacements={r"\btest\b": "validated"},
        conditions=[],
    )

    sanitizer.add_rule(new_rule)
    assert "test-rule" in sanitizer.rules

    # Test the new rule
    content = "This is a test"
    result = sanitizer.sanitize_content(content)
    assert "test-rule" in result.applied_rules
    assert "validated" in result.sanitized_content


def test_error_handling(sanitizer):
    """Test error handling in sanitization"""
    # Test with invalid content
    result = sanitizer.sanitize_content(None)
    assert result.is_clean
    assert result.content_id == "empty"

    # Test with invalid rule condition
    rule = SanitizationRule(
        id="invalid-rule",
        name="Invalid Rule",
        description="Rule with invalid condition",
        severity="low",
        patterns=[r"\btest\b"],
        replacements={},
        conditions=["invalid_condition()"],
    )
    sanitizer.add_rule(rule)
    result = sanitizer.sanitize_content("test")
    assert result is not None  # Should not crash


if __name__ == "__main__":
    pytest.main([__file__])

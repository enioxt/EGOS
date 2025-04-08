#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - ETHIK Sanitizer Mycelium Tests
============================================

Test suite for the ETHIK Sanitizer's Mycelium integration.
Ensures proper handling of sanitize requests and responses.

Version: 8.0.0
"""

import json
from pathlib import Path
from typing import Dict
from unittest.mock import patch

import pytest

# Import the sanitizer and related classes
from ..core.sanitizer import EthikSanitizer


# Mock Mycelium Interface (can reuse from test_service or define here)
class MockMyceliumInterface:
    def __init__(self, node_id="mock_node"):
        self.node_id = node_id
        self.published_messages = []
        self.subscribed_topics = {}

    async def publish(self, topic, message):
        self.published_messages.append({"topic": topic, "message": message})

    async def subscribe(self, topic, handler):
        if topic not in self.subscribed_topics:
            self.subscribed_topics[topic] = []
        self.subscribed_topics[topic].append(handler)


@pytest.fixture
def mock_mycelium():
    return MockMyceliumInterface()


@pytest.fixture
def test_sanitizer_config(tmp_path: Path) -> Dict:
    """Provides a basic sanitizer config and creates dummy rule file."""
    rules_file = tmp_path / "sanitization_rules.json"
    rules_content = {
        "rules": [
            {
                "id": "rule-001",
                "name": "Block Bad Word",
                "description": "Replaces BAD_WORD",
                "severity": "high",
                "patterns": ["BAD_WORD"],
                "replacements": {"BAD_WORD": "[REPLACED]"},
                "conditions": [],
            }
        ]
    }
    rules_file.write_text(json.dumps(rules_content))

    return {
        "rules_file": str(rules_file.resolve()),  # Pass absolute path
        "history_retention_days": 1,
        "performance": {"caching": {"max_size": 10}},
    }


@pytest.fixture
def sanitizer(test_sanitizer_config, mock_mycelium) -> EthikSanitizer:
    """Provides an initialized EthikSanitizer instance."""
    return EthikSanitizer(test_sanitizer_config, mock_mycelium)


@pytest.mark.asyncio
async def test_handle_sanitize_request_success(sanitizer, mock_mycelium):
    """Test successful handling of a sanitize request via Mycelium."""
    # Simulate receiving a message
    request_message = {
        "id": "req-123",
        "payload": {
            "content": "This contains a BAD_WORD.",
            "context": {"source": "test_component"},
        },
    }

    # Get the handler function from the sanitizer (assuming it subscribed)
    # In a real scenario, Mycelium would route this, here we call it directly
    handler = sanitizer.handle_sanitize_request
    await handler(request_message)

    # Check if response was published
    assert len(mock_mycelium.published_messages) == 1
    published = mock_mycelium.published_messages[0]

    # Verify response details
    assert published["topic"] == "response.sanitization.req-123"
    assert published["message"]["type"] == "sanitization_response"
    assert published["message"]["reference_id"] == "req-123"

    payload = published["message"]["payload"]
    assert payload["original_content"] == "This contains a BAD_WORD."
    assert payload["sanitized_content"] == "This contains a [REPLACED]."
    assert payload["is_clean"] is False
    assert "rule-001" in payload["applied_rules"]
    assert len(payload["changes_made"]) == 1
    assert payload["changes_made"][0]["original"] == "BAD_WORD"
    assert payload["changes_made"][0]["replacement"] == "[REPLACED]"


@pytest.mark.asyncio
async def test_handle_sanitize_request_no_content(sanitizer, mock_mycelium):
    """Test handling a sanitize request missing the content field."""
    request_message = {
        "id": "req-456",
        "payload": {
            # Missing "content"
            "context": {"source": "test_component"}
        },
    }

    handler = sanitizer.handle_sanitize_request
    await handler(request_message)

    # Check if error response was published
    assert len(mock_mycelium.published_messages) == 1
    published = mock_mycelium.published_messages[0]

    assert published["topic"] == "response.sanitization.req-456"
    assert published["message"]["type"] == "sanitization_error"
    assert published["message"]["reference_id"] == "req-456"
    assert "Missing 'content'" in published["message"]["error"]


@pytest.mark.asyncio
async def test_handle_sanitize_request_internal_error(sanitizer, mock_mycelium):
    """Test handling when an internal error occurs during sanitization."""
    request_message = {"id": "req-789", "payload": {"content": "Some content.", "context": {}}}

    # Mock the internal sanitize_content to raise an error
    with patch.object(
        sanitizer, "sanitize_content", side_effect=RuntimeError("Internal processing failed")
    ):
        handler = sanitizer.handle_sanitize_request
        await handler(request_message)

    # Check if error response was published
    assert len(mock_mycelium.published_messages) == 1
    published = mock_mycelium.published_messages[0]

    assert published["topic"] == "response.sanitization.req-789"
    assert published["message"]["type"] == "sanitization_error"
    assert published["message"]["reference_id"] == "req-789"
    assert "Internal processing failed" in published["message"]["error"]


# Add tests for cache hits via Mycelium requests, different contexts, etc.

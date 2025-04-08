#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - ETHIK Service Tests
==================================

Test suite for the main ETHIK Service.
Ensures proper initialization and lifecycle management of components.

Version: 8.0.0
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ..core.sanitizer import EthikSanitizer
from ..core.validator import EthikValidator

# Import the service and components to potentially mock
from ..service import EthikService


# Mock Mycelium Interface
class MockMyceliumInterface:
    def __init__(self, node_id="mock_node"):
        self.node_id = node_id
        self.published_messages = []
        self.subscribed_topics = {}
        self.is_connected = True  # Assume connected for tests

    async def publish(self, topic, message):
        self.published_messages.append({"topic": topic, "message": message})
        print(f"Mock Publish to {topic}: {message}")  # Optional: for debug

    async def subscribe(self, topic, handler):
        if topic not in self.subscribed_topics:
            self.subscribed_topics[topic] = []
        self.subscribed_topics[topic].append(handler)
        print(f"Mock Subscribe to {topic}")  # Optional: for debug

    async def connect(self):
        self.is_connected = True
        print("Mock Connect")

    async def disconnect(self):
        self.is_connected = False
        print("Mock Disconnect")


@pytest.fixture
def mock_mycelium():
    return MockMyceliumInterface()


def get_test_config():
    """Get test configuration."""
    return {
        "validation_rules_file": "config/validation_rules.json",  # Relative path for service init
        "sanitization_rules_file": (
            "config/sanitization_rules.json"  # Relative path for service init
        ),
        "history_retention_days": 7,
        "validator_config": {},
    }


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Provides the temporary path as the project root for testing."""
    return tmp_path


@patch(
    "subsystems.ETHIK.service.EthikValidator", new_callable=MagicMock
)  # Use MagicMock for sync class
@patch(
    "subsystems.ETHIK.service.EthikSanitizer", new_callable=MagicMock
)  # Use MagicMock for sync class
def test_service_initialization(
    mock_sanitizer_cls, mock_validator_cls, test_config, mock_mycelium, project_root
):
    """Test if EthikService initializes validator and sanitizer correctly."""

    # Setup mock instances returned by the mocked classes
    mock_validator_instance = AsyncMock(spec=EthikValidator)
    mock_sanitizer_instance = AsyncMock(spec=EthikSanitizer)
    mock_validator_cls.return_value = mock_validator_instance
    mock_sanitizer_cls.return_value = mock_sanitizer_instance

    service = EthikService(test_config, mock_mycelium, project_root)

    # Assertions
    assert service.config == test_config
    assert service.interface == mock_mycelium
    assert service.project_root == project_root
    assert not service.running

    # Check if Validator and Sanitizer were instantiated
    mock_validator_cls.assert_called_once()
    mock_sanitizer_cls.assert_called_once()

    # Check the config passed to constructors (includes resolved absolute paths)
    validator_call_args = mock_validator_cls.call_args[0]
    sanitizer_call_args = mock_sanitizer_cls.call_args[0]

    expected_val_rules_path = str((project_root / "config" / "validation_rules.json").resolve())
    expected_san_rules_path = str((project_root / "config" / "sanitization_rules.json").resolve())

    assert validator_call_args[0]["rules_file"] == expected_val_rules_path
    assert validator_call_args[1] == mock_mycelium

    assert sanitizer_call_args[0]["rules_file"] == expected_san_rules_path
    assert sanitizer_call_args[1] == mock_mycelium


@pytest.mark.asyncio
@patch("subsystems.ETHIK.service.EthikValidator", new_callable=MagicMock)
@patch("subsystems.ETHIK.service.EthikSanitizer", new_callable=MagicMock)
async def test_service_start(
    mock_sanitizer_cls, mock_validator_cls, test_config, mock_mycelium, project_root
):
    """Test the start method of EthikService."""

    # Setup mock instances with async methods
    mock_validator_instance = AsyncMock(spec=EthikValidator)
    mock_sanitizer_instance = AsyncMock(spec=EthikSanitizer)
    mock_validator_cls.return_value = mock_validator_instance
    mock_sanitizer_cls.return_value = mock_sanitizer_instance

    service = EthikService(test_config, mock_mycelium, project_root)

    assert not service.running
    await service.start()

    # Assertions
    assert service.running
    mock_validator_instance.start_monitoring.assert_awaited_once()
    mock_sanitizer_instance.start_monitoring.assert_awaited_once()


@pytest.mark.asyncio
@patch("subsystems.ETHIK.service.EthikValidator", new_callable=MagicMock)
@patch("subsystems.ETHIK.service.EthikSanitizer", new_callable=MagicMock)
async def test_service_stop(
    mock_sanitizer_cls, mock_validator_cls, test_config, mock_mycelium, project_root
):
    """Test the stop method of EthikService."""

    # Setup mock instances with async methods
    mock_validator_instance = AsyncMock(spec=EthikValidator)
    mock_sanitizer_instance = AsyncMock(spec=EthikSanitizer)
    mock_validator_cls.return_value = mock_validator_instance
    mock_sanitizer_cls.return_value = mock_sanitizer_instance

    service = EthikService(test_config, mock_mycelium, project_root)

    # Start the service first
    await service.start()
    assert service.running

    # Stop the service
    await service.stop()

    # Assertions
    assert not service.running
    mock_validator_instance.stop_monitoring.assert_awaited_once()
    mock_sanitizer_instance.stop_monitoring.assert_awaited_once()


@pytest.mark.asyncio
@patch("subsystems.ETHIK.service.EthikValidator", new_callable=MagicMock)
@patch("subsystems.ETHIK.service.EthikSanitizer", new_callable=MagicMock)
async def test_service_start_stop_idempotency(
    mock_sanitizer_cls, mock_validator_cls, test_config, mock_mycelium, project_root
):
    """Test that start/stop methods handle being called multiple times."""

    mock_validator_instance = AsyncMock(spec=EthikValidator)
    mock_sanitizer_instance = AsyncMock(spec=EthikSanitizer)
    mock_validator_cls.return_value = mock_validator_instance
    mock_sanitizer_cls.return_value = mock_sanitizer_instance

    service = EthikService(test_config, mock_mycelium, project_root)

    # Stop before starting
    await service.stop()  # Should do nothing and not raise error
    assert not service.running
    mock_validator_instance.stop_monitoring.assert_not_called()
    mock_sanitizer_instance.stop_monitoring.assert_not_called()

    # Start multiple times
    await service.start()
    await service.start()  # Second call should be ignored
    assert service.running
    mock_validator_instance.start_monitoring.assert_awaited_once()  # Still called only once
    mock_sanitizer_instance.start_monitoring.assert_awaited_once()  # Still called only once

    # Stop multiple times
    await service.stop()
    await service.stop()  # Second call should be ignored
    assert not service.running
    mock_validator_instance.stop_monitoring.assert_awaited_once()  # Still called only once
    mock_sanitizer_instance.stop_monitoring.assert_awaited_once()  # Still called only once


# Add more tests as needed, e.g., error handling during start/stop

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - ATLAS Service Tests
=================================

Test suite for the main ATLAS Service.
Ensures proper initialization, lifecycle, and Mycelium handling.

Version: 1.0.0
"""

from pathlib import Path
from typing import Dict  # Added
from unittest.mock import MagicMock, patch

import pytest

from ..core.atlas_core import ATLASCore

# Import the service and components to potentially mock
from ..service import AtlasService


# Mock Mycelium Interface (Copied from ETHIK tests for now)
class MockMyceliumInterface:
    def __init__(self, node_id="mock_node"):
        self.node_id = node_id
        self.published_messages = []
        self.subscribed_topics = {}
        self.is_connected = True  # Assume connected for tests

    async def publish(self, topic, message):
        self.published_messages.append({"topic": topic, "message": message})
        # print(f"Mock Publish to {topic}: {message}") # Optional: for debug

    async def subscribe(self, topic, handler):
        if topic not in self.subscribed_topics:
            self.subscribed_topics[topic] = []
        self.subscribed_topics[topic].append(handler)
        # print(f"Mock Subscribe to {topic}") # Optional: for debug
        return f"sub_{topic}"  # Return a dummy subscription ID

    async def unsubscribe(self, subscription_id):
        # Basic mock unsubscribe - find topic by ID and remove handler (complex)
        # For simplicity, just log it
        print(f"Mock Unsubscribe: {subscription_id}")
        pass

    async def connect(self):
        self.is_connected = True
        print("Mock Connect")

    async def disconnect(self):
        self.is_connected = False
        print("Mock Disconnect")


@pytest.fixture
def mock_mycelium():
    return MockMyceliumInterface()


@pytest.fixture
def test_config(tmp_path: Path) -> Dict:
    """Provides a basic config dictionary for ATLAS service tests."""
    return {
        "data_directory": "atlas_test_data",  # Relative path for service init
        "log_level": "DEBUG",
        "core_config": {"visualization": {"default_format": "svg"}},  # Config for ATLASCore
    }


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Provides the temporary path as the project root for testing."""
    return tmp_path


# --- Mock ATLASCore --- #
# We need more control over the mock core for handler tests
@pytest.fixture
def mock_atlas_core():
    core = MagicMock()  # Use simple MagicMock instead of spec
    core.graph = MagicMock()  # Mock the graph attribute
    core.graph.number_of_nodes.return_value = 0
    core.graph.number_of_edges.return_value = 0
    # Configure mock methods used by handlers
    core.map_system.return_value = True
    core.generate_obsidian_content.return_value = ("markdown_content", Path("/fake/image.png"))
    core.export_to_obsidian.return_value = ("markdown_content", Path("/fake/image.png"))
    core.analyze_system.return_value = {"basic_metrics": {"num_nodes": 0}}
    return core


# -------------------- #


# Use patch to inject the mocked ATLASCore *instance*
@patch("subsystems.ATLAS.service.ATLASCore")
def test_service_initialization(
    mock_atlas_core_cls, test_config, mock_mycelium, project_root, mock_atlas_core
):
    """Test if AtlasService initializes ATLASCore correctly."""
    # Make the mocked class return our pre-configured mock instance
    mock_atlas_core_cls.return_value = mock_atlas_core

    service = AtlasService(test_config, mock_mycelium, project_root)

    # Assertions
    assert service.config == test_config
    assert service.interface == mock_mycelium
    assert service.project_root == project_root
    assert not service.running
    assert service.atlas_core == mock_atlas_core  # Check if the instance is stored

    # Just verify the ATLASCore was called and capture the call
    mock_atlas_core_cls.assert_called_once()
    args, kwargs = mock_atlas_core_cls.call_args

    # Check that config was passed correctly
    assert kwargs["config"] == test_config["core_config"]

    # Check that data_dir was created correctly
    expected_data_dir = (project_root / test_config["data_directory"]).resolve()
    assert kwargs["data_dir"] == expected_data_dir

    # We don't compare the logger directly as it might have a different name


@pytest.mark.asyncio
@patch("subsystems.ATLAS.service.ATLASCore")
async def test_service_start_and_subscribe(
    mock_atlas_core_cls, test_config, mock_mycelium, project_root
):
    """Test the start method subscribes to topics."""
    mock_atlas_core_cls.return_value = MagicMock(spec=ATLASCore)  # Simple mock needed

    service = AtlasService(test_config, mock_mycelium, project_root)

    await service.start()

    assert service.running
    # Check subscriptions
    expected_topics = [
        f"request.{service.node_id}.map_system",
        f"request.{service.node_id}.generate_obsidian",
        f"request.{service.node_id}.analyze_system",
    ]
    assert set(mock_mycelium.subscribed_topics.keys()) == set(expected_topics)
    # Check handlers were registered (basic check)
    assert (
        mock_mycelium.subscribed_topics[expected_topics[0]][0] == service.handle_map_system_request
    )
    assert (
        mock_mycelium.subscribed_topics[expected_topics[1]][0]
        == service.handle_generate_obsidian_request
    )
    assert (
        mock_mycelium.subscribed_topics[expected_topics[2]][0]
        == service.handle_analyze_system_request
    )


@pytest.mark.asyncio
@patch("subsystems.ATLAS.service.ATLASCore")
async def test_service_stop(mock_atlas_core_cls, test_config, mock_mycelium, project_root):
    """Test the stop method."""
    mock_atlas_core_cls.return_value = MagicMock(spec=ATLASCore)
    service = AtlasService(test_config, mock_mycelium, project_root)

    await service.start()  # Start first
    assert service.running

    await service.stop()
    assert not service.running
    # Add assertion for unsubscribe if implemented


@pytest.mark.asyncio
@patch("subsystems.ATLAS.service.ATLASCore")
async def test_handle_map_system_request(
    mock_atlas_core_cls, test_config, mock_mycelium, project_root, mock_atlas_core
):
    """Test the Mycelium handler for map_system requests."""
    mock_atlas_core_cls.return_value = mock_atlas_core
    service = AtlasService(test_config, mock_mycelium, project_root)

    request_message = {
        "id": "map-req-1",
        "payload": {"system_data": {"nodes": {"X": {}}, "edges": []}, "map_name": "MySystemMap"},
    }

    # Mock node/edge counts after mapping
    mock_atlas_core.graph.number_of_nodes.return_value = 1
    mock_atlas_core.graph.number_of_edges.return_value = 0

    await service.handle_map_system_request(request_message)

    # Verify atlas_core method was called
    mock_atlas_core.map_system.assert_called_once_with(
        request_message["payload"]["system_data"], request_message["payload"]["map_name"]
    )

    # Verify response was published
    assert len(mock_mycelium.published_messages) == 1
    response = mock_mycelium.published_messages[0]
    assert response["topic"] == f"response.{service.node_id}.map-req-1"
    assert response["message"]["type"] == "map_system_response"
    assert response["message"]["payload"]["success"] is True
    assert response["message"]["payload"]["map_name"] == "MySystemMap"
    assert response["message"]["payload"]["nodes_count"] == 1
    assert response["message"]["payload"]["edges_count"] == 0


@pytest.mark.asyncio
@patch("subsystems.ATLAS.service.ATLASCore")
async def test_handle_map_system_request_error(
    mock_atlas_core_cls, test_config, mock_mycelium, project_root, mock_atlas_core
):
    """Test error handling in map_system request handler."""
    mock_atlas_core_cls.return_value = mock_atlas_core
    service = AtlasService(test_config, mock_mycelium, project_root)

    # Simulate error during core processing
    mock_atlas_core.map_system.side_effect = ValueError("Mapping failed badly")

    # Provide a valid payload with system_data and map_name
    request_message = {
        "id": "map-req-err",
        "payload": {"system_data": {"nodes": {}, "edges": []}, "map_name": "test_map"},
    }

    await service.handle_map_system_request(request_message)

    # Verify error response was published
    assert len(mock_mycelium.published_messages) == 1
    response = mock_mycelium.published_messages[0]
    assert response["topic"] == f"response.{service.node_id}.map-req-err"
    assert response["message"]["type"] == "error"
    assert "Mapping failed badly" in response["message"]["payload"]["message"]


@pytest.mark.asyncio
@patch("subsystems.ATLAS.service.ATLASCore")
async def test_handle_generate_obsidian_request(
    mock_atlas_core_cls, test_config, mock_mycelium, project_root, mock_atlas_core
):
    """Test the Mycelium handler for generate_obsidian requests."""
    mock_atlas_core_cls.return_value = mock_atlas_core
    service = AtlasService(test_config, mock_mycelium, project_root)

    request_message = {"id": "obs-req-1", "payload": {}}

    # Configure mock return value for generate_obsidian_content
    mock_image_path = project_root / "atlas_test_data" / "obs_image.png"
    mock_atlas_core.generate_obsidian_content.return_value = ("# Test Content", mock_image_path)

    await service.handle_generate_obsidian_request(request_message)

    mock_atlas_core.generate_obsidian_content.assert_called_once()

    assert len(mock_mycelium.published_messages) == 1
    response = mock_mycelium.published_messages[0]
    assert response["topic"] == f"response.{service.node_id}.obs-req-1"
    assert response["message"]["type"] == "generate_obsidian_response"
    assert response["message"]["payload"]["success"] is True
    assert response["message"]["payload"]["markdown_content"] == "# Test Content"
    assert response["message"]["payload"]["image_path"] == str(mock_image_path)


@pytest.mark.asyncio
@patch("subsystems.ATLAS.service.ATLASCore")
async def test_handle_analyze_system_request(
    mock_atlas_core_cls, test_config, mock_mycelium, project_root, mock_atlas_core
):
    """Test the Mycelium handler for analyze_system requests."""
    mock_atlas_core_cls.return_value = mock_atlas_core
    service = AtlasService(test_config, mock_mycelium, project_root)

    request_message = {"id": "analyze-req-1", "payload": {}}

    # Configure mock return value
    mock_analysis = {"basic_metrics": {"num_nodes": 10}}
    mock_atlas_core.analyze_system.return_value = mock_analysis

    await service.handle_analyze_system_request(request_message)

    mock_atlas_core.analyze_system.assert_called_once()

    assert len(mock_mycelium.published_messages) == 1
    response = mock_mycelium.published_messages[0]
    assert response["topic"] == f"response.{service.node_id}.analyze-req-1"
    assert response["message"]["type"] == "analyze_system_response"
    assert response["message"]["payload"]["success"] is True
    assert response["message"]["payload"]["analysis"] == mock_analysis


@pytest.mark.asyncio
@patch("subsystems.ATLAS.service.ATLASCore")
async def test_start_already_running(mock_core_cls, test_config, mock_mycelium, project_root):
    """Test calling start when already running."""
    mock_core_cls.return_value = MagicMock()
    service = AtlasService(test_config, mock_mycelium, project_root)
    await service.start()
    subscribe_call_count = len(mock_mycelium.subscribed_topics)
    await service.start()  # Call start again
    # Check it didn't try to subscribe again
    assert len(mock_mycelium.subscribed_topics) == subscribe_call_count


@pytest.mark.asyncio
@patch("subsystems.ATLAS.service.ATLASCore")
async def test_stop_not_running(mock_core_cls, test_config, mock_mycelium, project_root):
    """Test calling stop when not running."""
    mock_core_cls.return_value = MagicMock()
    service = AtlasService(test_config, mock_mycelium, project_root)
    # Ensure stop doesn't raise error or change state
    await service.stop()
    assert not service.running


@pytest.mark.asyncio
@patch("subsystems.ATLAS.service.ATLASCore")
async def test_handle_map_system_invalid_payload(
    mock_core_cls, test_config, mock_mycelium, project_root
):
    """Test map_system handler with missing system_data."""
    mock_core_cls.return_value = MagicMock()
    service = AtlasService(test_config, mock_mycelium, project_root)
    request_message = {
        "id": "map-req-invalid",
        "payload": {"map_name": "InvalidMap"},  # Missing system_data
    }
    await service.handle_map_system_request(request_message)
    # Verify error response
    assert len(mock_mycelium.published_messages) == 1
    response = mock_mycelium.published_messages[0]
    assert response["topic"] == f"response.{service.node_id}.map-req-invalid"
    assert response["message"]["type"] == "error"
    assert "Missing or invalid 'system_data'" in response["message"]["payload"]["message"]


@pytest.mark.asyncio
@patch("subsystems.ATLAS.service.ATLASCore")
async def test_handle_generate_obsidian_error(
    mock_core_cls, test_config, mock_mycelium, project_root, mock_atlas_core
):
    """Test error handling in generate_obsidian handler."""
    mock_core_cls.return_value = mock_atlas_core
    service = AtlasService(test_config, mock_mycelium, project_root)
    # Simulate core method returning None (failure)
    mock_atlas_core.generate_obsidian_content.return_value = None
    request_message = {"id": "obs-req-err", "payload": {}}
    await service.handle_generate_obsidian_request(request_message)
    # Verify failure response
    assert len(mock_mycelium.published_messages) == 1
    response = mock_mycelium.published_messages[0]
    assert response["topic"] == f"response.{service.node_id}.obs-req-err"
    assert response["message"]["payload"]["success"] is False
    assert "Failed to generate" in response["message"]["payload"]["message"]


@pytest.mark.asyncio
@patch("subsystems.ATLAS.service.ATLASCore")
async def test_handle_analyze_system_error(
    mock_core_cls, test_config, mock_mycelium, project_root, mock_atlas_core
):
    """Test error handling in analyze_system handler."""
    mock_core_cls.return_value = mock_atlas_core
    service = AtlasService(test_config, mock_mycelium, project_root)
    # Simulate core method returning error dict
    mock_atlas_core.analyze_system.return_value = {"error": "Analysis exploded"}
    request_message = {"id": "analyze-req-err", "payload": {}}
    await service.handle_analyze_system_request(request_message)
    # Verify failure response
    assert len(mock_mycelium.published_messages) == 1
    response = mock_mycelium.published_messages[0]
    assert response["topic"] == f"response.{service.node_id}.analyze-req-err"
    assert response["message"]["payload"]["success"] is False
    assert response["message"]["payload"]["analysis"] == {"error": "Analysis exploded"}

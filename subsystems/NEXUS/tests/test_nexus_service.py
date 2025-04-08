#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - NEXUS Service Tests
=================================

Test suite for the main NEXUS Service.
Ensures proper initialization, lifecycle, and Mycelium handling.

Version: 1.0.0
"""

from pathlib import Path
from typing import Dict  # Added
from unittest.mock import MagicMock, patch

import pytest

from subsystems.NEXUS.core.nexus_core import NEXUSCore

# Import the service and components to potentially mock
from subsystems.NEXUS.service import NexusService


# Mock Mycelium Interface (Reused)
class MockMyceliumInterface:
    def __init__(self, node_id="mock_node"):
        self.node_id = node_id
        self.published_messages = []
        self.subscribed_topics = {}
        self.is_connected = True

    async def publish(self, topic, message):
        self.published_messages.append({"topic": topic, "message": message})

    async def subscribe(self, topic, handler):
        if topic not in self.subscribed_topics:
            self.subscribed_topics[topic] = []
        self.subscribed_topics[topic].append(handler)
        return f"sub_{topic}"

    async def unsubscribe(self, subscription_id):
        pass

    async def connect(self):
        self.is_connected = True

    async def disconnect(self):
        self.is_connected = False


@pytest.fixture
def mock_mycelium():
    return MockMyceliumInterface()


@pytest.fixture
def test_config(tmp_path: Path) -> Dict:
    """Provides a basic config dictionary for NEXUS service tests."""
    return {"log_level": "DEBUG", "core_config": {}}


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    return tmp_path


# Mock NEXUSCore
@pytest.fixture
def mock_nexus_core():
    core = MagicMock(spec=NEXUSCore)
    # Configure mock methods used by handlers
    core.analyze_code.return_value = {"lines": 10, "complexity": {"cognitive_load": 5}}
    core.analyze_workspace.return_value = {
        "metrics": {"total_files": 2},
        "files": {},
        "dependencies": {},
    }
    core.suggest_improvements.return_value = [{"type": "complexity", "message": "Too complex"}]
    return core


# --- Test Cases --- #


@patch("subsystems.NEXUS.service.NEXUSCore")
def test_service_initialization(
    mock_nexus_core_cls, test_config, mock_mycelium, project_root, mock_nexus_core
):
    """Test if NexusService initializes NEXUSCore correctly."""
    mock_nexus_core_cls.return_value = mock_nexus_core

    service = NexusService(test_config, mock_mycelium, project_root)

    assert service.config == test_config
    assert service.interface == mock_mycelium
    assert service.project_root == project_root
    assert not service.running
    assert service.nexus_core == mock_nexus_core

    mock_nexus_core_cls.assert_called_once_with(
        config=test_config["core_config"],
        logger=service.nexus_core_logger,
        project_root=project_root,
    )


@pytest.mark.asyncio
@patch("subsystems.NEXUS.service.NEXUSCore")
async def test_service_start_and_subscribe(
    mock_nexus_core_cls, test_config, mock_mycelium, project_root
):
    """Test the start method subscribes to topics."""
    mock_nexus_core_cls.return_value = MagicMock(spec=NEXUSCore)
    service = NexusService(test_config, mock_mycelium, project_root)

    await service.start()

    assert service.running
    expected_topics = [
        f"request.{service.node_id}.analyze_file",
        f"request.{service.node_id}.analyze_workspace",
        f"request.{service.node_id}.suggest_improvements",
    ]
    assert set(mock_mycelium.subscribed_topics.keys()) == set(expected_topics)
    assert (
        mock_mycelium.subscribed_topics[expected_topics[0]][0]
        == service.handle_analyze_file_request
    )
    assert (
        mock_mycelium.subscribed_topics[expected_topics[1]][0]
        == service.handle_analyze_workspace_request
    )
    assert (
        mock_mycelium.subscribed_topics[expected_topics[2]][0]
        == service.handle_suggest_improvements_request
    )


@pytest.mark.asyncio
@patch("subsystems.NEXUS.service.NEXUSCore")
async def test_service_stop(mock_nexus_core_cls, test_config, mock_mycelium, project_root):
    """Test the stop method."""
    mock_nexus_core_cls.return_value = MagicMock(spec=NEXUSCore)
    service = NexusService(test_config, mock_mycelium, project_root)

    await service.start()
    assert service.running

    await service.stop()
    assert not service.running


@pytest.mark.asyncio
@patch("subsystems.NEXUS.service.NEXUSCore")
async def test_handle_analyze_file_request(
    mock_nexus_core_cls, test_config, mock_mycelium, project_root, mock_nexus_core
):
    """Test the Mycelium handler for analyze_file requests."""
    mock_nexus_core_cls.return_value = mock_nexus_core
    service = NexusService(test_config, mock_mycelium, project_root)

    file_path = "src/test.py"
    request_message = {"id": "file-req-1", "payload": {"file_path": file_path}}

    await service.handle_analyze_file_request(request_message)

    mock_nexus_core.analyze_code.assert_called_once_with(file_path)
    assert len(mock_mycelium.published_messages) == 1
    response = mock_mycelium.published_messages[0]
    assert response["topic"] == f"response.{service.node_id}.file-req-1"
    assert response["message"]["type"] == "analyze_file_response"
    assert response["message"]["payload"]["success"] is True
    assert response["message"]["payload"]["file_path"] == file_path
    assert "analysis" in response["message"]["payload"]


@pytest.mark.asyncio
@patch("subsystems.NEXUS.service.NEXUSCore")
async def test_handle_analyze_workspace_request(
    mock_nexus_core_cls, test_config, mock_mycelium, project_root, mock_nexus_core
):
    """Test the Mycelium handler for analyze_workspace requests."""
    mock_nexus_core_cls.return_value = mock_nexus_core
    service = NexusService(test_config, mock_mycelium, project_root)

    request_message = {"id": "ws-req-1", "payload": {}}

    await service.handle_analyze_workspace_request(request_message)

    mock_nexus_core.analyze_workspace.assert_called_once()
    assert len(mock_mycelium.published_messages) == 1
    response = mock_mycelium.published_messages[0]
    assert response["topic"] == f"response.{service.node_id}.ws-req-1"
    assert response["message"]["type"] == "analyze_workspace_response"
    assert response["message"]["payload"]["success"] is True
    assert "analysis" in response["message"]["payload"]


@pytest.mark.asyncio
@patch("subsystems.NEXUS.service.NEXUSCore")
async def test_handle_suggest_improvements_request(
    mock_nexus_core_cls, test_config, mock_mycelium, project_root, mock_nexus_core
):
    """Test the Mycelium handler for suggest_improvements requests."""
    mock_nexus_core_cls.return_value = mock_nexus_core
    service = NexusService(test_config, mock_mycelium, project_root)

    analysis_data = {"metrics": {}, "files": {}, "dependencies": {}}
    request_message = {"id": "sug-req-1", "payload": {"analysis_data": analysis_data}}

    await service.handle_suggest_improvements_request(request_message)

    mock_nexus_core.suggest_improvements.assert_called_once_with(analysis_data)
    assert len(mock_mycelium.published_messages) == 1
    response = mock_mycelium.published_messages[0]
    assert response["topic"] == f"response.{service.node_id}.sug-req-1"
    assert response["message"]["type"] == "suggest_improvements_response"
    assert response["message"]["payload"]["success"] is True
    assert "suggestions" in response["message"]["payload"]
    assert len(response["message"]["payload"]["suggestions"]) == 1  # Based on mock

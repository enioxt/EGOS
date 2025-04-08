#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test suite for the Analyzer component in NEXUS.
"""

import asyncio
from datetime import datetime
import json

import pytest

# Import the real interface for type hinting, but we'll mock it
# Corrected absolute import for NexusAnalyzer
from subsystems.NEXUS.core.analyzer import NexusAnalyzer


# Renamed Mock Class
class MockMyceliumInterface:
    """Mock Mycelium interface for testing NexusAnalyzer."""

    def __init__(self):
        self.published_events = []  # Changed from published_messages
        self.handlers = {}
        self._node_id = "mock_nexus_node"  # Mock node ID for the interface

    def subscribe(self, topic: str):
        # This mock needs to store the callback associated with the topic
        # The actual interface registers with the network, we just store locally
        def decorator(func):
            if not asyncio.iscoroutinefunction(func):
                raise TypeError(f"Handler for topic '{topic}' must be an async function")
            self.handlers[topic] = func
            print(f"[MockInterface] Handler registered for topic: {topic}")  # Debug print
            return func

        return decorator

    async def publish_event(self, topic: str, payload: dict):
        # Mimics the publish_event method of the real interface
        # The real interface builds a full message dictionary
        message = {
            "header": {
                "message_id": f"mock_msg_{datetime.now().isoformat()}",
                "correlation_id": None,  # Events don't usually have correlation IDs
                "timestamp": datetime.now().isoformat(),
                "sender_node": self._node_id,
                "target_node": "TOPIC_TARGET",
                "topic": topic,
                "message_type": "EVENT",
                "priority": "MEDIUM",
                "version": "1.0",
            },
            "payload": payload,
        }
        self.published_events.append(message)
        print(f"[MockInterface] Event published to topic '{topic}': {payload}")  # Debug print

    async def simulate_message(
        self,
        topic: str,
        payload: dict,
        sender: str = "mock_sender",
        msg_type: str = "EVENT",
        correlation_id: str = None,
    ):
        """Simulate receiving a message for a subscribed topic."""
        print(f"[MockInterface] Simulating message for topic: {topic}")  # Debug print
        if topic in self.handlers:
            handler = self.handlers[topic]
            # Construct a message dictionary mimicking what the real handler expects
            message = {
                "header": {
                    "message_id": f"sim_msg_{datetime.now().isoformat()}",
                    "correlation_id": correlation_id,
                    "timestamp": datetime.now().isoformat(),
                    "sender_node": sender,
                    "target_node": self._node_id,  # Assuming message is directed to this node
                    "topic": topic,
                    "message_type": msg_type,
                    "priority": "MEDIUM",
                    "version": "1.0",
                },
                "payload": payload,
            }
            print(f"[MockInterface] Calling handler for topic '{topic}'...")  # Debug print
            try:
                await handler(message)
                print(f"[MockInterface] Handler for topic '{topic}' finished.")  # Debug print
            except Exception as e:
                print(f"[MockInterface] Error in handler for topic '{topic}': {e}")  # Debug print
                raise  # Re-raise the exception so the test fails
        else:
            print(f"[MockInterface] No handler found for topic: {topic}")  # Debug print


@pytest.fixture
def config_path(tmp_path):
    """Create a temporary config file."""
    config = {
        "cache_duration": 60,
        "analysis_timeout": 10,
        "mycelium": {
            "topics": {
                "analyze_request": "test.analyze.request",
                "analyze_result": "test.analyze.result",
                "dependency_update": "test.dependency.update",
                "dependency_status": "test.dependency.status",
                "module_update": "test.module.update",
                "module_status": "test.module.status",
                "alert": "test.alert",
            }
        },
    }

    config_file = tmp_path / "nexus_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f)

    return config_file


# Updated fixture name
@pytest.fixture
def mock_mycelium_interface():
    """Create a mock Mycelium interface."""
    return MockMyceliumInterface()


# Updated fixture name and type hint
@pytest.fixture
def analyzer(config_path, mock_mycelium_interface: MockMyceliumInterface):
    """Create a NexusAnalyzer instance with mock Mycelium interface."""
    # Pass the mock interface to the analyzer
    return NexusAnalyzer(config_path, mock_mycelium_interface)


@pytest.mark.asyncio
async def test_analyze_request_handler(
    analyzer: NexusAnalyzer, mock_mycelium_interface: MockMyceliumInterface
):
    """Test handling of analysis requests via Mycelium."""
    # Setup test data
    module = "test_module"
    dependencies = ["dep1", "dep2"]
    metadata = {"version": "1.0"}
    request_corr_id = "req-123"

    # Update module data directly in analyzer (as if updated previously)
    await analyzer.update_dependencies(module, dependencies, metadata)

    # Simulate analysis request message
    await mock_mycelium_interface.simulate_message(
        topic=analyzer.topics["analyze_request"],
        payload={"target": module, "type": "dependencies", "include_metadata": True},
        msg_type="REQUEST",  # Assuming requests come as REQUEST type
        correlation_id=request_corr_id,
    )

    # Check published events
    assert len(mock_mycelium_interface.published_events) == 1, "Expected one event to be published"
    result_event = mock_mycelium_interface.published_events[0]
    assert (
        result_event["header"]["topic"] == analyzer.topics["analyze_result"]
    ), "Event topic mismatch"
    assert result_event["payload"]["result"]["module"] == module, "Module name mismatch in result"
    assert (
        result_event["payload"]["result"]["dependencies"] == dependencies
    ), "Dependencies mismatch in result"
    assert (
        result_event["payload"]["result"]["metadata"]["version"] == "1.0"
    ), "Metadata mismatch in result"
    assert (
        result_event["payload"]["request_id"] == request_corr_id
    ), "Correlation ID mismatch in result event"


@pytest.mark.asyncio
async def test_dependency_update_handler(
    analyzer: NexusAnalyzer, mock_mycelium_interface: MockMyceliumInterface
):
    """Test handling of dependency updates via Mycelium."""
    module = "test_module"
    dependencies = ["dep1", "dep2"]
    metadata = {"version": "1.0"}
    request_corr_id = "dep-upd-456"

    # Simulate dependency update message (assuming it's an EVENT)
    await mock_mycelium_interface.simulate_message(
        topic=analyzer.topics["dependency_update"],
        payload={"module": module, "dependencies": dependencies, "metadata": metadata},
        msg_type="EVENT",  # Or potentially REQUEST depending on system design
        correlation_id=request_corr_id,  # Pass correlation id if expected
    )

    # Check published confirmation event
    assert len(mock_mycelium_interface.published_events) == 1
    status_event = mock_mycelium_interface.published_events[0]
    assert status_event["header"]["topic"] == analyzer.topics["dependency_status"]
    assert status_event["payload"]["status"] == "success"
    assert status_event["payload"]["module"] == module
    assert status_event["payload"]["request_id"] == request_corr_id

    # Verify dependencies were updated internally in the analyzer
    result = await analyzer.analyze_module(module)
    assert result["dependencies"] == dependencies
    assert result["metadata"]["version"] == "1.0"


@pytest.mark.asyncio
async def test_module_update_handler(
    analyzer: NexusAnalyzer, mock_mycelium_interface: MockMyceliumInterface
):
    """Test handling of module updates via Mycelium."""
    module = "test_module"
    metadata = {"version": "2.0", "author": "test"}
    request_corr_id = "mod-upd-789"

    # Simulate module update message
    await mock_mycelium_interface.simulate_message(
        topic=analyzer.topics["module_update"],
        payload={"module": module, "metadata": metadata},
        msg_type="EVENT",  # Assuming EVENT
        correlation_id=request_corr_id,
    )

    # Check published confirmation event
    assert len(mock_mycelium_interface.published_events) == 1
    status_event = mock_mycelium_interface.published_events[0]
    assert status_event["header"]["topic"] == analyzer.topics["module_status"]
    assert status_event["payload"]["status"] == "success"
    assert status_event["payload"]["module"] == module
    assert status_event["payload"]["request_id"] == request_corr_id

    # Verify metadata was updated internally
    result = await analyzer.analyze_module(module)
    assert result["metadata"] == metadata


@pytest.mark.asyncio
async def test_error_handling(
    analyzer: NexusAnalyzer, mock_mycelium_interface: MockMyceliumInterface
):
    """Test error handling in Mycelium message handlers."""
    request_corr_id = "err-req-abc"

    # Simulate invalid analysis request (missing target in payload)
    await mock_mycelium_interface.simulate_message(
        topic=analyzer.topics["analyze_request"],
        payload={
            # Missing "target"
            "type": "dependencies"
        },
        msg_type="REQUEST",
        correlation_id=request_corr_id,
    )

    # Check error event response
    assert len(mock_mycelium_interface.published_events) == 1
    error_event = mock_mycelium_interface.published_events[0]
    assert error_event["header"]["topic"] == analyzer.topics["analyze_result"]
    assert error_event["payload"]["status"] == "error"
    assert "error" in error_event["payload"]
    assert error_event["payload"]["request_id"] == request_corr_id


@pytest.mark.asyncio
async def test_alert_publishing(
    analyzer: NexusAnalyzer, mock_mycelium_interface: MockMyceliumInterface
):
    """Test publishing alerts through Mycelium."""
    alert_type = "test_alert"
    message = "Test alert message"
    details = {"key": "value"}

    # Call the internal publish alert method
    await analyzer._publish_alert(alert_type, message, details)

    # Check published alert event
    assert len(mock_mycelium_interface.published_events) == 1
    alert_event = mock_mycelium_interface.published_events[0]
    assert alert_event["header"]["topic"] == analyzer.topics["alert"]
    assert alert_event["payload"]["type"] == alert_type
    assert alert_event["payload"]["message"] == message
    assert alert_event["payload"]["details"] == details


@pytest.mark.asyncio
async def test_cache_behavior(analyzer: NexusAnalyzer):  # No mock needed here
    """Test module analysis caching."""
    module = "test_module"
    dependencies = ["dep1"]

    # Update module
    await analyzer.update_dependencies(module, dependencies)

    # First analysis
    result1 = await analyzer.analyze_module(module)
    assert result1["dependencies"] == dependencies

    # Simulate time passing (or check cache directly if possible)
    # For simplicity, we'll just update and re-analyze

    # Update dependencies
    new_dependencies = ["dep2"]
    await analyzer.update_dependencies(module, new_dependencies)

    # Second analysis should reflect new dependencies because cache was cleared
    result2 = await analyzer.analyze_module(module)
    assert result2["dependencies"] == new_dependencies


# This test doesn't need the mock interface
@pytest.mark.asyncio
async def test_config_loading(tmp_path):
    """Test configuration loading and defaults."""
    # Test with no config file (passing None)
    analyzer_no_config = NexusAnalyzer(config_path=None, mycelium_interface=None)
    assert analyzer_no_config.config["cache_duration"] == 300

    # Test with custom config
    config = {
        "cache_duration": 600,
        "analysis_timeout": 20,
        "mycelium": {  # Need to include mycelium structure for deep merge
            "topics": {"analyze_request": "custom.request"}
        },
    }
    config_file = tmp_path / "custom_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f)

    analyzer_custom_config = NexusAnalyzer(config_file, mycelium_interface=None)
    assert analyzer_custom_config.config["cache_duration"] == 600
    assert analyzer_custom_config.config["analysis_timeout"] == 20
    # Check deep merge
    assert (
        analyzer_custom_config.config["mycelium"]["topics"]["analyze_request"] == "custom.request"
    )
    assert (
        analyzer_custom_config.config["mycelium"]["topics"]["analyze_result"]
        == "nexus.analyze.result"
    )  # Default preserved

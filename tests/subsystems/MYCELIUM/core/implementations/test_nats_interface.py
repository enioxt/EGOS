"""Unit tests for the NatsMyceliumInterface implementation."""

import asyncio
from datetime import datetime, timezone
import json
import logging
from typing import Dict
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

import nats
from nats.aio.msg import Msg
from nats.errors import NoServersError
import pytest

from subsystems.MYCELIUM.core.implementations.nats_interface import NatsMyceliumInterface

# Constants for testing
TEST_SERVERS = ["nats://localhost:4222"]
TEST_SUBJECT = "test.subject"
TEST_PAYLOAD = {"data": "test_value", "number": 123}
TEST_SOURCE_SUBSYSTEM = "TEST_SUB"


@pytest.fixture
def mock_nats_client():
    """Provides a mocked NATS client connection object."""
    mock_nc = AsyncMock(spec=nats.NATS)
    mock_nc.is_connected = True
    # Mock the connected_url attribute (might need adjustment based on actual usage)
    mock_nc.connected_url = MagicMock()
    mock_nc.connected_url.netloc = "mockserver:4222"
    # Set default return values for async methods if needed immediately
    # mock_nc.publish = AsyncMock()
    # mock_nc.subscribe = AsyncMock()
    # mock_nc.request = AsyncMock()
    # mock_nc.close = AsyncMock()
    return mock_nc


@pytest.fixture
async def nats_interface_with_mock_connect(mock_nats_client):
    """Provides NatsMyceliumInterface instance and the mocked nats.connect function."""
    interface = NatsMyceliumInterface(source_subsystem=TEST_SOURCE_SUBSYSTEM)
    with patch(
        "subsystems.MYCELIUM.core.implementations.nats_interface.nats.connect",
        return_value=mock_nats_client,
    ) as mock_connect:
        # Yield both the interface and the mock connect function
        yield interface, mock_connect
        # Ensure disconnection if connected during a test
        if interface._nc and interface._nc.is_connected:
            await interface.disconnect()


# --- Test Class ---
# Grouping tests for better organization


class TestNatsMyceliumInterface:
    @pytest.mark.asyncio
    async def test_connect_success(
        self, nats_interface_with_mock_connect, mock_nats_client: AsyncMock
    ):
        """Test successful connection to NATS."""
        nats_interface, mock_connect = nats_interface_with_mock_connect
        await nats_interface.connect(TEST_SERVERS)
        mock_connect.assert_awaited_once_with(servers=TEST_SERVERS)
        assert nats_interface._nc is mock_nats_client
        assert nats_interface._nc.is_connected is True

    @pytest.mark.asyncio
    async def test_connect_already_connected(
        self, nats_interface_with_mock_connect, mock_nats_client: AsyncMock
    ):
        """Test attempting to connect when already connected."""
        nats_interface, mock_connect = nats_interface_with_mock_connect
        # Connect first time
        await nats_interface.connect(TEST_SERVERS)
        connect_call_count = mock_connect.await_count
        # Attempt to connect again
        await nats_interface.connect(TEST_SERVERS)
        # Assert connect wasn't called again
        assert mock_connect.await_count == connect_call_count

    @pytest.mark.asyncio
    async def test_connect_failure_no_servers(self, nats_interface_with_mock_connect):
        """Test connection failure due to NoServersError."""
        # This test does its own patching, so doesn't strictly need the fixture's mock_connect
        nats_interface, _ = nats_interface_with_mock_connect
        with patch(
            "subsystems.MYCELIUM.core.implementations.nats_interface.nats.connect",
            side_effect=NoServersError,
        ) as mock_connect_local:
            with pytest.raises(ConnectionError, match="No servers available"):
                await nats_interface.connect(TEST_SERVERS)
            mock_connect_local.assert_awaited_once_with(servers=TEST_SERVERS)
            assert nats_interface._nc is None

    @pytest.mark.asyncio
    async def test_disconnect_success(
        self, nats_interface_with_mock_connect, mock_nats_client: AsyncMock
    ):
        """Test successful disconnection."""
        nats_interface, _ = nats_interface_with_mock_connect
        await nats_interface.connect(TEST_SERVERS)  # Ensure connected
        assert nats_interface._nc is mock_nats_client
        await nats_interface.disconnect()
        mock_nats_client.close.assert_awaited_once()
        assert nats_interface._nc is None

    @pytest.mark.asyncio
    async def test_disconnect_when_not_connected(self, nats_interface_with_mock_connect):
        """Test calling disconnect when not connected."""
        nats_interface, _ = nats_interface_with_mock_connect
        await nats_interface.disconnect()

    @pytest.mark.asyncio
    async def test_publish_success(
        self, nats_interface_with_mock_connect, mock_nats_client: AsyncMock
    ):
        """Test successful publishing of a message."""
        nats_interface, _ = nats_interface_with_mock_connect
        await nats_interface.connect(TEST_SERVERS)
        test_data = {"key": "value"}
        await nats_interface.publish(TEST_SUBJECT, test_data)
        mock_nats_client.publish.assert_awaited_once()
        call_args = mock_nats_client.publish.await_args
        sent_subject = call_args.args[0]
        sent_payload_bytes = call_args.args[1]

        assert sent_subject == TEST_SUBJECT
        # Verify the payload was wrapped correctly
        try:
            sent_envelope = json.loads(sent_payload_bytes.decode("utf-8"))
            assert isinstance(sent_envelope, dict)
            assert sent_envelope["source_subsystem"] == TEST_SOURCE_SUBSYSTEM
            assert sent_envelope["payload"] == test_data
            assert "message_id" in sent_envelope
            assert "timestamp" in sent_envelope
        except (json.JSONDecodeError, KeyError, AssertionError) as e:
            pytest.fail(f"Payload verification failed: {e}\nPayload bytes: {sent_payload_bytes}")

    @pytest.mark.asyncio
    async def test_publish_not_connected(self, nats_interface_with_mock_connect):
        """Test publishing when not connected raises ConnectionError."""
        nats_interface, _ = nats_interface_with_mock_connect
        with pytest.raises(ConnectionError, match="Not connected to NATS"):
            await nats_interface.publish(TEST_SUBJECT, {"data": "test"})

    @pytest.mark.asyncio
    async def test_subscribe_success(
        self, nats_interface_with_mock_connect, mock_nats_client: AsyncMock
    ):
        """Test successful subscription to a subject."""
        nats_interface, _ = nats_interface_with_mock_connect
        await nats_interface.connect(TEST_SERVERS)

        async def dummy_callback(payload: Dict):
            pass

        mock_sub = AsyncMock(spec=nats.aio.subscription.Subscription)
        mock_sub.subject = TEST_SUBJECT
        mock_nats_client.subscribe.return_value = mock_sub
        sub_id = await nats_interface.subscribe(TEST_SUBJECT, dummy_callback)
        mock_nats_client.subscribe.assert_awaited_once()
        call_args = mock_nats_client.subscribe.await_args
        assert call_args.args[0] == TEST_SUBJECT
        assert callable(call_args.kwargs.get("cb"))  # Check that a callback was registered

        # Assert subscription ID is stored and is a UUID string
        assert isinstance(sub_id, str)
        try:
            uuid.UUID(sub_id)  # Check if it's a valid UUID
        except ValueError:
            pytest.fail("Subscription ID is not a valid UUID string")
        assert sub_id in nats_interface._subscriptions
        assert nats_interface._subscriptions[sub_id] is mock_sub

    @pytest.mark.asyncio
    async def test_unsubscribe_success(
        self, nats_interface_with_mock_connect, mock_nats_client: AsyncMock
    ):
        """Test successful unsubscription."""
        nats_interface, _ = nats_interface_with_mock_connect
        await nats_interface.connect(TEST_SERVERS)

        async def dummy_callback(payload: Dict):
            pass

        mock_sub = AsyncMock(spec=nats.aio.subscription.Subscription)
        mock_sub.subject = TEST_SUBJECT
        mock_nats_client.subscribe.return_value = mock_sub
        sub_id = await nats_interface.subscribe(TEST_SUBJECT, dummy_callback)
        assert sub_id in nats_interface._subscriptions
        await nats_interface.unsubscribe(sub_id)
        mock_sub.unsubscribe.assert_awaited_once()
        assert sub_id not in nats_interface._subscriptions

    @pytest.mark.asyncio
    async def test_unsubscribe_unknown_id(self, nats_interface_with_mock_connect):
        """Test unsubscribing with an unknown ID does not raise errors."""
        nats_interface, _ = nats_interface_with_mock_connect
        await nats_interface.connect(TEST_SERVERS)
        await nats_interface.unsubscribe("non_existent_id")

    @pytest.mark.asyncio
    async def test_request_success(
        self, nats_interface_with_mock_connect, mock_nats_client: AsyncMock
    ):
        """Test successful request/response interaction."""
        nats_interface, _ = nats_interface_with_mock_connect
        await nats_interface.connect(TEST_SERVERS)
        test_request_payload = {"req_data": "find_this"}
        test_response_payload = {"res_data": "found_it"}
        response_envelope = {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_subsystem": "RESPONDER_SUB",  # Simulate response from another sub
            "correlation_id": None,  # NATS request handles correlation; wrapper adds it for request
            "payload": test_response_payload,
            "metadata": {},
        }
        response_bytes = json.dumps(response_envelope).encode("utf-8")
        mock_response_msg = MagicMock(spec=Msg)
        mock_response_msg.data = response_bytes
        mock_nats_client.request.return_value = mock_response_msg

        response = await nats_interface.request(TEST_SUBJECT, test_request_payload, timeout=0.1)
        mock_nats_client.request.assert_awaited_once()
        call_args = mock_nats_client.request.await_args
        sent_subject = call_args.args[0]
        sent_payload_bytes = call_args.args[1]
        sent_timeout = call_args.kwargs.get("timeout")

        assert sent_subject == TEST_SUBJECT
        assert sent_timeout == 0.1

        # Verify the request payload was wrapped
        try:
            sent_envelope = json.loads(sent_payload_bytes.decode("utf-8"))
            assert sent_envelope["source_subsystem"] == TEST_SOURCE_SUBSYSTEM
            assert sent_envelope["payload"] == test_request_payload
            assert "correlation_id" in sent_envelope and sent_envelope["correlation_id"] is not None
        except (json.JSONDecodeError, KeyError, AssertionError) as e:
            pytest.fail(
                f"Request payload verification failed: {e}\nPayload bytes: {sent_payload_bytes}"
            )

        # Assert the returned response is the unwrapped envelope dictionary
        assert isinstance(response, dict)
        assert response["payload"] == test_response_payload
        assert response["source_subsystem"] == "RESPONDER_SUB"

    @pytest.mark.asyncio
    async def test_callback_invocation(
        self, nats_interface_with_mock_connect, mock_nats_client: AsyncMock
    ):
        """Test that the callback function is invoked with the correct payload."""
        nats_interface, _ = nats_interface_with_mock_connect
        await nats_interface.connect(TEST_SERVERS)

        received_payload = None
        callback_called = asyncio.Event()

        async def test_callback(payload: Dict):
            nonlocal received_payload
            received_payload = payload
            callback_called.set()

        # Mock the subscription object and capture the internal NATS callback
        mock_sub = AsyncMock(spec=nats.aio.subscription.Subscription)
        mock_sub.subject = TEST_SUBJECT
        nats_callback = None

        async def capture_callback(*args, **kwargs):
            nonlocal nats_callback
            nats_callback = kwargs.get("cb")
            return mock_sub

        mock_nats_client.subscribe.side_effect = capture_callback

        await nats_interface.subscribe(TEST_SUBJECT, test_callback)

        # Ensure the internal callback was captured
        assert nats_callback is not None

        # --- Simulate receiving a message ---
        # Prepare a simulated incoming message with a wrapped payload
        simulated_payload_dict = {"sim_key": "sim_value"}
        simulated_envelope = {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_subsystem": "SIM_SOURCE",
            "correlation_id": None,
            "payload": simulated_payload_dict,
            "metadata": {},
        }
        simulated_bytes = json.dumps(simulated_envelope).encode("utf-8")
        mock_nats_msg = MagicMock(spec=Msg)
        mock_nats_msg.data = simulated_bytes
        mock_nats_msg.subject = TEST_SUBJECT

        # Directly invoke the captured internal handler
        await nats_callback(mock_nats_msg)

        # Wait for the user callback to be called
        try:
            await asyncio.wait_for(callback_called.wait(), timeout=0.1)
        except asyncio.TimeoutError:
            pytest.fail("Test callback was not invoked within timeout")

        # Assert the received payload in the user callback is the correct unwrapped envelope
        assert received_payload is not None
        assert isinstance(received_payload, dict)
        assert received_payload["payload"] == simulated_payload_dict
        assert received_payload["source_subsystem"] == "SIM_SOURCE"

    @pytest.mark.asyncio
    async def test_callback_payload_unwrapping_error(
        self, nats_interface_with_mock_connect, mock_nats_client: AsyncMock
    ):
        """Test error handling when received payload is invalid JSON."""
        nats_interface, _ = nats_interface_with_mock_connect
        await nats_interface.connect(TEST_SERVERS)

        callback_called_flag = False

        async def failing_callback(payload: Dict):
            nonlocal callback_called_flag
            callback_called_flag = True  # Should not be called

        # Capture the internal NATS callback
        nats_callback = None
        mock_sub = AsyncMock(spec=nats.aio.subscription.Subscription)

        async def capture_callback(*args, **kwargs):
            nonlocal nats_callback
            nats_callback = kwargs.get("cb")
            return mock_sub

        mock_nats_client.subscribe.side_effect = capture_callback
        await nats_interface.subscribe(TEST_SUBJECT, failing_callback)
        assert nats_callback is not None

        # Simulate receiving invalid JSON bytes
        invalid_bytes = b'{"invalid_json": "\'}'  # Corrected byte string
        mock_nats_msg = MagicMock(spec=Msg)
        mock_nats_msg.data = invalid_bytes
        mock_nats_msg.subject = TEST_SUBJECT

        # Invoke the handler - it should catch the JSONDecodeError and log, not raise
        # Use caplog fixture to check logs if necessary
        try:
            await nats_callback(mock_nats_msg)
        except Exception as e:
            pytest.fail(f"Internal message_handler raised unexpected exception: {e}")

        # Assert the user callback was NOT called
        assert callback_called_flag is False

    @pytest.mark.asyncio
    async def test_callback_execution_error(
        self, nats_interface_with_mock_connect, mock_nats_client: AsyncMock, caplog
    ):
        """Test that errors *within* the user callback are caught and logged."""
        nats_interface, _ = nats_interface_with_mock_connect
        await nats_interface.connect(TEST_SERVERS)

        custom_error_message = "Callback failed!"

        async def error_callback(payload: Dict):
            raise ValueError(custom_error_message)

        # Capture the internal NATS callback
        nats_callback = None
        mock_sub = AsyncMock(spec=nats.aio.subscription.Subscription)

        async def capture_callback(*args, **kwargs):
            nonlocal nats_callback
            nats_callback = kwargs.get("cb")
            return mock_sub

        mock_nats_client.subscribe.side_effect = capture_callback
        await nats_interface.subscribe(TEST_SUBJECT, error_callback)
        assert nats_callback is not None

        # Prepare valid message
        simulated_payload_dict = {"data": "valid"}
        simulated_envelope = {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_subsystem": "SIM_SOURCE",
            "correlation_id": None,
            "payload": simulated_payload_dict,
            "metadata": {},
        }
        simulated_bytes = json.dumps(simulated_envelope).encode("utf-8")
        mock_nats_msg = MagicMock(spec=Msg)
        mock_nats_msg.data = simulated_bytes
        mock_nats_msg.subject = TEST_SUBJECT

        # Invoke handler - it should catch the ValueError from the callback
        with caplog.at_level(logging.ERROR):
            try:
                await nats_callback(mock_nats_msg)
            except Exception as e:
                pytest.fail(f"Internal message_handler raised unexpected exception: {e}")

        # Assert that the specific error from the callback was logged
        assert f"Error in callback for subject '{TEST_SUBJECT}'" in caplog.text
        assert custom_error_message in caplog.text

    @pytest.mark.asyncio
    async def test_request_timeout(
        self, nats_interface_with_mock_connect, mock_nats_client: AsyncMock
    ):
        """Test that a TimeoutError is raised if the request times out."""
        nats_interface, _ = nats_interface_with_mock_connect
        await nats_interface.connect(TEST_SERVERS)
        test_request_payload = {"req_data": "wait_long"}

        # Configure the mock nc.request to raise a NATS TimeoutError
        mock_nats_client.request.side_effect = nats.errors.TimeoutError

        # Perform the request and assert TimeoutError is raised
        with pytest.raises(TimeoutError, match=f"Timeout waiting for response from {TEST_SUBJECT}"):
            await nats_interface.request(TEST_SUBJECT, test_request_payload, timeout=0.01)

        # Assert nc.request was called
        mock_nats_client.request.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_request_not_connected(self, nats_interface_with_mock_connect):
        """Test that requesting when not connected raises ConnectionError."""
        nats_interface, _ = nats_interface_with_mock_connect
        # Do not connect
        with pytest.raises(ConnectionError, match="Not connected to NATS"):
            await nats_interface.request(TEST_SUBJECT, {"data": "test"}, timeout=0.01)

    @pytest.mark.asyncio
    async def test_request_serialization_error(
        self, nats_interface_with_mock_connect, mock_nats_client: AsyncMock
    ):
        """Test that an error during request payload serialization is handled."""
        nats_interface, _ = nats_interface_with_mock_connect
        await nats_interface.connect(TEST_SERVERS)

        # Payload that cannot be JSON serialized (e.g., bytes)
        non_serializable_payload = {b"bytes_key": b"bytes_value"}

        with pytest.raises(ValueError, match="Cannot serialize payload to JSON"):
            await nats_interface.request(TEST_SUBJECT, non_serializable_payload, timeout=0.01)

        # Ensure the underlying NATS request wasn't even called
        mock_nats_client.request.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_request_deserialization_error(
        self, nats_interface_with_mock_connect, mock_nats_client: AsyncMock
    ):
        """Test that an error during response payload deserialization is handled."""
        nats_interface, _ = nats_interface_with_mock_connect
        await nats_interface.connect(TEST_SERVERS)
        test_request_payload = {"req_data": "get_bad_response"}

        # Prepare a mock response message with invalid JSON data
        invalid_response_bytes = b"[invalid json]"
        mock_response_msg = MagicMock(spec=Msg)
        mock_response_msg.data = invalid_response_bytes
        mock_nats_client.request.return_value = mock_response_msg

        # Perform the request and assert ValueError is raised during unwrapping
        with pytest.raises(ValueError, match="Cannot deserialize received message from JSON"):
            await nats_interface.request(TEST_SUBJECT, test_request_payload, timeout=0.01)

        # Assert nc.request was still called
        mock_nats_client.request.assert_awaited_once()

    # ... rest of the placeholders ...

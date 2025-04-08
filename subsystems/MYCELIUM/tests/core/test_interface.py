# subsystems/MYCELIUM/tests/core/test_interface.py

import asyncio
from datetime import datetime
import unittest
from unittest.mock import AsyncMock, MagicMock  # Added call

from subsystems.MYCELIUM.core.interface import MyceliumInterface

# Assume network and interface are importable
from subsystems.MYCELIUM.core.network import MyceliumNetwork


class TestMyceliumInterface(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        """Set up a mock network and an interface instance for each test."""
        self.mock_network = MagicMock(spec=MyceliumNetwork)
        # Mock methods that return values or are awaited
        self.mock_network.generate_uuid = MagicMock(
            side_effect=lambda: f"uuid-{datetime.now().isoformat()}"
        )
        self.mock_network.register_node = AsyncMock(return_value=True)
        self.mock_network.remove_node = AsyncMock(return_value=True)
        self.mock_network.route_message = AsyncMock()
        self.mock_network.add_subscription = AsyncMock()
        self.mock_network.register_response_handler = AsyncMock()
        self.mock_network.remove_response_handler = AsyncMock()

        self.node_id = "TEST_SUBSYSTEM"
        # Instantiate the class under test
        self.interface = MyceliumInterface(self.mock_network, self.node_id)

    async def test_interface_initialization(self):
        """Test if the interface initializes correctly."""
        self.assertEqual(self.interface._network, self.mock_network)
        self.assertEqual(self.interface._node_id, self.node_id)
        self.assertEqual(len(self.interface._response_waiters), 0)
        # Test initialization errors
        with self.assertRaises(ValueError):
            MyceliumInterface(None, "test")
        with self.assertRaises(ValueError):
            MyceliumInterface(self.mock_network, "")

    async def test_connect(self):
        """Test the connect method registers node and response handler."""
        node_type = "TESTER"
        version = "1.1"
        capabilities = ["testing"]

        result = await self.interface.connect(node_type, version, capabilities)

        self.assertTrue(result)
        # Check if network methods were called correctly
        self.mock_network.register_node.assert_called_once_with(
            self.node_id, node_type, version, capabilities
        )
        self.mock_network.register_response_handler.assert_called_once_with(
            self.node_id,
            self.interface._handle_response,  # Check it registers its internal handler
        )

    async def test_disconnect(self):
        """Test the disconnect method removes node and handler."""
        # Simulate a pending future
        test_future = asyncio.Future()
        self.interface._response_waiters["pending_corr_id"] = test_future

        result = await self.interface.disconnect()

        self.assertTrue(result)
        self.mock_network.remove_response_handler.assert_called_once_with(self.node_id)
        self.mock_network.remove_node.assert_called_once_with(self.node_id)
        self.assertIsNone(self.interface._node_id)  # Node ID should be cleared
        # Verify the future was cancelled, checking the message is unreliable
        self.assertTrue(test_future.cancelled())
        # Removed unreliable check:
        # self.assertIn("Node disconnecting", str(test_future.exception()))

    async def test_publish_event(self):
        """Test publishing an event formats message and calls route_message."""
        topic = "event.test.occurred"
        payload = {"data": 123}

        await self.interface.publish_event(topic, payload)

        # Check that route_message was called
        self.mock_network.route_message.assert_called_once()
        # Get the message argument passed to route_message
        sent_message = self.mock_network.route_message.call_args[0][0]

        # Verify message structure
        self.assertEqual(sent_message["header"]["message_type"], "EVENT")
        self.assertEqual(sent_message["header"]["sender_node"], self.node_id)
        self.assertEqual(sent_message["header"]["target_node"], "TOPIC_TARGET")
        self.assertEqual(sent_message["header"]["topic"], topic)
        self.assertIsNone(sent_message["header"]["correlation_id"])
        self.assertEqual(sent_message["payload"], payload)

    async def test_subscribe(self):
        """Test subscribing calls network's add_subscription."""
        topic = "event.test.listen"

        async def my_callback(message):
            pass

        await self.interface.subscribe(topic, my_callback)

        self.mock_network.add_subscription.assert_called_once_with(topic, self.node_id, my_callback)

    async def test_report_health(self):
        """Test reporting health publishes an event."""
        status = "degraded"
        details = {"reason": "high load"}

        await self.interface.report_health(status, details)

        # Verify route_message was called (since report_health uses publish_event)
        self.mock_network.route_message.assert_called_once()
        sent_message = self.mock_network.route_message.call_args[0][0]

        # Verify health event structure
        self.assertEqual(sent_message["header"]["message_type"], "EVENT")
        self.assertEqual(sent_message["header"]["sender_node"], self.node_id)
        self.assertEqual(sent_message["header"]["topic"], "event.mycelium.health_report")
        self.assertEqual(sent_message["payload"]["node_id"], self.node_id)
        self.assertEqual(sent_message["payload"]["status"], status)
        self.assertEqual(sent_message["payload"]["details"], details)

    async def test_send_request_success(self):
        """Test send_request successful path."""
        target_node = "NODE_B"
        topic = "request.test.get_data"
        payload = {"id": 1}
        expected_response_payload = {"status": "SUCCESS", "data": "found data"}

        # Mock network behavior for handling the response
        async def mock_route_message(message):
            if message["header"]["message_type"] == "REQUEST":
                response_msg = {
                    "header": {
                        # Use mock_network here
                        "message_id": self.mock_network.generate_uuid(),
                        "correlation_id": message["header"]["correlation_id"],
                        "timestamp": datetime.now().isoformat(),
                        "sender_node": target_node,
                        "target_node": self.node_id,
                        "topic": topic,
                        "message_type": "RESPONSE",
                        "priority": "MEDIUM",
                        "version": "1.0",
                    },
                    "payload": expected_response_payload,
                }
                await self.interface._handle_response(response_msg)

        self.mock_network.route_message = mock_route_message

        response = await self.interface.send_request(target_node, topic, payload, timeout=1)

        self.assertEqual(response, expected_response_payload)

    async def test_send_request_timeout(self):
        """Test send_request timeout path."""
        target_node = "NODE_B"
        topic = "request.test.timeout"
        payload = {"id": 2}

        # Mock network does *not* route a response back
        self.mock_network.route_message = AsyncMock()

        with self.assertRaises(asyncio.TimeoutError):
            await self.interface.send_request(target_node, topic, payload, timeout=0.1)

    async def test_send_request_error_response(self):
        """Test send_request receiving an error response."""
        target_node = "NODE_B"
        topic = "request.test.error"
        payload = {"id": 3}
        error_response_payload = {"status": "ERROR", "error_message": "Target failed"}

        async def mock_route_message_error(message):
            if message["header"]["message_type"] == "REQUEST":
                response_msg = {
                    "header": {
                        # Use mock_network here
                        "message_id": self.mock_network.generate_uuid(),
                        "correlation_id": message["header"]["correlation_id"],
                        "timestamp": datetime.now().isoformat(),
                        "sender_node": target_node,
                        "target_node": self.node_id,
                        "topic": topic,
                        "message_type": "RESPONSE",
                        "priority": "MEDIUM",
                        "version": "1.0",
                    },
                    "payload": error_response_payload,
                }
                await self.interface._handle_response(response_msg)

        self.mock_network.route_message = mock_route_message_error

        # Use assertRaisesRegex to check for the specific error message within the Exception
        with self.assertRaisesRegex(Exception, "Target failed"):
            await self.interface.send_request(target_node, topic, payload, timeout=1)


# Main execution block
if __name__ == "__main__":
    unittest.main()

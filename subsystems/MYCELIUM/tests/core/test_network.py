# subsystems/MYCELIUM/tests/core/test_network.py

import asyncio
from datetime import datetime
from typing import Any, Dict
import unittest

from subsystems.MYCELIUM.core.network import MyceliumNetwork
from subsystems.MYCELIUM.core.node import MyceliumNode


class TestMyceliumNetwork(unittest.TestCase):
    def setUp(self):
        """Set up a new MyceliumNetwork instance for each test."""
        self.network = MyceliumNetwork()

    def test_network_initialization(self):
        """Test if the network initializes correctly."""
        self.assertIsInstance(self.network, MyceliumNetwork)
        self.assertEqual(len(self.network.nodes), 0)
        self.assertEqual(len(self.network.connections), 0)
        self.assertEqual(len(self.network.subscriptions), 0)
        self.assertEqual(self.network.message_queue.qsize(), 0)
        self.assertIsNone(self.network._message_processor_task)

    def test_node_registration(self):
        """Test registering a single node."""
        node_id = "NODE_A"
        node_type = "TEST_TYPE"
        version = "1.0"
        capabilities = ["test_cap"]

        registered = self.network.register_node(node_id, node_type, version, capabilities)
        self.assertTrue(registered)
        self.assertIn(node_id, self.network.nodes)
        self.assertIsInstance(self.network.nodes[node_id], MyceliumNode)
        self.assertEqual(self.network.nodes[node_id].node_id, node_id)
        self.assertEqual(self.network.nodes[node_id].node_type, node_type)
        self.assertEqual(self.network.nodes[node_id].version, version)
        self.assertEqual(self.network.nodes[node_id].capabilities, capabilities)
        self.assertEqual(self.network.nodes[node_id].status, "active")

    def test_register_duplicate_node(self):
        """Test registering the same node ID twice (should update)."""
        node_id = "NODE_A"
        self.network.register_node(node_id, "TYPE_1", "1.0", ["cap1"])
        self.assertEqual(len(self.network.nodes), 1)
        self.assertEqual(self.network.nodes[node_id].node_type, "TYPE_1")

        # Register again with different info
        registered = self.network.register_node(node_id, "TYPE_2", "2.0", ["cap2"])
        self.assertTrue(registered)
        self.assertEqual(len(self.network.nodes), 1)  # Should still be 1 node
        self.assertEqual(self.network.nodes[node_id].node_type, "TYPE_2")  # Type updated
        self.assertEqual(self.network.nodes[node_id].version, "2.0")
        self.assertEqual(self.network.nodes[node_id].capabilities, ["cap2"])

    def test_node_removal(self):
        """Test removing a registered node."""
        node_id = "NODE_A"
        self.network.register_node(node_id, "TEST", "1.0", [])
        self.assertIn(node_id, self.network.nodes)

        removed = self.network.remove_node(node_id)
        self.assertTrue(removed)
        self.assertNotIn(node_id, self.network.nodes)
        self.assertEqual(len(self.network.nodes), 0)

    def test_remove_nonexistent_node(self):
        """Test removing a node that doesn't exist."""
        removed = self.network.remove_node("NONEXISTENT")
        self.assertFalse(removed)

    def test_add_connection(self):
        """Test adding a connection between two registered nodes."""
        node_a = "NODE_A"
        node_b = "NODE_B"
        self.network.register_node(node_a, "T", "1", [])
        self.network.register_node(node_b, "T", "1", [])

        self.network.add_connection(node_a, node_b)

        self.assertIn(node_b, self.network.connections[node_a])
        self.assertIn(node_a, self.network.connections[node_b])

    def test_add_connection_nonexistent_node(self):
        """Test adding a connection when one node doesn't exist."""
        node_a = "NODE_A"
        self.network.register_node(node_a, "T", "1", [])
        # NODE_C is not registered
        self.network.add_connection(node_a, "NODE_C")
        self.assertNotIn("NODE_C", self.network.connections[node_a])
        self.assertNotIn(node_a, self.network.connections.get("NODE_C", set()))

    def test_remove_connection(self):
        """Test removing an existing connection."""
        node_a = "NODE_A"
        node_b = "NODE_B"
        self.network.register_node(node_a, "T", "1", [])
        self.network.register_node(node_b, "T", "1", [])
        self.network.add_connection(node_a, node_b)
        self.assertIn(node_b, self.network.connections[node_a])

        self.network.remove_connection(node_a, node_b)

        self.assertNotIn(node_b, self.network.connections.get(node_a, set()))
        self.assertNotIn(node_a, self.network.connections.get(node_b, set()))

    def test_remove_node_removes_connections(self):
        """Test that removing a node also removes its connections."""
        node_a = "NODE_A"
        node_b = "NODE_B"
        node_c = "NODE_C"
        self.network.register_node(node_a, "T", "1", [])
        self.network.register_node(node_b, "T", "1", [])
        self.network.register_node(node_c, "T", "1", [])
        self.network.add_connection(node_a, node_b)
        self.network.add_connection(node_a, node_c)

        self.assertIn(node_a, self.network.connections[node_b])
        self.assertIn(node_a, self.network.connections[node_c])
        self.assertEqual(len(self.network.connections[node_a]), 2)

        # Remove Node A
        removed = self.network.remove_node(node_a)
        self.assertTrue(removed)

        # Check connections are gone
        self.assertNotIn(node_a, self.network.connections.get(node_b, set()))
        self.assertNotIn(node_a, self.network.connections.get(node_c, set()))
        self.assertNotIn(node_a, self.network.connections)  # Entry for node_a itself is gone


# Add a new class for asynchronous tests
class TestMyceliumNetworkAsync(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        """Set up a new MyceliumNetwork instance for each async test."""
        self.network = MyceliumNetwork()
        # Register nodes used in multiple tests
        self.node_a_id = "NODE_A"
        self.node_b_id = "NODE_B"
        self.network.register_node(self.node_a_id, "TYPE_ASYNC", "1.0", [])
        self.network.register_node(self.node_b_id, "TYPE_ASYNC", "1.0", [])
        self.callback_received_message = None  # Variable to store received message in callbacks
        self.response_futures = {}  # Store response futures for tests

    async def asyncSetUp(self):
        """Start the network processor and register response handlers."""

        # Register a generic response handler for Node A for tests that need it
        async def generic_node_a_handler(message):
            correlation_id = message["header"]["correlation_id"]
            if correlation_id in self.response_futures:
                future = self.response_futures.pop(correlation_id)
                if not future.done():
                    future.set_result(message["payload"])

        # Use the network's method to register the handler
        await self.network.register_response_handler(self.node_a_id, generic_node_a_handler)
        await self.network.start()

    async def asyncTearDown(self):
        """Stop the network processor and clean up handlers/futures."""
        # Use the network's method to remove the handler
        await self.network.remove_response_handler(self.node_a_id)
        await self.network.stop()
        # Cancel any remaining futures
        for future in self.response_futures.values():
            if not future.done():
                future.cancel("Test teardown")
        self.response_futures.clear()
        await asyncio.sleep(0.01)

    async def test_start_stop_processor(self):
        """Test starting and stopping the message processor task."""
        self.assertIsNotNone(self.network._message_processor_task)
        self.assertFalse(self.network._message_processor_task.done())

        task = self.network._message_processor_task  # Get task reference before stopping

        await self.asyncTearDown()  # This calls network.stop()

        # Assert the task itself is done/cancelled and the network attribute is None
        self.assertTrue(task.done() or task.cancelled())
        self.assertIsNone(self.network._message_processor_task)

    async def test_send_request_receive_response(self):
        """Test sending a request and receiving a response via the queue."""
        topic = "request.test.echo"
        correlation_id = self.network.generate_uuid()  # Generate unique ID

        # Mock Node B's process_message
        async def mock_process_message(message):
            self.assertEqual(message["header"]["topic"], topic)
            self.assertEqual(message["header"]["target_node"], self.node_b_id)
            return {"status": "SUCCESS", "data": f"Echo: {message['payload']['value']}"}

        self.network.nodes[self.node_b_id].process_message = mock_process_message

        # Prepare future for response handler in asyncSetUp
        response_future = asyncio.Future()
        self.response_futures[correlation_id] = response_future  # Store future for the handler

        # Prepare and send request message
        request_message = {
            "header": {
                "message_id": self.network.generate_uuid(),
                "correlation_id": correlation_id,  # Use generated ID
                "timestamp": datetime.now().isoformat(),
                "sender_node": self.node_a_id,
                "target_node": self.node_b_id,
                "topic": topic,
                "message_type": "REQUEST",
                "priority": "MEDIUM",
                "version": "1.0",
            },
            "payload": {"value": "Hello B"},
        }
        await self.network.route_message(request_message)

        # Wait for the response future
        try:
            response_payload = await asyncio.wait_for(response_future, timeout=1.0)
            self.assertEqual(response_payload["status"], "SUCCESS")
            self.assertEqual(response_payload["data"], "Echo: Hello B")
        except asyncio.TimeoutError:
            self.fail("Timeout waiting for response")

    async def test_publish_event_receive_by_subscriber(self):
        """Test publishing an event and having a subscriber receive it."""
        topic = "event.test.notify"
        event_payload = {"value": "Notification!"}

        async def node_b_callback(message: Dict[str, Any]):
            self.callback_received_message = message

        await self.network.add_subscription(topic, self.node_b_id, node_b_callback)
        self.assertIn((self.node_b_id, node_b_callback), self.network.subscriptions[topic])

        # Prepare and publish event message from Node A
        event_message = {
            "header": {
                "message_id": self.network.generate_uuid(),
                "correlation_id": None,
                "timestamp": datetime.now().isoformat(),
                "sender_node": self.node_a_id,
                "target_node": "TOPIC_TARGET",
                "topic": topic,
                "message_type": "EVENT",
                "priority": "MEDIUM",
                "version": "1.0",
            },
            "payload": event_payload,
        }
        await self.network.route_message(event_message)

        # Wait briefly for the event to be processed by the background task
        await asyncio.sleep(0.1)

        # Check if the callback was invoked and received the correct message
        self.assertIsNotNone(self.callback_received_message)
        self.assertEqual(self.callback_received_message["header"]["topic"], topic)
        self.assertEqual(self.callback_received_message["payload"], event_payload)
        self.assertEqual(self.callback_received_message["header"]["sender_node"], self.node_a_id)

    async def test_request_to_nonexistent_node(self):
        """Test sending a request to a node that is not registered."""
        node_c_id = "NODE_C"  # Non-existent node
        topic = "request.test.fail"
        correlation_id = self.network.generate_uuid()

        # Prepare future for response handler in asyncSetUp
        response_future = asyncio.Future()
        self.response_futures[correlation_id] = response_future

        # Prepare and send request message
        request_message = {
            "header": {
                "message_id": self.network.generate_uuid(),
                "correlation_id": correlation_id,
                "timestamp": datetime.now().isoformat(),
                "sender_node": self.node_a_id,
                "target_node": node_c_id,
                "topic": topic,
                "message_type": "REQUEST",
                "priority": "MEDIUM",
                "version": "1.0",
            },
            "payload": {"value": "This should fail"},
        }
        await self.network.route_message(request_message)

        # Wait for the error response
        try:
            response_payload = await asyncio.wait_for(response_future, timeout=1.0)
            self.assertEqual(response_payload["status"], "ERROR")
            self.assertIn(f"Target node '{node_c_id}' not found", response_payload["error_message"])
        except asyncio.TimeoutError:
            self.fail("Timeout waiting for error response")

    async def test_remove_node_removes_subscriptions(self):
        """Test that removing a node also removes its subscriptions."""
        topic = "event.test.sub_removal"

        async def dummy_callback(message):
            pass

        await self.network.add_subscription(topic, self.node_b_id, dummy_callback)
        self.assertTrue(any(sub[0] == self.node_b_id for sub in self.network.subscriptions[topic]))

        # Remove Node B
        removed = self.network.remove_node(self.node_b_id)
        self.assertTrue(removed)

        # Verify subscription is gone
        self.assertFalse(
            any(sub[0] == self.node_b_id for sub in self.network.subscriptions.get(topic, []))
        )
        # Also check if the topic entry itself is removed if it became empty
        if not self.network.subscriptions.get(topic, []):
            self.assertNotIn(topic, self.network.subscriptions)


# Basic test execution (can be run with:
# python -m unittest subsystems/MYCELIUM/tests/core/test_network.py)
if __name__ == "__main__":
    unittest.main()

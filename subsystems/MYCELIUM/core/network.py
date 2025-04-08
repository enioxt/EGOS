# subsystems/MYCELIUM/core/network.py

"""Defines the MyceliumNetwork class, the central orchestrator."""

import asyncio
from collections import defaultdict
from datetime import datetime
import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set
import uuid

from .node import MyceliumNode

logger = logging.getLogger(__name__)


# Define custom exceptions if needed, e.g.:
class MyceliumError(Exception):
    pass


class NodeNotFoundError(MyceliumError):
    pass


class RoutingError(MyceliumError):
    pass


class MyceliumNetwork:
    """Manages the nodes, connections, and message routing for the Mycelium Network."""

    def __init__(self):
        self.nodes: Dict[str, MyceliumNode] = {}
        self.connections: Dict[str, Set[str]] = defaultdict(
            set
        )  # node_id -> set of connected node_ids
        self.subscriptions: Dict[str, List[tuple[str, Callable[[Dict[str, Any]], Coroutine]]]] = (
            defaultdict(list)
        )  # topic -> list of (node_id, async_callback)
        self.response_waiters: Dict[str, asyncio.Future] = {}  # correlation_id -> Future
        self.message_queue = asyncio.Queue()
        self._message_processor_task: Optional[asyncio.Task] = None  # Explicitly type hint task
        self._response_handlers: Dict[
            str, Callable
        ] = {}  # node_id -> _handle_response method from interface
        logger.info("Mycelium Network initialized.")

    def generate_uuid(self) -> str:
        """Generates a unique identifier."""
        return str(uuid.uuid4())

    async def register_node(
        self, node_id: str, node_type: str, version: str, capabilities: List[str]
    ) -> bool:
        """Registers a new node or updates an existing one (async)."""
        if node_id in self.nodes:
            logger.warning(f"Node {node_id} already registered. Updating info.")
            node = self.nodes[node_id]
            node.node_type = node_type
            node.version = version
            node.capabilities = capabilities
            node.update_status("active")
        else:
            node = MyceliumNode(node_id, node_type, version, capabilities)
            self.nodes[node_id] = node
            node.update_status("active")
        logger.info(f"Node registered/updated: {node_id}")
        return True

    async def remove_node(self, node_id: str) -> bool:
        """Removes a node and its connections (async)."""
        if node_id not in self.nodes:
            logger.warning(f"Attempted to remove non-existent node: {node_id}")
            return False

        # Remove connections to this node
        connected_ids = list(self.connections.get(node_id, set()))
        for target_id in connected_ids:
            if target_id in self.connections:
                self.connections[target_id].discard(node_id)

        # Remove node's own connection entry
        self.connections.pop(node_id, None)

        # Remove subscriptions for this node
        for topic in list(self.subscriptions.keys()):
            self.subscriptions[topic] = [
                (sub_id, cb) for sub_id, cb in self.subscriptions[topic] if sub_id != node_id
            ]
            if not self.subscriptions[topic]:  # Clean up empty topic lists
                del self.subscriptions[topic]

        # Remove response handler if it exists
        await self.remove_response_handler(node_id)

        # Remove node itself
        del self.nodes[node_id]
        logger.info(f"Node removed: {node_id}")
        return True

    # --- Response Handler Registration (Called by Interface) --- #
    async def register_response_handler(self, node_id: str, handler: Callable):
        """Registers the function responsible for handling responses for a node."""
        if node_id in self.nodes:
            self._response_handlers[node_id] = handler
            logger.debug(f"Response handler registered for node {node_id}")
        else:
            logger.error(f"Cannot register response handler for non-existent node {node_id}")

    async def remove_response_handler(self, node_id: str):
        """Removes the response handler for a node."""
        removed_handler = self._response_handlers.pop(node_id, None)
        if removed_handler:
            logger.debug(f"Response handler removed for node {node_id}")
        else:
            logger.debug(f"No response handler found to remove for node {node_id}")

    # ----------------------------------------------------------- #

    def add_connection(self, node1_id: str, node2_id: str):
        """Adds a bidirectional connection between two nodes."""
        if node1_id in self.nodes and node2_id in self.nodes:
            self.connections[node1_id].add(node2_id)
            self.connections[node2_id].add(node1_id)
            logger.info(f"Connection added: {node1_id} <-> {node2_id}")
        else:
            logger.error(
                f"Cannot add connection: one or both nodes not found ({node1_id}, {node2_id})"
            )

    def remove_connection(self, node1_id: str, node2_id: str):
        """Removes a bidirectional connection."""
        if node1_id in self.connections:
            self.connections[node1_id].discard(node2_id)
        if node2_id in self.connections:
            self.connections[node2_id].discard(node1_id)
        logger.info(f"Connection removed: {node1_id} <-> {node2_id}")

    async def add_subscription(
        self, topic: str, node_id: str, callback: Callable[[Dict[str, Any]], Coroutine]
    ):
        """Adds a subscription for a node to a topic."""
        if node_id not in self.nodes:
            logger.error(f"Cannot subscribe: Node {node_id} not registered.")
            return
        # Avoid duplicate subscriptions for the same node/callback
        if not any(
            sub_id == node_id and cb == callback for sub_id, cb in self.subscriptions[topic]
        ):
            self.subscriptions[topic].append((node_id, callback))
            logger.info(f"Node {node_id} subscribed to topic: {topic}")
        else:
            logger.warning(
                f"Node {node_id} already subscribed to topic {topic} with this callback."
            )

    async def route_message(self, message: Dict[str, Any]):
        """Puts a message onto the internal queue for processing."""
        await self.message_queue.put(message)

    async def _process_messages(self):
        """Continuously processes messages from the internal queue."""
        while True:
            try:
                message = await self.message_queue.get()
                # Wrap processing in create_task to avoid blocking the loop if one handler hangs
                asyncio.create_task(self._handle_single_message(message))
            except asyncio.CancelledError:
                logger.info("Message processor task cancelled.")
                break  # Exit the loop if cancelled
            except Exception as e:
                logger.error(f"Fatal error in message processing loop: {e}", exc_info=True)
                # Consider more robust error handling or restarting logic here
                await asyncio.sleep(1)  # Avoid tight loop on persistent error

    async def _handle_single_message(self, message: Dict[str, Any]):
        """Handles the routing and processing of a single message."""
        # Outer try-except to catch unexpected errors during handling
        try:
            header = message.get("header", {})  # Use .get for safety
            if not header:
                logger.error(f"Message missing header: {message}")
                return

            msg_type = header.get("message_type")
            target = header.get("target_node")
            topic = header.get("topic")
            sender = header.get("sender_node")
            correlation_id = header.get("correlation_id")
            msg_id = header.get("message_id", "N/A")

            if not all([msg_type, target, topic, sender]):
                logger.error(
                    f"Message header missing required fields "
                    f"(type, target, topic, sender): {header}"
                )
                return

            logger.debug(
                f"Processing message {msg_id} from {sender} to {target} ({topic}) [{msg_type}] "
            )

            # --- RESPONSE Handling --- #
            if msg_type == "RESPONSE":
                if not correlation_id:
                    logger.warning(f"Received RESPONSE without correlation_id: {message}")
                    return
                response_target_node = target
                if response_target_node in self._response_handlers:
                    try:
                        await self._response_handlers[response_target_node](message)
                    except Exception as e:
                        logger.error(
                            f"Error invoking response handler for node {response_target_node}, "
                            f"corr_id {correlation_id}: {e}",
                            exc_info=True,
                        )
                else:
                    logger.warning(
                        f"No response handler registered for node {response_target_node} "
                        f"to handle corr_id {correlation_id}"
                    )

            # --- REQUEST Handling --- #
            elif msg_type == "REQUEST":
                if target not in self.nodes:
                    logger.error(f"Cannot route REQUEST: Target node {target} not found.")
                    error_payload = {
                        "status": "ERROR",
                        "error_message": f"Target node '{target}' not found",
                    }
                    response_msg = self._create_response_message(message, error_payload)
                    if response_msg:
                        await self.route_message(response_msg)
                    return

                node = self.nodes[target]
                try:
                    response_payload = await node.process_message(message)
                    if response_payload is not None:
                        response_msg = self._create_response_message(message, response_payload)
                        if response_msg:
                            await self.route_message(response_msg)
                except Exception as e:
                    logger.error(
                        f"Error processing REQUEST in node {target} for topic {topic}: {e}",
                        exc_info=True,
                    )
                    error_payload = {
                        "status": "ERROR",
                        "error_message": f"Error processing request in {target}: {str(e)}",
                    }
                    response_msg = self._create_response_message(message, error_payload)
                    if response_msg:
                        await self.route_message(response_msg)

            # --- EVENT Handling --- #
            elif msg_type == "EVENT":
                subscribers_to_notify = []
                # Determine target audience based on target_node/topic
                if target == "BROADCAST":
                    subscribers_to_notify = [
                        (nid, node) for nid, node in self.nodes.items() if nid != sender
                    ]
                elif target == "TOPIC_TARGET":
                    subscribers_to_notify = [
                        (sub_id, self.nodes[sub_id])
                        for sub_id, cb in self.subscriptions.get(topic, [])
                        if sub_id in self.nodes
                    ]
                elif target in self.nodes:
                    subscribers_to_notify = [(target, self.nodes[target])]
                else:
                    logger.error(f"Cannot route EVENT: Target node {target} not found.")
                    return

                if not subscribers_to_notify:
                    logger.debug(f"No active subscribers found for event topic: {topic}")

                # Use registered callbacks or default process_message
                active_subscriptions = self.subscriptions.get(topic, [])
                callback_map = {sub_id: cb for sub_id, cb in active_subscriptions}

                for node_id, node_instance in subscribers_to_notify:
                    if node_id != sender:
                        try:
                            # Prioritize specific registered callback,
                            # fallback to node's process_message
                            handler_coro = callback_map.get(node_id, node_instance.process_message)
                            # Ensure we only schedule if the handler is valid
                            if asyncio.iscoroutinefunction(handler_coro) or isinstance(
                                handler_coro, Coroutine
                            ):
                                asyncio.create_task(
                                    handler_coro(message), name=f"event_callback_{node_id}_{topic}"
                                )
                            else:
                                logger.error(
                                    f"Invalid handler for event callback node {node_id} "
                                    f"on topic {topic}: {type(handler_coro)}"
                                )
                        except Exception as e:
                            logger.error(
                                f"Error scheduling/executing EVENT callback for node {node_id} "
                                f"on topic {topic}: {e}",
                                exc_info=True,
                            )
            else:
                logger.warning(f"Unsupported message type received: {msg_type}")

        # Catch all unexpected errors during handling of this specific message
        except Exception as e:
            msg_id_for_log = message.get("header", {}).get("message_id", "N/A")
            logger.error(f"Critical error handling message {msg_id_for_log}: {e}", exc_info=True)
        finally:
            pass  # task_done() is not used when using create_task per message

    def _create_response_message(
        self, request_message: Dict[str, Any], response_payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Helper to construct a RESPONSE message."""
        # Add more robust checking for request_message structure
        header = request_message.get("header")
        if not isinstance(header, dict) or not all(
            k in header for k in ["correlation_id", "target_node", "sender_node", "topic"]
        ):
            logger.error(f"Cannot create response, invalid request message header: {header}")
            return None

        return {
            "header": {
                "message_id": self.generate_uuid(),
                "correlation_id": request_message["header"]["correlation_id"],
                "timestamp": datetime.now().isoformat(),
                "sender_node": request_message["header"][
                    "target_node"
                ],  # Response comes from original target
                "target_node": request_message["header"][
                    "sender_node"
                ],  # Send back to original sender
                "topic": request_message["header"]["topic"],
                "message_type": "RESPONSE",
                "priority": request_message.get("header", {}).get("priority", "MEDIUM"),
                "version": "1.0",
            },
            "payload": response_payload,
        }

    async def start(self):
        """Starts the background message processing task."""
        if self._message_processor_task is None or self._message_processor_task.done():
            self._message_processor_task = asyncio.create_task(
                self._process_messages(), name="mycelium_message_processor"
            )
            logger.info("Mycelium Network message processor started.")
        else:
            logger.warning("Mycelium Network message processor already running.")

    async def stop(self):
        """Stops the background message processing task gracefully."""
        if self._message_processor_task and not self._message_processor_task.done():
            self._message_processor_task.cancel()
            try:
                await self._message_processor_task
            except asyncio.CancelledError:
                logger.info("Mycelium Network message processor stopped.")
            self._message_processor_task = None
        else:
            logger.info("Mycelium Network message processor already stopped.")

    def get_network_status(self) -> Dict[str, Any]:
        """Returns the current status of the network."""
        node_statuses = {nid: node.get_status() for nid, node in self.nodes.items()}
        connection_counts = {nid: len(conns) for nid, conns in self.connections.items()}

        # Calculate total connections accurately (avoid double counting)
        total_connections = sum(connection_counts.values()) // 2

        return {
            "total_nodes": len(self.nodes),
            "total_connections": total_connections,  # Added accurate count
            "connections_per_node": connection_counts,  # Added detail
            "nodes": node_statuses,  # Added node details
            "subscriptions": {
                topic: [sub[0] for sub in subs] for topic, subs in self.subscriptions.items()
            },
            "queue_size": self.message_queue.qsize(),
            "processor_running": self._message_processor_task is not None
            and not self._message_processor_task.done(),
        }


# Global instance (optional, could be managed by BIOS-Q)
# mycelium_network = MyceliumNetwork()

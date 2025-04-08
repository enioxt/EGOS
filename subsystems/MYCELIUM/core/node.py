# subsystems/MYCELIUM/core/node.py

"""Defines the MyceliumNode class representing a component in the network."""

from datetime import datetime
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class MyceliumNode:
    """Represents a single node (subsystem or component) in the Mycelium Network."""

    def __init__(
        self, node_id: str, node_type: str, version: str = "N/A", capabilities: list = None
    ):
        self.node_id: str = node_id
        self.node_type: str = node_type
        self.version: str = version
        self.capabilities: list = capabilities or []
        # Connections will be managed by the MyceliumNetwork class
        self.data: Dict[str, Any] = {}  # Optional local data cache
        self.last_update: datetime = datetime.now()
        self.status: str = "initializing"  # e.g., initializing, active, degraded, inactive
        self.health_details: Optional[Dict[str, Any]] = None

        logger.info(f"Node created: {self.node_id} ({self.node_type} v{self.version})")

    async def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handles an incoming message routed by the network.

        This method should be implemented by specific node types or subsystems
        to handle requests, events, etc.

        Returns:
            Optional response payload if the message was a request requiring a response.
        """
        msg_type = message.get("header", {}).get("message_type", "UNKNOWN")
        topic = message.get("header", {}).get("topic", "N/A")
        logger.debug(f"Node {self.node_id} received message: Topic={topic}, Type={msg_type}")

        # Placeholder: Subclasses or specific node handlers would implement logic here
        if msg_type == "REQUEST":
            # Example: Echo back the payload for testing
            logger.info(f"Node {self.node_id} echoing REQUEST on topic {topic}")
            return {"status": "SUCCESS", "echo": message.get("payload")}
        elif msg_type == "EVENT":
            # Base node might just log events it receives
            logger.info(f"Node {self.node_id} received EVENT on topic {topic}")
            return None  # No response needed for events
        # Add handling for QUERY if defined
        # elif msg_type == "QUERY":
        #     pass
        else:
            logger.warning(
                f"Node {self.node_id} received unhandled message type '{msg_type}' on topic {topic}"
            )
            return None

    def update_status(self, status: str, details: Optional[Dict[str, Any]] = None):
        """Updates the node's status and health details."""
        self.status = status
        self.health_details = details
        self.last_update = datetime.now()
        logger.info(f"Node {self.node_id} status updated: {status}")

    def get_status(self) -> Dict[str, Any]:
        """Returns the current status and metadata of the node."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "version": self.version,
            "status": self.status,
            "capabilities": self.capabilities,
            "last_update": self.last_update.isoformat(),
            "health_details": self.health_details,
        }

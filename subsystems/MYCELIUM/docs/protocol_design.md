# Mycelium Network - Protocol Design

**Version:** 0.7 # Updated version
**Last Updated:** 2025-04-02

## 1. Overview

This document outlines the design for the Mycelium Network communication protocol, the central nervous system of EGOS. It incorporates insights from multiple sources: the existing implementation within the SLOP server (`slop_server.js.backup`), a Python network implementation (`mycelium_network.py`), a static analysis tool (`quantum_mycelium.py`), and an external health check script (`check_mycelium_health.ps1`) found in backups. **This design specifies an initial implementation using Python's `asyncio` for message routing.** **Future enhancements inspired by biological mycelium principles are noted in relevant sections.**

## 2. Core Concepts

-   **Nodes:** Individual subsystems or components registered with the network.
-   **Files:** Specific files registered with the network. (Primarily via SLOP API currently).
-   **Connections:** Relationships between Nodes or Files.
-   **Messages:** Standardized units of information (structure below).
-   **Topics/Channels:** Logical pathways for specific types of communication. **Naming Convention:** `category.origin_subsystem.action_or_entity` (e.g., `event.cronos.backup_completed`, `request.nexus.analyze_module`). Used for pub/sub and potentially routing.
-   **Router/Broker:** **Initial Implementation:** Implicit routing managed by the central `MyceliumNetwork` class using `asyncio`. *(Future Enhancement: Explore decentralized routing algorithms inspired by biological network resilience and scalability)*.
-   **Health & Sync:** Target: Integrated health monitoring via network messages. Sync logic to be robust within CRONOS/Mycelium.
-   **Master State:** Centralized `master_state.json` concept is deprecated in favor of dynamic status reporting via the network.
-   **Static Analysis Integration:** `quantum_mycelium.py` output to bootstrap/validate connections.

## 3. Message Format (Standard Protocol)

```json
{
  "header": {
    "message_id": "uuid",
    "correlation_id": "uuid", // For request/response
    "timestamp": "iso8601",
    "sender_node": "SUBSYSTEM_NAME",
    "target_node": "SUBSYSTEM_NAME | BROADCAST | TOPIC_TARGET", // Target node or topic
    "topic": "category.origin_subsystem.action_or_entity", // Defines message content/purpose
    "message_type": "REQUEST | RESPONSE | EVENT | QUERY",
    "priority": "HIGH | MEDIUM | LOW", // For potential queuing
    "version": "1.0"
  },
  "payload": {
    // Subsystem-specific data
    "status": "SUCCESS | ERROR", // For RESPONSE messages
    "error_message": "Details if status is ERROR" // For RESPONSE messages
  }
}
```

## 4. Existing Communication & Logic

-   **SLOP Server REST API:** `POST /mycelium/connect`, `POST /mycelium/register-file`, `GET /mycelium/status`.
-   **SLOP Server Internal Logic:** In-memory Maps, periodic file sync, basic health calc.
-   **Python Network Implementation (`mycelium_network.py` Backup):** Classes, node/connection mgmt, async `propagate_update`, pre-defined connections.
-   **Python Static Analysis (`quantum_mycelium.py` Backup):** Scans project, finds references, detects duplicates/orphans.
-   **Health Check Script (`check_mycelium_health.ps1` Backup):** External periodic check (simulated), updates deprecated `master_state.json`.

## 5. Communication Patterns (Target State - Asyncio Implementation)

-   **Request/Response:**
    1.  Requester sends a message to a specific topic pattern like `request.<target_subsystem>.<action>` (e.g., `request.ethik.validate_text`).
    2.  The target subsystem listens on this topic.
    3.  The target responds on a unique reply topic (potentially included in the request message or derived algorithmically).
-   **Publish/Subscribe:**
    1.  Publisher sends a message to a topic like `event.<source_subsystem>.<event_name>` (e.g., `event.cronos.backup_started`).
    2.  Any interested subscriber listens on that topic or a pattern (e.g., `event.cronos.*`).
-   **Event Broadcasting:** Specific case of pub/sub using a general topic or `target_node` = `BROADCAST`.
-   **Queries:** Similar to Request/Response, but potentially targeting a topic (`target_node` = `TOPIC_TARGET`) where multiple nodes might respond.
*(Future Enhancement: Investigate faster, potentially direct communication channels inspired by mycelial electrical signaling for specific high-priority or low-latency use cases.)*

## 6. Node/File Discovery and Registration

-   **Target:** Standardized registration via `MyceliumInterface.connect()` and `register_file()`. Auto-discovery via static analysis is a future goal.
*(Future Enhancement: Implement dynamic connection adjustments based on network load, node health, or message priority, mimicking adaptive biological growth.)*

## 7. State Synchronization

-   **Target:** To be handled by CRONOS, potentially triggered or coordinated via Mycelium messages (`event.subsystem.state_changed`, `request.cronos.sync_state`).

## 8. Resource Sharing

-   Resource sharing will primarily be implemented using the **Request/Response** pattern.
-   Nodes needing a resource managed by another node will send a `REQUEST` message using a specific topic indicating the desired resource (e.g., `request.bios-q.get_config_value`, `request.ethik.get_validation_rule`).
-   The node owning the resource will process the request and return the resource data (or an error) in a `RESPONSE` message payload.
-   This avoids complex shared memory or direct access, relying on the standard message bus.
*(Future Enhancement: Explore more nuanced information/resource sharing based on node relationships or contextual needs, inspired by mycorrhizal network interactions.)*

## 9. Error Handling

-   **Target:**
    *   `RESPONSE` messages should include `status` and `error_message` in payload.
    *   `send_request` interface should handle timeouts.
    *   Network should log routing/delivery errors.
    *   Define standard error topics (e.g., `error.mycelium.delivery_failed`).
*(Future Enhancement: Implement advanced fault tolerance mechanisms like redundant pathways or automated node isolation based on health status.)*

## 10. Security Considerations

-   **Authentication/Authorization:**
    *   **Initial Target (Internal Asyncio):** Focus on ensuring only registered/authenticated nodes (subsystems started within the EGOS environment) can connect and send messages. Basic validation of message sources based on node identity established during connection.
    *   **Future (External/Distributed):** Implement stronger authentication (e.g., tokens, certificates) if Mycelium needs to bridge processes or machines. Authorization might involve topic-level ACLs.
-   **Encryption:** Use TLS/SSL for connections if Mycelium operates over insecure networks.
-   **Input Validation:** Subsystems receiving messages **MUST** rigorously validate the payload content according to their schemas, regardless of the source. Trust but verify.

## 11. API/Interface for Subsystems (Target State)

*(Refined conceptual Python `MyceliumInterface` class based on asyncio patterns)*

```python
import asyncio
from typing import Dict, Any, Callable, List, Optional

# Assuming MyceliumNetwork class exists and handles routing/subscriptions
# class MyceliumNetwork:
#    async def route_message(self, message: Dict[str, Any]): ...
#    def register_node(self, node_id: str, node_type: str, ...): ...
#    def remove_node(self, node_id: str): ...
#    def add_subscription(self, topic: str, node_id: str, callback: Callable): ...
#    # etc.

class MyceliumInterface:
    """Conceptual interface for subsystems to interact with the Mycelium Network (Asyncio implementation)."""

    def __init__(self, network_instance: 'MyceliumNetwork', node_id: str):
        self._network = network_instance
        self._node_id = node_id
        self._response_futures: Dict[str, asyncio.Future] = {}

    async def connect(self, node_type: str, version: str, capabilities: List[str]) -> bool:
        """Registers the subsystem node with the network."""
        # Called by the subsystem during its initialization
        return self._network.register_node(self._node_id, node_type, version, capabilities)

    async def disconnect(self) -> bool:
        """Deregisters the subsystem node."""
        # Called during subsystem shutdown
        # Cancel any pending response futures
        for future in self._response_futures.values():
            if not future.done():
                future.set_exception(ConnectionAbortedError("Node disconnecting"))
        return self._network.remove_node(self._node_id)

    async def send_request(self, target_node: str, topic: str, payload: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
        """Sends a request and waits for a response.

        Args:
            target_node: The ID of the target node.
            topic: The specific request topic (e.g., 'request.nexus.analyze_module').
            payload: The data for the request.
            timeout: Maximum seconds to wait for a response.

        Returns:
            The payload of the response message.

        Raises:
            TimeoutError: If no response is received within the timeout.
            Exception: If the response payload indicates an error status.
        """
        correlation_id = self._network.generate_uuid() # Network should provide UUID generation
        future = asyncio.Future()
        self._response_futures[correlation_id] = future

        message = {
            "header": {
                "message_id": self._network.generate_uuid(),
                "correlation_id": correlation_id,
                "timestamp": datetime.now().isoformat(),
                "sender_node": self._node_id,
                "target_node": target_node,
                "topic": topic,
                "message_type": "REQUEST",
                "priority": "MEDIUM",
                "version": "1.0"
            },
            "payload": payload
        }

        await self._network.route_message(message) # Network handles routing via asyncio

        try:
            response_payload = await asyncio.wait_for(future, timeout=timeout)
            if response_payload.get("status") == "ERROR":
                 raise Exception(response_payload.get("error_message", "Unknown error in response"))
            return response_payload
        finally:
            # Clean up future
            del self._response_futures[correlation_id]

    async def _handle_response(self, message: Dict[str, Any]):
        """Internal method called by the network to resolve a response future."""
        correlation_id = message["header"]["correlation_id"]
        if correlation_id in self._response_futures:
            future = self._response_futures[correlation_id]
            if not future.done():
                future.set_result(message["payload"])

    async def publish_event(self, topic: str, payload: Dict[str, Any]):
        """Publishes an event to a topic."""
        message = {
             "header": {
                "message_id": self._network.generate_uuid(),
                "correlation_id": None,
                "timestamp": datetime.now().isoformat(),
                "sender_node": self._node_id,
                "target_node": "TOPIC_TARGET", # Indicate topic-based routing
                "topic": topic,
                "message_type": "EVENT",
                "priority": "MEDIUM",
                "version": "1.0"
            },
            "payload": payload
        }
        await self._network.route_message(message) # Network distributes to subscribers

    async def subscribe(self, topic: str, callback_function: Callable[[Dict[str, Any]], Coroutine]):
        """Subscribes to a topic, providing an async callback function.
        The callback will receive the full message dictionary.
        """
        # Network stores subscription: topic -> list[(node_id, callback)]
        await self._network.add_subscription(topic, self._node_id, callback_function)

    async def report_health(self, status: str, details: Optional[Dict[str, Any]] = None):
        """Reports the node's health status to the network."""
        payload = {"node_id": self._node_id, "status": status, "details": details or {}}
        await self.publish_event(topic='event.mycelium.health_report', payload=payload)

    # TODO: Add methods for register_file, get_network_status, get_node_status if needed
    # These might be better suited for a dedicated admin/KOIOS interface

## 12. Migration/Refactoring Plan

**Decision:** Implement core logic in Python within `subsystems/MYCELIUM/`, using `asyncio` initially.

**Approach:**

1.  **Finalize Protocol Design:** Complete placeholders in this document.
2.  **Phased Python Implementation (`subsystems/MYCELIUM/core/`):
    *   **Phase 1 (Core):** Implement `MyceliumNetwork` class, `MyceliumNode`, basic `asyncio` routing (queues/callbacks), registration, connection management.
    *   **Phase 2 (API/Interface):** Implement the Python `MyceliumInterface`.
    *   **Phase 3 (Features):** Implement integrated health monitoring, robust state synchronization (likely via CRONOS), advanced topic management.
3.  **Static Analysis Integration:** Develop process (KOIOS/NEXUS) using `quantum_mycelium.py`.
4.  **Subsystem Integration:** Connect subsystems via `MyceliumInterface`.
5.  **Decommissioning:** Deprecate SLOP Mycelium endpoints and external scripts.

## 13. Future Directions (Bio-Inspired Enhancements) # Added Section

While the current focus is on implementing a robust `asyncio`-based network, the research into biological mycelium offers inspiration for future evolution:

-   **Decentralized Routing:** Investigating peer-to-peer or gossip-based routing could improve scalability and eliminate single points of failure inherent in the initial centralized approach.
-   **Dynamic Pathway Optimization:** Implementing mechanisms for the network to learn and reinforce efficient communication pathways based on usage patterns, similar to biological reinforcement.
-   **Adaptive Connections:** Allowing nodes to dynamically form or prune connections based on needs or environmental factors (e.g., system load).
-   **Advanced Resource/Info Sharing:** Moving beyond simple Request/Response for resources towards more context-aware sharing models.
-   **Specialized Communication Channels:** Exploring dedicated, potentially faster channels for critical system messages, inspired by electrical signaling.
-   **Enhanced Fault Tolerance:** Implementing self-healing capabilities, perhaps through redundant connections or automatic rerouting around failed nodes.

These directions represent potential future research and development efforts after the core Mycelium network is stable and integrated.

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧

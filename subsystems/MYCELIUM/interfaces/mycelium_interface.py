from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, List, Optional, Coroutine
import asyncio

class MyceliumInterface(ABC):
    """Abstract Base Class defining the interface for subsystems to interact with the Mycelium Network."""

    @abstractmethod
    async def connect(self, node_type: str, version: str, capabilities: List[str]) -> bool:
        """Registers the subsystem node with the network."""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Deregisters the subsystem node."""
        pass

    @abstractmethod
    async def send_request(self, target_node: str, topic: str, payload: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
        """Sends a request and waits for a response."""
        pass

    @abstractmethod
    async def publish_event(self, topic: str, payload: Dict[str, Any]):
        """Publishes an event to a topic."""
        pass

    @abstractmethod
    async def subscribe(self, topic: str, callback_function: Callable[[Dict[str, Any]], Coroutine]):
        """Subscribes to a topic, providing an async callback function."""
        pass

    @abstractmethod
    async def report_health(self, status: str, details: Optional[Dict[str, Any]] = None):
        """Reports the node's health status to the network."""
        pass

    # Potentially add internal methods needed by concrete implementations
    # or methods called *by* the network (like _handle_response),
    # although those might live in the concrete class or network core.
    # @abstractmethod
    # async def _handle_response(self, message: Dict[str, Any]):
    #     pass

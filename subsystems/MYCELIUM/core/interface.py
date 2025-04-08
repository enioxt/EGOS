# subsystems/MYCELIUM/core/interface.py

"""Defines the MyceliumInterface class for subsystems to interact with the network."""

import abc
import logging
from typing import Any, Callable, Coroutine, Dict

# Forward declaration for type hinting
# from .network import MyceliumNetwork

logger = logging.getLogger(__name__)


class MyceliumInterface(abc.ABC):
    """Defines the standard interface for interacting with the Mycelium Network."""

    @abc.abstractmethod
    async def connect(self, servers: list[str], **kwargs) -> None:
        """Connect to the Mycelium messaging system.

        Args:
            servers: List of server URLs to connect to.
            **kwargs: Additional implementation-specific connection options.

        Raises:
            ConnectionError: If connection fails.
        """
        pass

    @abc.abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the Mycelium messaging system gracefully."""
        pass

    @abc.abstractmethod
    async def publish(self, subject: str, payload: Dict[str, Any], **kwargs) -> None:
        """Publish a message dictionary to a given subject (topic).

        Args:
            subject: The subject (topic) to publish to.
            payload: The message payload dictionary.
            **kwargs: Implementation-specific publishing options.
        """
        pass

    @abc.abstractmethod
    async def subscribe(
        self,
        subject: str,
        callback: Callable[[Dict[str, Any]], Coroutine[Any, Any, None]],
        **kwargs,
    ) -> Any:
        """Subscribe to a subject (topic) and register an async callback.

        The callback will receive the core payload dictionary.

        Args:
            subject: The subject (topic) to subscribe to (can include wildcards).
            callback: An async function to call when a message is received.
                      The callback should accept the core payload dictionary as an argument.
            **kwargs: Implementation-specific subscription options.

        Returns:
            A subscription identifier that can be used to unsubscribe.
        """
        pass

    @abc.abstractmethod
    async def unsubscribe(self, subscription_id: Any) -> None:
        """Unsubscribe from a previously established subscription.

        Args:
            subscription_id: The identifier returned by the subscribe method.
        """
        pass

    @abc.abstractmethod
    async def request(
        self, subject: str, payload: Dict[str, Any], timeout: float = 1.0, **kwargs
    ) -> Dict[str, Any]:
        """Send a request dictionary and wait for a single dictionary reply.

        Args:
            subject: The subject to send the request to.
            payload: The request payload dictionary.
            timeout: Maximum time in seconds to wait for a reply.
            **kwargs: Implementation-specific request options.

        Returns:
            The response payload dictionary.

        Raises:
            TimeoutError: If no response is received within the timeout period.
            # Specific implementation might raise other errors (e.g., NoRespondersError)
        """
        pass

"""NATS implementation of the MyceliumInterface."""

from datetime import datetime, timezone
import json
import logging
from typing import Any, Callable, Coroutine, Dict, Optional
import uuid

import nats
from nats.aio.msg import Msg
from nats.errors import ConnectionClosedError, NoServersError, TimeoutError

from subsystems.MYCELIUM.core.interface import MyceliumInterface

# Placeholder logger until KoiosLogger is integrated
logger = logging.getLogger(__name__)


class NatsMyceliumInterface(MyceliumInterface):
    """Provides interaction with the Mycelium Network using NATS."""

    def __init__(self, source_subsystem: str):
        """Initialize the interface.

        Args:
            source_subsystem: The name of the subsystem this instance represents.
                              Used for the 'source_subsystem' field in messages.
        """
        self._nc: Optional[nats.NATS] = None
        self._subscriptions: Dict[str, Any] = {}
        self._source_subsystem = source_subsystem  # Store the subsystem name
        logger.info(f"NatsMyceliumInterface initialized for {self._source_subsystem}.")

    def _wrap_payload(self, payload: Dict[str, Any], correlation_id: Optional[str] = None) -> bytes:
        """Wraps the user payload dictionary in the standard message envelope and serializes to JSON bytes."""
        message = {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_subsystem": self._source_subsystem,
            "correlation_id": correlation_id,
            "payload": payload,
            "metadata": {},
        }
        try:
            return json.dumps(message, ensure_ascii=False).encode("utf-8")
        except TypeError as e:
            logger.error(f"Payload serialization error: {e}. Payload: {payload}", exc_info=True)
            raise ValueError(f"Cannot serialize payload to JSON: {e}") from e

    def _unwrap_payload(self, raw_payload: bytes) -> Dict[str, Any]:
        """Deserializes the JSON bytes envelope and returns the core user payload dictionary."""
        try:
            envelope = json.loads(raw_payload.decode("utf-8"))
            # TODO: Add validation against a schema if needed
            if isinstance(envelope, dict) and "payload" in envelope:
                return envelope  # Return the whole envelope for now, callback decides what to use
            else:
                logger.error(f"Invalid message structure received: {envelope}")
                raise ValueError("Received message missing 'payload' field or is not a dictionary.")
        except json.JSONDecodeError as e:
            logger.error(
                f"Payload deserialization error: {e}. Raw data: {raw_payload[:200]}...",
                exc_info=True,
            )
            raise ValueError("Cannot deserialize received message from JSON") from e
        except UnicodeDecodeError as e:
            logger.error(
                f"Payload decoding error: {e}. Raw data: {raw_payload[:200]}...", exc_info=True
            )
            raise ValueError("Cannot decode received message as UTF-8") from e

    async def connect(self, servers: list[str], **kwargs) -> None:
        """Connects to the NATS server(s)."""
        if self._nc and self._nc.is_connected:
            logger.warning(f"[{self._source_subsystem}] Already connected to NATS.")
            return

        logger.info(f"[{self._source_subsystem}] Connecting to NATS servers: {servers}")
        try:
            self._nc = await nats.connect(servers=servers, **kwargs)
            logger.info(
                f"[{self._source_subsystem}] Successfully connected to NATS: {self._nc.connected_url.netloc if self._nc.connected_url else 'N/A'}"
            )
        except NoServersError as e:
            logger.error(f"[{self._source_subsystem}] Could not connect to any NATS servers: {e}")
            self._nc = None
            raise ConnectionError(
                f"NATS connection failed: No servers available at {servers}"
            ) from e
        except Exception as e:
            logger.error(
                f"[{self._source_subsystem}] An unexpected error occurred during NATS connection: {e}",
                exc_info=True,
            )
            self._nc = None
            raise ConnectionError(f"NATS connection failed: {e}") from e

    async def disconnect(self) -> None:
        """Disconnects from the NATS server gracefully."""
        if self._nc and self._nc.is_connected:
            logger.info(f"[{self._source_subsystem}] Disconnecting from NATS...")
            try:
                await self._nc.close()
                logger.info(f"[{self._source_subsystem}] Successfully disconnected from NATS.")
            except Exception as e:
                logger.error(
                    f"[{self._source_subsystem}] Error during NATS disconnection: {e}",
                    exc_info=True,
                )
            finally:
                self._nc = None
                self._subscriptions = {}
        else:
            logger.warning(
                f"[{self._source_subsystem}] disconnect called but not connected to NATS."
            )

    async def publish(self, subject: str, payload: Dict[str, Any], **kwargs) -> None:
        """Publishes a message dictionary to a NATS subject, wrapping it in the standard envelope."""
        if not self._nc or not self._nc.is_connected:
            logger.error(
                f"[{self._source_subsystem}] Cannot publish to {subject}: Not connected to NATS."
            )
            raise ConnectionError("Not connected to NATS")

        try:
            wrapped_payload = self._wrap_payload(payload)
            logger.debug(
                f"[{self._source_subsystem}] Publishing {len(wrapped_payload)} bytes to subject '{subject}'"
            )
            await self._nc.publish(subject, wrapped_payload, **kwargs)
        except ConnectionClosedError:
            logger.error(
                f"[{self._source_subsystem}] Cannot publish to {subject}: Connection closed."
            )
            raise ConnectionError("NATS connection closed")
        except TimeoutError:
            logger.error(f"[{self._source_subsystem}] Timeout publishing to {subject}.")
            raise TimeoutError(f"Timeout publishing to {subject}")  # Re-raise stdlib TimeoutError
        except ValueError as e:  # Catch serialization errors from _wrap_payload
            logger.error(
                f"[{self._source_subsystem}] Failed to wrap/serialize payload for {subject}: {e}"
            )
            raise
        except Exception as e:
            logger.error(
                f"[{self._source_subsystem}] Error publishing to {subject}: {e}", exc_info=True
            )
            raise

    async def subscribe(
        self,
        subject: str,
        callback: Callable[[Dict[str, Any]], Coroutine[Any, Any, None]],
        **kwargs,
    ) -> Any:
        """Subscribes to a NATS subject. The callback receives the deserialized message envelope dictionary."""
        if not self._nc or not self._nc.is_connected:
            logger.error(
                f"[{self._source_subsystem}] Cannot subscribe to {subject}: Not connected to NATS."
            )
            raise ConnectionError("Not connected to NATS")

        async def message_handler(msg: Msg):
            # Receives NATS message, unwraps payload, calls user callback
            try:
                # Pass the entire deserialized envelope to the callback
                envelope = self._unwrap_payload(msg.data)
                logger.debug(
                    f"[{self._source_subsystem}] Received message on '{subject}', invoking callback."
                )
                await callback(envelope)
            except ValueError as e:  # Catch deserialization/unwrap errors
                logger.error(
                    f"[{self._source_subsystem}] Cannot process message on '{subject}': {e}"
                )
                # Optionally, send to an error queue or take other action
            except Exception as e:
                logger.error(
                    f"[{self._source_subsystem}] Error in callback for subject '{subject}': {e}",
                    exc_info=True,
                )
                # Decide how to handle callback errors

        try:
            logger.info(f"[{self._source_subsystem}] Subscribing to NATS subject: '{subject}'")
            sub = await self._nc.subscribe(subject, cb=message_handler, **kwargs)
            # Store subscription using a unique ID or the NATS sub object itself
            sub_id = str(uuid.uuid4())  # Use a UUID as the key for robust unsubscribe
            self._subscriptions[sub_id] = sub
            return sub_id  # Return the UUID identifier
        except ConnectionClosedError:
            logger.error(
                f"[{self._source_subsystem}] Cannot subscribe to {subject}: Connection closed."
            )
            raise ConnectionError("NATS connection closed")
        except Exception as e:
            logger.error(
                f"[{self._source_subsystem}] Error subscribing to {subject}: {e}", exc_info=True
            )
            raise

    async def unsubscribe(self, subscription_id: Any) -> None:
        """Unsubscribes using the identifier returned by subscribe."""
        if subscription_id not in self._subscriptions:
            logger.warning(
                f"[{self._source_subsystem}] Attempted to unsubscribe with unknown id: {subscription_id}"
            )
            return

        sub = self._subscriptions.pop(subscription_id)  # Remove and get NATS sub object
        if not isinstance(sub, nats.aio.subscription.Subscription):
            logger.error(
                f"[{self._source_subsystem}] Invalid object found for subscription id: {subscription_id}"
            )
            return  # Should not happen if stored correctly

        if not self._nc or not self._nc.is_connected:
            logger.warning(
                f"[{self._source_subsystem}] Cannot unsubscribe from {sub.subject}: Not connected to NATS."
            )
            return

        try:
            logger.info(
                f"[{self._source_subsystem}] Unsubscribing from NATS subject: '{sub.subject}' (ID: {subscription_id})"
            )
            await sub.unsubscribe()
        except ConnectionClosedError:
            logger.warning(
                f"[{self._source_subsystem}] Cannot unsubscribe from {sub.subject}: Connection already closed."
            )
        except Exception as e:
            logger.error(
                f"[{self._source_subsystem}] Error unsubscribing from {sub.subject}: {e}",
                exc_info=True,
            )

    async def request(
        self, subject: str, payload: Dict[str, Any], timeout: float = 1.0, **kwargs
    ) -> Dict[str, Any]:
        """Sends a request dictionary via NATS and returns the response dictionary envelope."""
        if not self._nc or not self._nc.is_connected:
            logger.error(
                f"[{self._source_subsystem}] Cannot send request to {subject}: Not connected to NATS."
            )
            raise ConnectionError("Not connected to NATS")

        # Use message's UUID as correlation ID for simplicity
        correlation_id = str(uuid.uuid4())
        try:
            wrapped_payload = self._wrap_payload(payload, correlation_id=correlation_id)
            logger.debug(
                f"[{self._source_subsystem}] Sending request ({len(wrapped_payload)} bytes) to '{subject}' with timeout {timeout}s (CorrID: {correlation_id})"
            )
            response_msg = await self._nc.request(
                subject, wrapped_payload, timeout=timeout, **kwargs
            )
            logger.debug(
                f"[{self._source_subsystem}] Received response for request to '{subject}' (CorrID: {correlation_id})"
            )
            response_envelope = self._unwrap_payload(response_msg.data)
            # Optional: Check correlation ID match if needed, though NATS handles request-reply correlation
            # if response_envelope.get("correlation_id") != correlation_id:
            #    logger.error("Correlation ID mismatch!") # Handle error
            return response_envelope  # Return the full response envelope

        except TimeoutError:
            logger.error(
                f"[{self._source_subsystem}] Timeout waiting for response from {subject} (CorrID: {correlation_id})."
            )
            raise TimeoutError(
                f"Timeout waiting for response from {subject}"
            )  # Re-raise stdlib TimeoutError
        except ConnectionClosedError:
            logger.error(
                f"[{self._source_subsystem}] Cannot send request to {subject}: Connection closed."
            )
            raise ConnectionError("NATS connection closed")
        except nats.errors.NoServersError:
            logger.error(
                f"[{self._source_subsystem}] Cannot send request to {subject}: No NATS servers available."
            )
            raise ConnectionError("No NATS servers available")
        except ValueError as e:  # Catch wrap/unwrap errors
            logger.error(
                f"[{self._source_subsystem}] Failed to wrap/unwrap payload for {subject}: {e}"
            )
            raise
        except Exception as e:
            logger.error(
                f"[{self._source_subsystem}] Error during request to {subject}: {e}", exc_info=True
            )
            raise

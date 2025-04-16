import asyncio
import nats
import json # Import json
import uuid # Import uuid
from datetime import datetime, timezone # Import timezone
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError
from typing import Dict, Any, Callable, List, Optional, Coroutine

from koios.logger import KoiosLogger # Assuming logger is available
from ..interfaces.mycelium_interface import MyceliumInterface

# TODO: Get logger instance properly
logger = KoiosLogger.get_logger("MYCELIUM.Core.NatsInterface")

class NatsMyceliumInterface(MyceliumInterface):
    """Concrete implementation of MyceliumInterface using NATS."""

    def __init__(self, config: Dict[str, Any], node_id: str):
        self.config = config
        self.node_id = node_id
        self.nc: Optional[nats.NATS] = None
        self.subscriptions: Dict[str, nats.Subscription] = {}
        # Store futures keyed by correlation_id
        self.response_futures: Dict[str, asyncio.Future] = {}
        logger.info(f"NATS Interface initialized for node: {self.node_id}")

    def _create_standard_envelope(self, message_type: str, topic: str, payload: Dict[str, Any], target_node: Optional[str] = None, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """Wraps a payload in the standard Mycelium message envelope."""
        msg_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        # Default target node based on message type if not provided
        if target_node is None:
            target = "TOPIC_TARGET" if message_type.upper() in ["EVENT", "LOG"] else None
        else:
            target = target_node

        return {
            "message_id": msg_id,
            "timestamp": timestamp,
            "source_subsystem": self.node_id,
            "correlation_id": correlation_id,
            "payload": payload,
            "metadata": {
                # Add standard metadata
                "schema_version": self.config.get("message_schema_version", "1.0"),
                "topic": topic, # Include topic in metadata for context
                 "message_type": message_type.upper(), # Include type in metadata
                 "target_node": target # Include resolved target
                 # Add other potential metadata like priority, trace_id later
            }
        }

    def _encode_message(self, message: Dict[str, Any]) -> bytes:
        """Encodes the full message envelope to bytes."""
        try:
            # Ensure datetime objects are handled if not already isoformat strings
            return json.dumps(message, default=str).encode('utf-8')
        except TypeError as e:
            logger.error(f"Failed to JSON encode message: {e}. Message sample: {str(message)[:200]}")
            raise ValueError(f"Cannot serialize message payload: {e}")

    def _decode_message(self, data: bytes) -> Optional[Dict[str, Any]]:
        """Decodes bytes into the standard message envelope dictionary."""
        try:
            return json.loads(data.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode incoming JSON message: {e}", exc_info=False)
            return None
        except Exception as e:
            logger.error(f"Error decoding message data: {e}", exc_info=True)
            return None

    async def connect(self, node_type: str = "GENERIC", version: str = "0.1", capabilities: Optional[List[str]] = None) -> bool:
        """Registers the subsystem node with the network by connecting to NATS."""
        if self.nc and self.nc.is_connected:
            logger.warning("Already connected to NATS.")
            return True

        servers = self.config.get('servers', ["nats://localhost:4222"])
        try:
            logger.info(f"Connecting node '{self.node_id}' to NATS servers: {servers}")
            connect_options = {
                "servers": servers,
                "name": f"{self.node_id}-{node_type}-v{version}",
                "error_cb": self._error_cb,
                "reconnected_cb": self._reconnected_cb,
                "disconnected_cb": self._disconnected_cb,
                "closed_cb": self._closed_cb,
                "connect_timeout": self.config.get("connect_timeout", 10),
                "reconnect_time_wait": self.config.get("reconnect_wait", 2),
                "max_reconnect_attempts": self.config.get("max_reconnect", 60),
            }
            # Add credentials if configured
            user = self.config.get("user")
            password = self.config.get("password")
            token = self.config.get("token")
            if user and password: connect_options["user"] = user; connect_options["password"] = password
            elif token: connect_options["token"] = token

            self.nc = await nats.connect(**connect_options)
            logger.info(f"Successfully connected to NATS as '{self.node_id}'. Status: {self.nc.status}")
            await self.report_health("connected", {"capabilities": capabilities or []})
            return True
        except NoServersError as e:
            logger.error(f"Could not connect to any NATS servers: {e}")
            self.nc = None
            return False
        except Exception as e:
            logger.error(f"Error connecting to NATS: {e}", exc_info=True)
            self.nc = None
            return False

    async def disconnect(self) -> bool:
        """Deregisters the subsystem node by closing the NATS connection."""
        if self.nc and not self.nc.is_closed:
            logger.info(f"Disconnecting node '{self.node_id}' from NATS.")
            # Unsubscribe from all topics gracefully
            for topic in list(self.subscriptions.keys()):
                await self.unsubscribe(topic)
            # Drain ensures buffered messages are sent before closing
            await self.nc.drain()
            # Close is now implicitly handled by drain in nats-py >= 2.0, but explicit close is safe
            if not self.nc.is_closed:
                 await self.nc.close()
            logger.info(f"Node '{self.node_id}' disconnected.")
            self.nc = None
            return True
        logger.warning("disconnect called but not connected.")
        return False

    async def send_request(self, target_node: str, topic: str, payload: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
        """Sends a request and waits for a response using NATS request/reply."""
        if not self.nc or not self.nc.is_connected:
            raise ConnectionError("Not connected to NATS.")

        correlation_id = str(uuid.uuid4())
        # Target node info might be embedded in topic for routing by subscriber
        # or handled by NATS server/queues depending on setup.
        # The standard envelope still contains the intended target.
        request_message = self._create_standard_envelope(
            "REQUEST", topic, payload, target_node=target_node, correlation_id=correlation_id
        )
        encoded_message = self._encode_message(request_message)

        logger.debug(f"Sending request ({correlation_id}) to topic '{topic}'")
        future = asyncio.Future()
        self.response_futures[correlation_id] = future

        try:
            # NATS request sends and waits for ONE reply on an internal inbox subject
            response_msg = await self.nc.request(topic, encoded_message, timeout=timeout)
            # If nc.request completes without timeout, a response was received.
            # The callback (_handle_response) should have already resolved the future.
            # We await the future here to get the processed result or handle errors set by callback.
            logger.debug(f"NATS request completed for {correlation_id}, awaiting future.")
            return await asyncio.wait_for(future, timeout=0.1) # Short wait, should be resolved

        except TimeoutError:
            logger.error(f"Timeout ({timeout}s) waiting for response on NATS topic '{topic}' for request {correlation_id}")
            future.set_exception(TimeoutError(f"Request timed out on topic {topic}"))
            raise # Re-raise NATS TimeoutError
        except ConnectionClosedError as e:
             logger.error(f"Connection closed while sending request to '{topic}': {e}")
             future.set_exception(e)
             raise
        except Exception as e:
            logger.error(f"Error during NATS request to '{topic}': {e}", exc_info=True)
            future.set_exception(e)
            raise
        finally:
            # Clean up the future regardless of outcome
            self.response_futures.pop(correlation_id, None)

    async def _handle_response(self, msg):
        """Internal callback for handling responses to requests."""
        decoded_message = self._decode_message(msg.data)
        if not decoded_message or "header" not in decoded_message or "payload" not in decoded_message:
            logger.error(f"Received invalid response message format on reply subject: {msg.subject}")
            return

        header = decoded_message["header"]
        payload = decoded_message["payload"]
        correlation_id = header.get("correlation_id")

        if correlation_id and correlation_id in self.response_futures:
            future = self.response_futures.get(correlation_id)
            if future and not future.done():
                logger.debug(f"Received response for request {correlation_id}")
                if payload.get("status") == "ERROR":
                    error_details = payload.get("error_message", "Unknown error in response")
                    logger.warning(f"Received ERROR response payload for {correlation_id}: {error_details}")
                    future.set_exception(Exception(f"Request failed: {error_details}"))
                else:
                    future.set_result(payload) # Resolve future with the payload
            # Future might be already done if timeout occurred in send_request
            # or might not exist if cleanup happened.
        else:
            logger.warning(f"Received response with unknown or missing correlation_id: {correlation_id}")

    async def publish_event(self, topic: str, payload: Dict[str, Any]):
        """Publishes an event wrapped in the standard envelope."""
        if not self.nc or not self.nc.is_connected:
            logger.error(f"Cannot publish event to '{topic}', not connected to NATS.")
            return

        event_message = self._create_standard_envelope("EVENT", topic, payload)
        encoded_message = self._encode_message(event_message)

        logger.debug(f"Publishing event {event_message['message_id']} to topic '{topic}'")
        try:
            await self.nc.publish(topic, encoded_message)
        except ConnectionClosedError:
            logger.error(f"Connection closed while publishing event to '{topic}'")
        except Exception as e:
            logger.error(f"Error publishing event to '{topic}': {e}", exc_info=True)

    async def subscribe(self, topic: str, callback_function: Callable[[Dict[str, Any]], Coroutine]):
        """Subscribes to a topic, providing an async callback function.

        The callback receives the full decoded message dictionary (header + payload).
        Handles standard request/reply by routing responses to _handle_response.
        """
        if not self.nc or not self.nc.is_connected:
            raise ConnectionError("Not connected to NATS.")

        if topic in self.subscriptions:
            logger.warning(f"Already subscribed to topic '{topic}'. Unsubscribing first.")
            await self.unsubscribe(topic)

        async def internal_nats_callback(msg: nats.aio.msg.Msg):
            subject = msg.subject
            reply_subject = msg.reply
            decoded_message = self._decode_message(msg.data)

            if not decoded_message:
                logger.error(f"Failed to decode message received on topic '{subject}'")
                return

            msg_type = decoded_message.get("header", {}).get("message_type", "UNKNOWN").upper()
            corr_id = decoded_message.get("header", {}).get("correlation_id")

            # Check if it's a response to one of our requests (using correlation_id)
            if corr_id and corr_id in self.response_futures:
                 await self._handle_response(decoded_message)
                 return # Response handled, don't call user callback
            # Check if it's a direct reply to a request WE made (less common for services)
            elif msg_type == "RESPONSE" and corr_id:
                 logger.warning(f"Received RESPONSE message on non-inbox subject '{subject}'. Might be misrouted?")
                 # Optionally handle anyway if needed
                 await self._handle_response(decoded_message)
                 return
            # Check if it's a request message needing a reply (Standard Req/Rep)
            elif msg_type == "REQUEST" and reply_subject:
                logger.debug(f"Received REQUEST message on '{subject}' requiring reply to '{reply_subject}'")
                # User callback MUST handle sending the response via nc.publish(reply_subject, ...)
                try:
                    # Pass the full message and reply subject to user callback
                    await callback_function(decoded_message, reply_subject=reply_subject)
                except Exception as cb_e:
                    logger.error(f"Error in REQUEST callback for '{subject}': {cb_e}", exc_info=True)
                    # Optionally send error response back
                    try:
                         error_payload = {"status": "ERROR", "error_message": f"Error processing request: {cb_e}"}
                         error_msg = self._create_standard_envelope("RESPONSE", subject, error_payload, correlation_id=corr_id)
                         await self.nc.publish(reply_subject, self._encode_message(error_msg))
                    except Exception as pub_e:
                         logger.error(f"Failed to publish error response to {reply_subject}: {pub_e}")
            # Otherwise, assume it's a standard pub/sub message or event
            else:
                logger.debug(f"Received {msg_type} message on '{subject}'. ID: {decoded_message.get('header',{}).get('message_id')}")
                try:
                    await callback_function(decoded_message)
                except Exception as cb_e:
                    logger.error(f"Error in standard callback for topic '{subject}': {cb_e}", exc_info=True)

        try:
            logger.info(f"Subscribing node '{self.node_id}' to topic '{topic}'")
            queue_group = self.config.get("queue_group")
            sub = await self.nc.subscribe(topic, cb=internal_nats_callback, queue=queue_group or "")
            self.subscriptions[topic] = sub
            logger.info(f"Successfully subscribed to topic '{topic}' (Queue: '{queue_group or ""}')")
        except Exception as e:
            logger.error(f"Error subscribing to topic '{topic}': {e}", exc_info=True)
            raise

    async def unsubscribe(self, topic: str):
        """Unsubscribes from a topic."""
        if topic in self.subscriptions:
            sub = self.subscriptions.pop(topic)
            try:
                if self.nc and not self.nc.is_closed:
                    await sub.unsubscribe()
                    logger.info(f"Unsubscribed from topic '{topic}'")
                else:
                     logger.warning(f"Cannot unsubscribe from '{topic}', NATS connection closed.")
            except Exception as e:
                logger.error(f"Error unsubscribing from '{topic}': {e}", exc_info=True)
                self.subscriptions[topic] = sub # Put back if failed
        else:
            logger.warning(f"Attempted to unsubscribe from topic '{topic}' but was not subscribed.")

    async def report_health(self, status: str, details: Optional[Dict[str, Any]] = None):
        """Reports the node's health status to the network."""
        health_payload = {"node_id": self.node_id, "status": status, "details": details or {}}
        health_topic = self.config.get("mycelium", {}).get("topics", {}).get("health_report", f"event.mycelium.health.{self.node_id}")
        await self.publish_event(health_topic, health_payload)

    # --- NATS Callback Handlers ---

    async def _disconnected_cb(self):
        logger.warning(f"NATS client '{self.node_id}' disconnected.")
        # Cancel pending response futures on disconnect
        for future in self.response_futures.values():
            if not future.done():
                future.set_exception(ConnectionClosedError("NATS connection disconnected"))
        self.response_futures.clear()

    async def _reconnected_cb(self):
        logger.info(f"NATS client '{self.node_id}' reconnected. Status: {self.nc.status if self.nc else 'N/A'}")
        # Resubscribe logic might be needed depending on NATS client behavior
        # logger.info("Attempting to re-subscribe to topics...")
        # for topic, callback in self.subscribed_callbacks.items(): # Need to store callbacks
        #     try:
        #         await self.subscribe(topic, callback)
        #     except Exception as e:
        #         logger.error(f"Failed to re-subscribe to {topic}: {e}")

    async def _error_cb(self, e):
        logger.error(f"NATS Error for '{self.node_id}': {e}", exc_info=isinstance(e, Exception))

    async def _closed_cb(self):
        logger.info(f"NATS connection '{self.node_id}' is permanently closed.")
        self.nc = None
        # Cancel pending futures again on final close
        for future in self.response_futures.values():
            if not future.done():
                future.set_exception(ConnectionClosedError("NATS connection closed"))
        self.response_futures.clear()

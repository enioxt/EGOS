"""
NATS client functionality for the EGOS Dashboard.
Handles connections to the NATS server, message subscriptions, and data reception.
"""

import json
import threading
import time

import streamlit as st

from src.config import NATS_SERVER_URL  # Import the server URL from config
from src.koios_logger import KoiosLogger

# Import our mock implementation
from src.nats_mock import Connection, ConnectionState

# Setup KoiosLogger
logger = KoiosLogger.get_logger("DASHBOARD.NatsClient")

# Constants
DEFAULT_NATS_SUBJECTS = [
    "egos.status.>",  # For subsystem status updates
    "egos.metrics.>",  # For metric updates
    "egos.alerts.>",  # For system alerts
    "egos.heartbeat.>",  # For heartbeat messages
]


class NatsConnectionManager:
    """Manages the connection to NATS and handles message processing."""

    def __init__(self, server_url=NATS_SERVER_URL, subjects=None):
        """
        Initialize the NATS connection manager.

        Args:
            server_url: URL of the NATS server
            subjects: List of subjects to subscribe to
        """
        self.server_url = server_url
        self.subjects = subjects or DEFAULT_NATS_SUBJECTS
        self.is_connected = False
        self.connection_error = None
        self.subscription_handlers = []
        self.connection = None
        self.message_thread = None
        self.stop_event = threading.Event()

        # Log initialization
        KoiosLogger.log_system_event(
            logger,
            "initialization",
            "NATS Connection Manager initialized",
            {"server_url": server_url, "subjects": self.subjects},
        )

    def connect(self):
        """
        Connect to the NATS server.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create and connect
            self.connection = Connection(uris=[self.server_url])
            self.connection.connect()

            # Check if connection was successful
            if self.connection.state == ConnectionState.CONNECTED:
                self.is_connected = True
                self.connection_error = None

                # Subscribe to subjects
                for subject in self.subjects:
                    self.connection.subscribe(subject)

                # Start message handling thread
                self.stop_event.clear()
                self.message_thread = threading.Thread(target=self._message_loop)
                self.message_thread.daemon = True
                self.message_thread.start()

                # Log successful connection
                KoiosLogger.log_system_event(
                    logger,
                    "connection",
                    "Successfully connected to NATS server",
                    {"server_url": self.server_url},
                )

                return True
            else:
                self.is_connected = False
                self.connection_error = "Failed to connect to NATS server"

                # Log connection failure
                KoiosLogger.log_system_event(
                    logger,
                    "connection_error",
                    "Failed to connect to NATS server",
                    {"server_url": self.server_url, "state": str(self.connection.state)},
                )

                return False

        except Exception as e:
            self.is_connected = False
            self.connection_error = str(e)

            # Log connection error
            KoiosLogger.log_system_event(
                logger,
                "connection_error",
                f"Error connecting to NATS server: {str(e)}",
                {"server_url": self.server_url, "error": str(e)},
            )

            return False

    def _message_loop(self):
        """Background thread to receive and process NATS messages."""
        while not self.stop_event.is_set() and self.is_connected:
            try:
                # Wait for message with timeout (allows thread to check stop_event)
                msg = self.connection.next_msg(timeout=0.5)
                if msg:
                    self._handle_message(msg)
            except Exception as e:
                # Log error but continue processing
                KoiosLogger.log_system_event(
                    logger,
                    "message_processing_error",
                    f"Error processing NATS message: {str(e)}",
                    {"error": str(e)},
                )
                time.sleep(0.1)  # Brief pause to avoid tight loop on repeated errors

    def _handle_message(self, msg):
        """
        Process incoming NATS messages.

        Args:
            msg: The NATS message
        """
        subject = msg.subject
        data = msg.data.decode()

        try:
            # Try to parse as JSON
            payload = json.loads(data)

            # Process based on subject pattern
            if subject.startswith("egos.status."):
                self._process_status_update(subject, payload)
            elif subject.startswith("egos.metrics."):
                self._process_metrics_update(subject, payload)
            elif subject.startswith("egos.alerts."):
                self._process_alert(subject, payload)
            elif subject.startswith("egos.heartbeat."):
                self._process_heartbeat(subject, payload)

            # Log message received
            KoiosLogger.log_system_event(
                logger,
                "message_received",
                f"Received NATS message on subject {subject}",
                {
                    "subject": subject,
                    "message_type": subject.split(".")[1]
                    if len(subject.split(".")) > 1
                    else "unknown",
                },
            )

        except json.JSONDecodeError:
            # Handle non-JSON messages
            st.session_state.nats_messages.append(f"Raw message on {subject}: {data}")

            # Log invalid message format
            KoiosLogger.log_system_event(
                logger,
                "invalid_message_format",
                f"Received non-JSON message on {subject}",
                {"subject": subject, "data": data[:100] + "..." if len(data) > 100 else data},
            )

    def _process_status_update(self, subject, payload):
        """Process subsystem status updates."""
        # Extract subsystem from subject (e.g., egos.status.ETHIK)
        parts = subject.split(".")
        if len(parts) >= 3:
            subsystem = parts[2]
            # Store in session state for display
            if "subsystem_status" not in st.session_state:
                st.session_state.subsystem_status = {}

            st.session_state.subsystem_status[subsystem] = {
                "status": payload.get("status", "Unknown"),
                "timestamp": payload.get("timestamp"),
                "details": payload.get("details", {}),
            }

    def _process_metrics_update(self, subject, payload):
        """Process metrics updates."""
        # Extract subsystem and metric type from subject (e.g., egos.metrics.ETHIK.validation)
        parts = subject.split(".")
        if len(parts) >= 3:
            subsystem = parts[2]
            metric_type = parts[3] if len(parts) >= 4 else "general"

            # Store in session state for display
            if "subsystem_metrics" not in st.session_state:
                st.session_state.subsystem_metrics = {}

            if subsystem not in st.session_state.subsystem_metrics:
                st.session_state.subsystem_metrics[subsystem] = {}

            st.session_state.subsystem_metrics[subsystem][metric_type] = payload

    def _process_alert(self, subject, payload):
        """Process system alerts."""
        # Add to alert list, keeping only the most recent N alerts
        if "alerts" not in st.session_state:
            st.session_state.alerts = []

        st.session_state.alerts.insert(0, payload)
        if len(st.session_state.alerts) > 10:  # Keep only 10 most recent alerts
            st.session_state.alerts.pop()

    def _process_heartbeat(self, subject, payload):
        """Process heartbeat messages."""
        # Extract subsystem from subject (e.g., egos.heartbeat.ETHIK)
        parts = subject.split(".")
        if len(parts) >= 3:
            subsystem = parts[2]

            # Update last seen timestamp
            if "heartbeats" not in st.session_state:
                st.session_state.heartbeats = {}

            st.session_state.heartbeats[subsystem] = payload.get("timestamp", "")

    def disconnect(self):
        """Disconnect from the NATS server."""
        if not self.is_connected:
            return

        # Signal thread to stop and wait for it
        self.stop_event.set()
        if self.message_thread and self.message_thread.is_alive():
            self.message_thread.join(timeout=2.0)  # Wait up to 2 seconds for thread to exit

        # Close connection
        if self.connection:
            self.connection.close()
            self.is_connected = False

        # Log disconnection
        KoiosLogger.log_system_event(
            logger,
            "disconnection",
            "Disconnected from NATS server",
            {"server_url": self.server_url},
        )


def connect_to_nats(server_url=NATS_SERVER_URL):
    """
    Helper function to connect to NATS from Streamlit.
    Updates session state with connection status.

    Args:
        server_url: URL of the NATS server

    Returns:
        bool: True if successful, False otherwise
    """
    # Initialize session variables if they don't exist
    if "nats_connection_status" not in st.session_state:
        st.session_state.nats_connection_status = "Disconnected"

    if "nats_messages" not in st.session_state:
        st.session_state.nats_messages = []

    # Update status
    st.session_state.nats_connection_status = "Connecting..."

    # Log connection attempt
    KoiosLogger.log_user_action(logger, "nats_connection_attempt", {"server_url": server_url})

    # Create manager and connect
    manager = NatsConnectionManager(server_url)
    success = manager.connect()

    # Update status based on result
    if success:
        st.session_state.nats_connection_status = "Connected"
        st.session_state.nats_manager = manager

        # Log successful connection
        KoiosLogger.log_user_action(logger, "nats_connection_success", {"server_url": server_url})
    else:
        error_msg = manager.connection_error or "Unknown error"
        st.session_state.nats_connection_status = f"Error: {error_msg}"

        # Log connection failure
        KoiosLogger.log_user_action(
            logger, "nats_connection_failure", {"server_url": server_url, "error": error_msg}
        )

    return success


def disconnect_from_nats():
    """
    Helper function to disconnect from NATS.

    Returns:
        bool: True if successful, False otherwise
    """
    if "nats_manager" in st.session_state and st.session_state.nats_manager.is_connected:
        # Log disconnection attempt
        KoiosLogger.log_user_action(logger, "nats_disconnection_attempt", {})

        st.session_state.nats_manager.disconnect()
        st.session_state.nats_connection_status = "Disconnected"

        # Log successful disconnection
        KoiosLogger.log_user_action(logger, "nats_disconnection_success", {})

        return True
    return False

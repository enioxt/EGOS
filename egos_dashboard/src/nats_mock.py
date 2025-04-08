"""
Mock NATS implementation for EGOS Dashboard demonstration purposes.
This simulates NATS functionality when a real NATS server isn't available.
"""

import enum
import json
import random
import threading
import time
from typing import Any, Dict, List, Optional


class ConnectionState(enum.Enum):
    """Enumeration of connection states."""

    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    CLOSED = 3


class Message:
    """Mock message class to simulate NATS messages."""

    def __init__(self, subject: str, data: bytes):
        """
        Initialize a message.

        Args:
            subject: The message subject
            data: The message data
        """
        self.subject = subject
        self.data = data


class Connection:
    """Mock NATS connection class."""

    def __init__(self, uris: List[str]):
        """
        Initialize a connection.

        Args:
            uris: List of server URIs to connect to
        """
        self.uris = uris
        self.state = ConnectionState.DISCONNECTED
        self.subscriptions = []
        self.messages = []
        self.simulation_thread = None
        self.stop_event = threading.Event()

        # Subsystem statuses for simulation
        self.subsystems = [
            "ETHIK",
            "KOIOS",
            "CORUJA",
            "MYCELIUM",
            "ATLAS",
            "NEXUS",
            "CRONOS",
            "HARMONY",
        ]

        # Status values for simulation
        self.status_values = ["HEALTHY", "WARNING", "ERROR", "INACTIVE"]
        self.status_weights = [0.7, 0.15, 0.1, 0.05]  # Mostly healthy

    def connect(self) -> None:
        """Connect to the NATS server."""
        self.state = ConnectionState.CONNECTING
        time.sleep(0.5)  # Simulate connection delay

        # 90% chance of successful connection
        if random.random() < 0.9:
            self.state = ConnectionState.CONNECTED
            # Start simulation thread
            self.stop_event.clear()
            self.simulation_thread = threading.Thread(target=self._simulate_messages)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()
        else:
            self.state = ConnectionState.DISCONNECTED

    def subscribe(self, subject: str) -> None:
        """
        Subscribe to a subject.

        Args:
            subject: The subject to subscribe to
        """
        if self.state != ConnectionState.CONNECTED:
            raise ValueError("Not connected")

        self.subscriptions.append(subject)

    def publish(self, subject: str, data: Dict[str, Any]) -> None:
        """
        Publish a message to a subject.

        Args:
            subject: The subject to publish to
            data: The data to publish
        """
        if self.state != ConnectionState.CONNECTED:
            raise ValueError("Not connected")

        # Add to messages queue
        message = Message(subject, json.dumps(data).encode())
        self.messages.append(message)

    def next_msg(self, timeout: float = 1.0) -> Optional[Message]:
        """
        Get the next message.

        Args:
            timeout: Time to wait for a message

        Returns:
            The next message or None
        """
        if self.state != ConnectionState.CONNECTED:
            return None

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.messages:
                return self.messages.pop(0)
            time.sleep(0.01)

        return None

    def close(self) -> None:
        """Close the connection."""
        self.stop_event.set()
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=2.0)

        self.state = ConnectionState.CLOSED
        self.subscriptions = []
        self.messages = []

    def _simulate_messages(self) -> None:
        """Simulate incoming messages for the dashboard."""
        while not self.stop_event.is_set():
            # Only generate messages if we have subscriptions
            if not self.subscriptions:
                time.sleep(1.0)
                continue

            # 1 in 5 chance of generating a message each cycle
            if random.random() < 0.2:
                self._generate_random_message()

            time.sleep(1.0)

    def _generate_random_message(self) -> None:
        """Generate a random message for simulation."""
        message_type = random.choice(["status", "metrics", "heartbeat", "alert"])
        subsystem = random.choice(self.subsystems)

        if message_type == "status":
            self._generate_status_message(subsystem)
        elif message_type == "metrics":
            self._generate_metrics_message(subsystem)
        elif message_type == "heartbeat":
            self._generate_heartbeat_message(subsystem)
        elif message_type == "alert":
            self._generate_alert_message(subsystem)

    def _generate_status_message(self, subsystem: str) -> None:
        """Generate a status message for a subsystem."""
        status = random.choices(self.status_values, weights=self.status_weights)[0]

        data = {
            "status": status,
            "timestamp": time.time(),
            "details": {
                "message": f"{subsystem} status update",
                "uptime": random.randint(1, 86400),  # Up to 1 day in seconds
            },
        }

        subject = f"egos.status.{subsystem}"
        if any(subject.startswith(s) for s in self.subscriptions):
            self.messages.append(Message(subject, json.dumps(data).encode()))

    def _generate_metrics_message(self, subsystem: str) -> None:
        """Generate a metrics message for a subsystem."""
        metric_types = {
            "ETHIK": ["validation", "sanitization", "compliance"],
            "KOIOS": ["search", "documentation", "standards"],
            "CORUJA": ["inference", "orchestration", "adaptation"],
            "MYCELIUM": ["messages", "connections", "throughput"],
            "ATLAS": ["mapping", "visualization", "discovery"],
            "NEXUS": ["analysis", "modularization", "dependency"],
            "CRONOS": ["backup", "retention", "versioning"],
            "HARMONY": ["integration", "compatibility", "synchronization"],
        }

        metric_type = random.choice(metric_types.get(subsystem, ["general"]))

        data = {
            "value": random.random() * 100,
            "unit": random.choice(["count", "percent", "bytes", "seconds"]),
            "timestamp": time.time(),
            "change": random.uniform(-10, 10),
        }

        subject = f"egos.metrics.{subsystem}.{metric_type}"
        if any(
            s.endswith(">") or subject.startswith(s.replace(">", "")) for s in self.subscriptions
        ):
            self.messages.append(Message(subject, json.dumps(data).encode()))

    def _generate_heartbeat_message(self, subsystem: str) -> None:
        """Generate a heartbeat message for a subsystem."""
        data = {
            "timestamp": time.time(),
            "version": f"1.{random.randint(0, 9)}.{random.randint(0, 9)}",
        }

        subject = f"egos.heartbeat.{subsystem}"
        if any(
            s.endswith(">") or subject.startswith(s.replace(">", "")) for s in self.subscriptions
        ):
            self.messages.append(Message(subject, json.dumps(data).encode()))

    def _generate_alert_message(self, subsystem: str) -> None:
        """Generate an alert message."""
        alert_levels = ["INFO", "WARNING", "ERROR", "CRITICAL"]
        alert_weights = [0.4, 0.3, 0.2, 0.1]  # Mostly lower severity

        level = random.choices(alert_levels, weights=alert_weights)[0]

        alert_messages = {
            "INFO": [
                f"{subsystem} component started successfully",
                f"Configuration updated for {subsystem}",
                f"New version available for {subsystem}",
            ],
            "WARNING": [
                f"High resource usage in {subsystem}",
                f"Configuration warning in {subsystem}",
                f"Slow response times in {subsystem}",
            ],
            "ERROR": [
                f"Failed to process request in {subsystem}",
                f"Connection error in {subsystem}",
                f"Component failure in {subsystem}",
            ],
            "CRITICAL": [
                f"Service unavailable: {subsystem}",
                f"Database corruption in {subsystem}",
                f"Security breach detected in {subsystem}",
            ],
        }

        message = random.choice(alert_messages[level])

        data = {
            "level": level,
            "message": message,
            "subsystem": subsystem,
            "timestamp": time.time(),
            "alert_id": f"ALERT-{random.randint(1000, 9999)}",
        }

        subject = f"egos.alerts.{subsystem}"
        if any(
            s.endswith(">") or subject.startswith(s.replace(">", "")) for s in self.subscriptions
        ):
            self.messages.append(Message(subject, json.dumps(data).encode()))

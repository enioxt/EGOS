"""
SPARC Message Formats for Mycelium

This module defines standardized message formats for SPARC task communication
via the Mycelium messaging system. These formats enable structured communication
between subsystems when delegating and returning Boomerang Tasks.
"""

import json
import time
from typing import Any, Dict, List, Literal, Optional
import uuid

# Message types for SPARC task communication
MessageType = Literal[
    "task.create", "task.assign", "task.status", "task.complete", "task.delegate", "task.result"
]

# Task types from SPARC methodology
TaskType = Literal[
    "specification",
    "pseudocode",
    "architecture",
    "refinement",
    "code",
    "test",
    "security",
    "documentation",
]

# Task status values
TaskStatus = Literal["created", "assigned", "in_progress", "completed", "failed", "cancelled"]


class SPARCMessageSchema:
    """Base schema for all SPARC-related Mycelium messages."""

    @staticmethod
    def create_message_id() -> str:
        """Generate a unique message ID."""
        return str(uuid.uuid4())

    @staticmethod
    def create_task_message(
        message_type: MessageType,
        task_id: str,
        source_subsystem: str,
        target_subsystem: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a standardized message for SPARC task communication.

        Args:
            message_type: The type of message being sent
            task_id: The ID of the task this message relates to
            source_subsystem: The subsystem sending the message
            target_subsystem: The subsystem the message is intended for (optional)
            payload: Additional data specific to this message type

        Returns:
            A dictionary containing the formatted message
        """
        message = {
            "id": SPARCMessageSchema.create_message_id(),
            "timestamp": time.time(),
            "type": message_type,
            "task_id": task_id,
            "source": source_subsystem,
            "payload": payload or {},
        }

        if target_subsystem:
            message["target"] = target_subsystem

        return message

    @staticmethod
    def get_topic_for_message(message: Dict[str, Any]) -> str:
        """
        Get the appropriate Mycelium topic for a message.

        Args:
            message: The message dictionary

        Returns:
            The topic string for this message
        """
        message_type = message.get("type", "")
        task_id = message.get("task_id", "")
        target = message.get("target", "")

        if message_type == "task.create":
            return f"sparc.task.create.{target}" if target else "sparc.task.create"
        elif message_type == "task.assign":
            return f"sparc.task.assign.{target}"
        elif message_type == "task.status":
            return f"sparc.task.status.{task_id}"
        elif message_type == "task.complete":
            return f"sparc.task.complete.{task_id}"
        elif message_type == "task.delegate":
            return f"sparc.task.delegate.{target}"
        elif message_type == "task.result":
            return f"sparc.task.results.{task_id}"
        else:
            return f"sparc.{message_type}"


class SPARCMessages:
    """Factory methods for creating specific SPARC message types."""

    @staticmethod
    def create_task(
        task_id: str,
        task_type: TaskType,
        title: str,
        description: str,
        acceptance_criteria: List[str],
        source_subsystem: str,
        target_subsystem: Optional[str] = None,
        parent_id: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a message for a new task creation.

        Args:
            task_id: The unique identifier for the task
            task_type: The type of SPARC task
            title: Short description of the task
            description: Detailed description of the task
            acceptance_criteria: List of criteria that define when the task is complete
            source_subsystem: The subsystem creating the task
            target_subsystem: The subsystem the task is assigned to (optional)
            parent_id: ID of the parent task if this is a subtask (optional)
            dependencies: List of task IDs this task depends on (optional)
            inputs: Initial inputs for the task (optional)
            metadata: Additional information about the task (optional)

        Returns:
            A formatted task creation message
        """
        payload = {
            "task_type": task_type,
            "title": title,
            "description": description,
            "acceptance_criteria": acceptance_criteria,
        }

        if parent_id:
            payload["parent_id"] = parent_id

        if dependencies:
            payload["dependencies"] = dependencies

        if inputs:
            payload["inputs"] = inputs

        if metadata:
            payload["metadata"] = metadata

        return SPARCMessageSchema.create_task_message(
            message_type="task.create",
            task_id=task_id,
            source_subsystem=source_subsystem,
            target_subsystem=target_subsystem,
            payload=payload,
        )

    @staticmethod
    def assign_task(
        task_id: str,
        source_subsystem: str,
        target_subsystem: str,
        priority: Optional[str] = None,
        due_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Create a message for assigning a task to a subsystem.

        Args:
            task_id: The ID of the task being assigned
            source_subsystem: The subsystem assigning the task
            target_subsystem: The subsystem the task is assigned to
            priority: Task priority (optional)
            due_time: Timestamp when the task should be completed (optional)

        Returns:
            A formatted task assignment message
        """
        payload = {}

        if priority:
            payload["priority"] = priority

        if due_time:
            payload["due_time"] = due_time

        return SPARCMessageSchema.create_task_message(
            message_type="task.assign",
            task_id=task_id,
            source_subsystem=source_subsystem,
            target_subsystem=target_subsystem,
            payload=payload,
        )

    @staticmethod
    def update_status(
        task_id: str,
        source_subsystem: str,
        status: TaskStatus,
        message: Optional[str] = None,
        progress: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Create a message for updating a task's status.

        Args:
            task_id: The ID of the task being updated
            source_subsystem: The subsystem updating the status
            status: The new status of the task
            message: Optional message about the status update (optional)
            progress: Numeric progress indicator (0-1) (optional)

        Returns:
            A formatted status update message
        """
        payload = {"status": status}

        if message:
            payload["message"] = message

        if progress is not None:
            payload["progress"] = progress

        return SPARCMessageSchema.create_task_message(
            message_type="task.status",
            task_id=task_id,
            source_subsystem=source_subsystem,
            payload=payload,
        )

    @staticmethod
    def complete_task(
        task_id: str,
        source_subsystem: str,
        outputs: Dict[str, Any],
        success: bool = True,
        message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a message for marking a task as complete.

        Args:
            task_id: The ID of the completed task
            source_subsystem: The subsystem completing the task
            outputs: The outputs/results of the task
            success: Whether the task was completed successfully (default: True)
            message: Optional message about the completion (optional)

        Returns:
            A formatted task completion message
        """
        payload = {"success": success, "outputs": outputs}

        if message:
            payload["message"] = message

        return SPARCMessageSchema.create_task_message(
            message_type="task.complete",
            task_id=task_id,
            source_subsystem=source_subsystem,
            payload=payload,
        )

    @staticmethod
    def delegate_task(
        task_id: str,
        source_subsystem: str,
        target_subsystem: str,
        context: Dict[str, Any],
        return_topic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a message for delegating a task to another subsystem (Boomerang).

        Args:
            task_id: The ID of the task being delegated
            source_subsystem: The subsystem delegating the task
            target_subsystem: The subsystem the task is delegated to
            context: Contextual information needed to perform the task
            return_topic: The topic to return results to (optional)

        Returns:
            A formatted task delegation message
        """
        payload = {"context": context}

        if return_topic:
            payload["return_topic"] = return_topic

        return SPARCMessageSchema.create_task_message(
            message_type="task.delegate",
            task_id=task_id,
            source_subsystem=source_subsystem,
            target_subsystem=target_subsystem,
            payload=payload,
        )

    @staticmethod
    def task_result(
        task_id: str,
        source_subsystem: str,
        target_subsystem: str,
        result: Dict[str, Any],
        success: bool = True,
        message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a message for returning task results (Boomerang return).

        Args:
            task_id: The ID of the task with results
            source_subsystem: The subsystem that completed the task
            target_subsystem: The subsystem that delegated the task
            result: The result data from the task
            success: Whether the task was successful (default: True)
            message: Optional message about the result (optional)

        Returns:
            A formatted task result message
        """
        payload = {"success": success, "result": result}

        if message:
            payload["message"] = message

        return SPARCMessageSchema.create_task_message(
            message_type="task.result",
            task_id=task_id,
            source_subsystem=source_subsystem,
            target_subsystem=target_subsystem,
            payload=payload,
        )


# Example usage for reference
if __name__ == "__main__":
    # Example: Create a new architecture task
    create_msg = SPARCMessages.create_task(
        task_id="task-123",
        task_type="architecture",
        title="Design Authentication Flow",
        description="Create the architecture for the authentication system",
        acceptance_criteria=["Component diagram", "API specifications"],
        source_subsystem="ATLAS",
        target_subsystem="NEXUS",
        inputs={"requirements": ["Must support OAuth", "Rate limiting required"]},
    )

    # Get the appropriate topic for this message
    topic = SPARCMessageSchema.get_topic_for_message(create_msg)

    print(f"Topic: {topic}")
    print(f"Message: {json.dumps(create_msg, indent=2)}")

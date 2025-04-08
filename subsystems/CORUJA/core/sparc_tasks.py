"""
SPARC Task Registry for CORUJA

This module implements a registry system for tracking SPARC methodology tasks
(Specification, Pseudocode, Architecture, Refinement, Completion) within EGOS.
It provides functionality for creating, tracking, and completing tasks across
subsystems, enabling Boomerang-style task delegation and return.
"""

from dataclasses import dataclass, field
import logging
import time
from typing import Any, Dict, List, Literal, Optional
import uuid

# Configure logging
logger = logging.getLogger(__name__)

# Task type definitions
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

TaskStatus = Literal["created", "assigned", "in_progress", "completed", "failed", "cancelled"]


@dataclass
class SPARCTask:
    """Represents a task in the SPARC methodology workflow."""

    id: str
    type: TaskType
    title: str
    description: str
    acceptance_criteria: List[str]
    status: TaskStatus = "created"
    owner: str = "CORUJA"  # Default owner is CORUJA
    parent_id: Optional[str] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    subtasks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def update_status(self, new_status: TaskStatus) -> None:
        """Update the status of the task and the updated_at timestamp."""
        self.status = new_status
        self.updated_at = time.time()
        logger.info(f"Task {self.id} status updated to {new_status}")

    def add_subtask(self, subtask_id: str) -> None:
        """Add a subtask to this task."""
        if subtask_id not in self.subtasks:
            self.subtasks.append(subtask_id)
            self.updated_at = time.time()

    def add_output(self, key: str, value: Any) -> None:
        """Add or update an output value."""
        self.outputs[key] = value
        self.updated_at = time.time()

    def meets_criteria(self) -> bool:
        """Check if all acceptance criteria have outputs or indicators of completion."""
        # This is a simplistic implementation - in a real system, this would be more sophisticated
        return len(self.outputs) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "acceptance_criteria": self.acceptance_criteria,
            "status": self.status,
            "owner": self.owner,
            "parent_id": self.parent_id,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "dependencies": self.dependencies,
            "subtasks": self.subtasks,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SPARCTask":
        """Create a task from a dictionary."""
        return cls(**data)


class SPARCTaskRegistry:
    """Registry for managing SPARC methodology tasks."""

    def __init__(self):
        self.tasks: Dict[str, SPARCTask] = {}

    def create_task(
        self,
        type: TaskType,
        title: str,
        description: str,
        acceptance_criteria: List[str],
        owner: str = "CORUJA",
        parent_id: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SPARCTask:
        """Create a new task and add it to the registry."""
        task_id = str(uuid.uuid4())

        task = SPARCTask(
            id=task_id,
            type=type,
            title=title,
            description=description,
            acceptance_criteria=acceptance_criteria,
            owner=owner,
            parent_id=parent_id,
            inputs=inputs or {},
            dependencies=dependencies or [],
            metadata=metadata or {},
        )

        self.tasks[task_id] = task
        logger.info(f"Created new {type} task: {title} (ID: {task_id})")

        # If this is a subtask, update the parent
        if parent_id and parent_id in self.tasks:
            self.tasks[parent_id].add_subtask(task_id)

        return task

    def get_task(self, task_id: str) -> Optional[SPARCTask]:
        """Retrieve a task by its ID."""
        return self.tasks.get(task_id)

    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update the status of a task."""
        task = self.get_task(task_id)
        if task:
            task.update_status(status)
            return True
        return False

    def add_task_output(self, task_id: str, key: str, value: Any) -> bool:
        """Add an output to a task."""
        task = self.get_task(task_id)
        if task:
            task.add_output(key, value)

            # Check if task is now complete based on outputs
            if task.meets_criteria() and task.status != "completed":
                task.update_status("completed")
                logger.info(f"Task {task_id} automatically marked as completed")

            return True
        return False

    def get_tasks_by_status(self, status: TaskStatus) -> List[SPARCTask]:
        """Get all tasks with a specific status."""
        return [task for task in self.tasks.values() if task.status == status]

    def get_tasks_by_owner(self, owner: str) -> List[SPARCTask]:
        """Get all tasks assigned to a specific owner."""
        return [task for task in self.tasks.values() if task.owner == owner]

    def get_tasks_by_type(self, type: TaskType) -> List[SPARCTask]:
        """Get all tasks of a specific type."""
        return [task for task in self.tasks.values() if task.type == type]

    def get_subtasks(self, parent_id: str) -> List[SPARCTask]:
        """Get all subtasks for a given parent task."""
        parent = self.get_task(parent_id)
        if not parent:
            return []

        return [
            self.get_task(subtask_id) for subtask_id in parent.subtasks if subtask_id in self.tasks
        ]


# Create a global instance of the registry
# This follows the singleton pattern for easy access across the codebase
global_task_registry = SPARCTaskRegistry()


def get_task_registry() -> SPARCTaskRegistry:
    """Get the global task registry instance."""
    return global_task_registry


# Example usage:
if __name__ == "__main__":
    # Example of how to use this module
    registry = get_task_registry()

    # Create a parent specification task
    spec_task = registry.create_task(
        type="specification",
        title="Build Authentication System",
        description="Create a secure user authentication system for EGOS",
        acceptance_criteria=[
            "Support email/password login",
            "Implement MFA",
            "Rate limiting for failed attempts",
        ],
        owner="ATLAS",
    )

    # Create subtasks for architecture and implementation
    arch_task = registry.create_task(
        type="architecture",
        title="Authentication System Architecture",
        description="Design the components and interfaces for the auth system",
        acceptance_criteria=["Component diagram", "API specifications", "Data models"],
        owner="NEXUS",
        parent_id=spec_task.id,
    )

    impl_task = registry.create_task(
        type="code",
        title="Implement Authentication Service",
        description="Implement the core authentication service",
        acceptance_criteria=["Passes all tests", "Follows security guidelines"],
        owner="CORUJA",
        parent_id=spec_task.id,
        dependencies=[arch_task.id],
    )

    # Update task statuses
    registry.update_task_status(arch_task.id, "completed")
    registry.add_task_output(
        arch_task.id, "component_diagram", "https://example.com/diagrams/auth-system.png"
    )

    # Print all subtasks of the specification
    subtasks = registry.get_subtasks(spec_task.id)
    for task in subtasks:
        print(f"{task.title}: {task.status}")

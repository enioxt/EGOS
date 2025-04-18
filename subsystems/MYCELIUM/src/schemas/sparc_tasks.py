"""
Pydantic schemas for SPARC task messages exchanged over the Mycelium network.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class SparcStage(str, Enum):
    """Enumeration of the SPARC stages.

    Defines the distinct phases within the SPARC methodology:
    - SETUP: Preparing the task, defining goals, gathering initial resources.
    - PERCEIVE: Gathering information, analyzing context, understanding the current state.
    - ACTION: Performing the core work or intervention.
    - REFLECT: Evaluating the action's outcome, comparing against goals.
    - CONSOLIDATE: Summarizing findings, preparing outputs, cleaning up.
    """
    SETUP = "SETUP"
    PERCEIVE = "PERCEIVE"
    ACTION = "ACTION"
    REFLECT = "REFLECT"
    CONSOLIDATE = "CONSOLIDATE"


class TaskStatus(str, Enum):
    """Enumeration of possible task statuses.

    Represents the lifecycle state of a SPARC task or one of its stages.
    """
    PENDING = "PENDING"  # Task is queued but not yet started
    IN_PROGRESS = "IN_PROGRESS"  # Task or stage is actively being processed
    COMPLETED = "COMPLETED"  # Task or stage finished successfully
    FAILED = "FAILED"  # Task or stage encountered an error and could not complete
    CANCELLED = "CANCELLED"  # Task was cancelled before completion


class BaseSparcMessage(BaseModel):
    """Base model for all SPARC task-related messages.

    Includes common metadata essential for routing, tracking, and context
    across Mycelium network communications.
    """
    message_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for this specific message instance.")
    task_id: uuid.UUID = Field(..., description="Identifier for the overall SPARC task this message relates to.")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp when the message was created.")
    source_subsystem: str = Field(..., description="Identifier of the subsystem sending the message (e.g., 'CORUJA', 'ATLAS').")
    destination_subsystem: str = Field(..., description="Identifier of the intended recipient subsystem.")


class SparcTaskRequest(BaseSparcMessage):
    """Message schema for requesting a SPARC task execution.

    Used to initiate a new SPARC task or delegate it to another subsystem.
    """
    task_type: str = Field(..., description="Identifier for the type of SPARC task to be performed (e.g., 'refactor_code', 'generate_documentation').")
    parameters: Dict[str, Any] = Field(..., description="Dictionary containing the specific inputs and configuration required for the task.")


class SparcTaskResult(BaseSparcMessage):
    """Message schema for communicating the final result of a SPARC task.

    Transmits the overall outcome (success/failure) and any resulting data
    or error information upon task completion.
    """
    status: TaskStatus = Field(..., description="Final status of the overall SPARC task (COMPLETED or FAILED).")
    result_data: Optional[Any] = Field(None, description="The output or result produced by the task, if successful.")
    error_message: Optional[str] = Field(None, description="Description of the error if the task failed.")


class SparcStageUpdate(BaseSparcMessage):
    """Message schema for reporting updates from a specific SPARC stage.

    Allows subsystems to provide progress information, intermediate data, or
    status changes related to a particular stage of an ongoing SPARC task.
    """
    stage: SparcStage = Field(..., description="The SPARC stage this update pertains to.")
    status: TaskStatus = Field(..., description="The current status of this specific stage (e.g., IN_PROGRESS, COMPLETED, FAILED).")
    stage_data: Optional[Dict[str, Any]] = Field(None, description="Optional data generated or relevant during this stage.")
    details: Optional[str] = Field(None, description="Optional human-readable description of the stage's progress or status.")


# Example Usage (for testing/documentation purposes):
if __name__ == "__main__":
    task_id = uuid.uuid4()

    # Task Request
    request_msg = SparcTaskRequest(
        task_id=task_id,
        source_subsystem="ATLAS",
        destination_subsystem="CORUJA",
        task_type="analyze_codebase_complexity",
        parameters={"target_directory": "/path/to/code"}
    )
    print(f"Request Message:\n{request_msg.model_dump_json(indent=2)}\n")

    # Stage Update
    stage_update_msg = SparcStageUpdate(
        task_id=task_id,
        source_subsystem="CORUJA",
        destination_subsystem="ATLAS",
        stage=SparcStage.PERCEIVE,
        status=TaskStatus.IN_PROGRESS,
        stage_data={"files_found": 150},
        details="Scanning project files..."
    )
    print(f"Stage Update Message:\n{stage_update_msg.model_dump_json(indent=2)}\n")

    # Task Result (Success)
    result_msg_success = SparcTaskResult(
        task_id=task_id,
        source_subsystem="CORUJA",
        destination_subsystem="ATLAS",
        status=TaskStatus.COMPLETED,
        result_data={"complexity_score": 75.5, "report_path": "/reports/complexity.txt"}
    )
    print(f"Result Message (Success):\n{result_msg_success.model_dump_json(indent=2)}\n")

    # Task Result (Failure)
    result_msg_fail = SparcTaskResult(
        task_id=task_id,
        source_subsystem="CORUJA",
        destination_subsystem="ATLAS",
        status=TaskStatus.FAILED,
        error_message="Could not access target directory."
    )
    print(f"Result Message (Failure):\n{result_msg_fail.model_dump_json(indent=2)}\n")

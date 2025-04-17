# Proposed content for subsystems/CORUJA/schemas.py

from typing import List, Dict, Any, Optional, Literal, Union
from pydantic import BaseModel, Field
import datetime
import uuid  # Import uuid to generate unique IDs

# --- Basic Task & Agent Structures ---

class ToolDefinition(BaseModel):
    name: str = Field(..., description="Unique name of the tool.")
    description: str = Field(..., description="Description of what the tool does and how to use it.")
    schema_input: Optional[Dict[str, Any]] = Field(None, description="JSON schema for the tool's input arguments.")
    # Potentially add info about required subsystem, security context, etc.

class AgentConfig(BaseModel):
    role: str = Field(..., description="The role the agent assumes (e.g., 'Python Developer', 'Technical Writer').")
    goal: str = Field(..., description="The primary objective of this agent.")
    backstory: Optional[str] = Field(None, description="Contextual background for the agent.")
    llm_config: Dict[str, Any] = Field(..., description="Configuration for the LLM (model name, temperature, etc.). Should align with ModelInterface capabilities.")
    tools: Optional[List[str]] = Field(None, description="List of tool names available to this agent (must exist in ToolRegistry).")
    # verbose: bool = Field(False, description="Enable verbose logging for this agent.")

class TaskDefinition(BaseModel):
    id: str = Field(default_factory=lambda: f"task_{uuid.uuid4()}", description="Unique identifier for this specific task instance.")
    description: str = Field(..., description="Detailed description of the work to be done.")
    expected_output: str = Field(..., description="Description of the expected format or content of the output.")
    assigned_agent_role: Optional[str] = Field(None, description="Role of the agent assigned to this task.")
    required_tools: Optional[List[str]] = Field(None, description="List of tool names required for this task.")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Data required to start the task.")
    # Add fields for context, constraints, etc.

class TaskOutput(BaseModel):
    task_id: str = Field(..., description="ID of the task that produced this output.")
    status: Literal["success", "failure", "partial"] = Field(...)
    result: Optional[Any] = Field(None, description="The actual output/result of the task.")
    error_message: Optional[str] = Field(None, description="Error message if the task failed.")
    agent_role: Optional[str] = Field(None, description="Role of the agent that executed the task.")
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)


# --- Crew Structures ---

class CrewDefinition(BaseModel):
    id: str = Field(default_factory=lambda: f"crewdef_{uuid.uuid4()}", description="Unique identifier for this crew definition.")
    agents: List[AgentConfig] = Field(..., description="List of agent configurations in the crew.")
    tasks: List[TaskDefinition] = Field(..., description="List of tasks to be executed by the crew.")
    process: Literal["sequential", "hierarchical"] = Field("sequential", description="Execution process (currently only sequential).")
    # verbose: bool = Field(False, description="Enable verbose logging for the crew.")

class CrewExecutionRequest(BaseModel):
    crew_definition_id: str = Field(..., description="ID of the CrewDefinition to execute.")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Initial input data for the first task(s).")
    request_id: str = Field(default_factory=lambda: f"crewreq_{uuid.uuid4()}", description="Unique ID for this execution request.")

class CrewExecutionResult(BaseModel):
    request_id: str = Field(..., description="ID of the original execution request.")
    crew_definition_id: str
    status: Literal["completed", "failed", "in_progress"]
    final_output: Optional[Any] = Field(None, description="The final synthesized output of the crew.")
    task_outputs: List[TaskOutput] = Field(..., description="Outputs from individual tasks.")
    error_message: Optional[str] = Field(None)
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)


# --- SPARC Task Structures (Aligning with sparc_orchestration.mdc) ---

SPARCTaskType = Literal[
    "specification", "architecture", "implementation", "testing", "security", "documentation", "refinement", "planning", "analysis", "review"
]

class SPARCTaskBase(BaseModel):
    task_id: str = Field(default_factory=lambda: f"sparc_{uuid.uuid4()}", description="Unique identifier for this SPARC task instance.")
    parent_task_id: Optional[str] = Field(None, description="ID of the parent task, if part of a larger workflow.")
    task_type: SPARCTaskType = Field(..., description="The specific type of SPARC task.")
    title: str = Field(..., description="Brief task description.")
    description: Optional[str] = Field(None, description="Detailed task requirements and context.")
    acceptance_criteria: Optional[List[str]] = Field(None, description="List of criteria for successful completion.")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Input data necessary for this task.")
    dependencies: Optional[List[str]] = Field(None, description="List of task IDs this task depends on.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata (priority, complexity, owner subsystem).")
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now, description="Timestamp of task definition/creation.")


class SPARCTaskCreationRequest(SPARCTaskBase):
    requesting_subsystem: str = Field(...)

class SPARCTaskStatusUpdate(BaseModel):
    task_id: str = Field(...)
    status: Literal["received", "in_progress", "delegated", "awaiting_dependency", "completed", "failed", "paused"]
    message: Optional[str] = Field(None)
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    reporting_subsystem: str = Field(...) # Added reporting subsystem

class SPARCTaskDelegation(BaseModel):
    task_id: str = Field(...) # ID of the parent/originating task
    delegating_subsystem: str = Field(...)
    target_subsystem: str = Field(...)
    delegated_task_details: SPARCTaskBase = Field(..., description="The specific task details being delegated. This will have its own task_id.")
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)

class SPARCTaskResult(BaseModel):
    task_id: str = Field(..., description="ID of the SPARC task that produced this result.")
    status: Literal["success", "failure"]
    output_data: Optional[Dict[str, Any]] = Field(None, description="Output data produced by the task.")
    error_message: Optional[str] = Field(None)
    completed_by_subsystem: str = Field(...)
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)


# --- Common Mycelium Message Wrapper ---

class MyceliumMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4()}", description="Unique ID for this specific message.")
    correlation_id: Optional[str] = Field(None, description="ID to correlate related messages (e.g., request/response, task workflow). Often the request_id or task_id.")
    source_subsystem: str = Field(...)
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    payload_type: str = Field(..., description="Fully qualified name indicating the type of the payload model (e.g., 'subsystems.CORUJA.schemas.CrewExecutionRequest').")
    payload: Union[
        CrewExecutionRequest,
        CrewExecutionResult,
        SPARCTaskCreationRequest,
        SPARCTaskStatusUpdate,
        SPARCTaskDelegation,
        SPARCTaskResult,
        # Add other payload types as needed
    ]

    # Add model validator to ensure payload matches payload_type if needed

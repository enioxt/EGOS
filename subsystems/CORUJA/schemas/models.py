"""
Pydantic models defining core data structures for the CORUJA subsystem.

Version: 0.1.0
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AgentConfig(BaseModel):
    """Configuration defining an AI Agent."""
    agent_id: str = Field(..., description="Unique identifier for the agent configuration.")
    role: str = Field(..., description="The designated role of the agent (e.g., 'Python Developer', 'Documentation Writer').")
    goal: str = Field(..., description="The primary objective or goal for this agent.")
    backstory: Optional[str] = Field(default=None, description="Contextual background information for the agent.")
    llm_config: Dict[str, Any] = Field(..., description="Configuration for the LLM used by this agent, e.g., {'provider': 'openai', 'model': 'gpt-4o', 'temperature': 0.7}.")
    tools: List[str] = Field(default_factory=list, description="List of tool names available to this agent, referencing tools in the ToolRegistry.")

class TaskDefinition(BaseModel):
    """
    Defines a task to be executed, often within the SPARC framework.
    Based on .cursor/rules/sparc_orchestration.mdc.
    """
    id: str = Field(..., description="Unique task identifier.")
    type: str = Field(..., description="Type of task (e.g., 'specification', 'architecture', 'implementation', 'testing', 'documentation', 'security').")
    title: str = Field(..., description="A brief, human-readable title for the task.")
    description: str = Field(..., description="Detailed description of the task requirements and context.")
    acceptance_criteria: List[str] = Field(..., description="A list of criteria that must be met for the task to be considered complete.")
    inputs: Dict[str, Any] = Field(..., description="Input data required for the task.")
    dependencies: List[str] = Field(default_factory=list, description="List of task IDs that must be completed before this task can start.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata, e.g., {'priority': 'high', 'estimated_complexity': 3, 'owner': 'ATLAS'}.")
    expected_output_format: Optional[str] = Field(default=None, description="Description or reference to the expected format of the task's output.")

class SPARCTaskState(BaseModel):
    """Represents the state of a SPARC task being managed by the SPARCTaskRegistry."""
    task_id: str = Field(..., description="The unique identifier of the task.")
    status: str = Field(..., description="Current status of the task (e.g., 'pending', 'running', 'completed', 'failed', 'delegated').")
    current_phase: Optional[str] = Field(default=None, description="The current SPARC phase if applicable (e.g., 'specification', 'implementation').")
    result: Optional[Any] = Field(default=None, description="The output/result of the task upon completion.")
    error_message: Optional[str] = Field(default=None, description="Error message if the task failed.")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="A log of state changes, actions, or significant events related to the task.")

class ToolDefinition(BaseModel):
    """Defines a tool available for agents to use via the ToolRegistry."""
    name: str = Field(..., description="Unique name of the tool.")
    description: str = Field(..., description="Description of what the tool does, used for agent understanding.")
    input_schema: Dict[str, Any] = Field(..., description="JSON Schema defining the expected input arguments for the tool.")
    # The implementation_ref points to the actual callable function or method.
    # This could be a string like 'subsystems.tools.file_io.read_file'
    implementation_ref: str = Field(..., description="Reference to the tool's implementation (e.g., Python import path).")
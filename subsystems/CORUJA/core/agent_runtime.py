"""
Represents the runtime execution environment for a single AI agent instance
within the CORUJA subsystem.
"""
from typing import Dict, Any, Optional, List
import json # Import json

from koios.logger import KoiosLogger # Assuming KoiosLogger path
# from subsystems.CORUJA.schemas.models import TaskDefinition, AgentConfig
# from subsystems.CORUJA.interfaces.model_interface import ModelInterface
# from subsystems.CORUJA.core.tool_registry import ToolRegistry
# from subsystems.CORUJA.core.prompt_manager import PromptManager

logger = KoiosLogger.get_logger("CORUJA.AgentRuntime")

class AgentRuntime:
    """
    Handles the execution lifecycle of a single task assigned to an AI agent.
    It interacts with the ModelInterface, ToolRegistry, and PromptManager
    based on its configuration and the assigned task.
    """

    def __init__(self,
                 agent_config: Dict[str, Any], # Should be AgentConfig model instance
                 model_interface: Any, # Should be ModelInterface instance
                 tool_registry: Any, # Should be ToolRegistry instance
                 prompt_manager: Any): # Should be PromptManager instance
        """
        Initializes the AgentRuntime.

        Args:
            agent_config: Configuration for this specific agent instance.
            model_interface: Interface for interacting with LLMs.
            tool_registry: Registry for accessing available tools.
            prompt_manager: Manager for retrieving and formatting prompts.
        """
        self.agent_config = agent_config
        self.model_interface = model_interface
        self.tool_registry = tool_registry
        self.prompt_manager = prompt_manager
        self.agent_id = agent_config.get('agent_id', 'unknown_agent')
        logger.info(f"AgentRuntime initialized for agent: {self.agent_id}")

    async def execute_task(self, task_definition: Dict[str, Any]) -> Any: # task_definition should be TaskDefinition model
        """
        Executes a given task definition.

        This involves:
        1. Getting the appropriate prompt using PromptManager.
        2. Formatting the prompt with task inputs and agent context.
        3. Invoking the LLM via ModelInterface.
        4. Handling potential tool calls requested by the LLM using ToolRegistry.
        5. Returning the final result.

        Args:
            task_definition: The definition of the task to execute.

        Returns:
            The result produced by the agent for the task.
        """
        task_id = task_definition.get('id', 'unknown_task')
        logger.info(f"Agent {self.agent_id} starting task {task_id} ({task_definition.get('type')})")

        try:
            # 1. Get and format prompt (Placeholder)
            # prompt_name = self._determine_prompt_name(task_definition)
            # variables = {**task_definition.get('inputs', {}), "agent_role": self.agent_config.get('role')}
            # formatted_prompt = await self.prompt_manager.get_prompt(prompt_name, variables)
            formatted_prompt = f"Task: {task_definition.get('description')}\nInputs: {task_definition.get('inputs')}" # Placeholder
            logger.debug(f"Formatted prompt for task {task_id} (placeholder).")

            # --- LLM Interaction & Tool Use Loop ---
            # This loop handles the conversation flow, including potential tool calls
            conversation_history: List[Dict[str, str]] = [] # Add type hint
            current_prompt_content = formatted_prompt # Start with the initial formatted prompt
            max_iterations = 5 # Safety break to prevent infinite loops
            final_result = None

            for i in range(max_iterations):
                logger.debug(f"LLM invocation iteration {i+1} for task {task_id}")

                # TODO: Add conversation history to the prompt/messages if needed by the model interface
                # For now, just sending the latest content
                llm_response = await self.model_interface.invoke_llm(
                    prompt=current_prompt_content, # Pass current content
                    config=self.agent_config.get('llm_config', {})
                )

                # Check for errors from the ModelInterface
                if llm_response.get("error"):
                    logger.error(f"LLM invocation failed for task {task_id}: {llm_response['error']}")
                    # Return an error structure that CrewManager can understand
                    return {"error": f"LLM invocation failed: {llm_response['error']}"}

                # Process tool calls if present
                tool_calls = llm_response.get("tool_calls")
                if tool_calls:
                    logger.info(f"Agent {self.agent_id} received {len(tool_calls)} tool call(s) for task {task_id}")
                    tool_results = []
                    # TODO: Execute tool calls concurrently?
                    for tool_call in tool_calls:
                        tool_name = tool_call.get("name")
                        tool_args_str = tool_call.get("args_str") # Expecting string from interface for now
                        tool_call_id = tool_call.get("id") # Needed for some models like OpenAI

                        if tool_name and tool_args_str is not None:
                            try:
                                # TODO: Add robust JSON parsing with error handling for args_str
                                import json
                                tool_args = json.loads(tool_args_str)
                                logger.info(f"Agent {self.agent_id} executing tool '{tool_name}' with args: {tool_args}")
                                # Execute the tool
                                tool_output = await self.tool_registry.execute_tool(tool_name, tool_args)
                                tool_results.append({
                                    "tool_call_id": tool_call_id, # Include ID if present
                                    "tool_name": tool_name,
                                    "result": tool_output # Store the actual result
                                })
                            except json.JSONDecodeError as json_err:
                                logger.error(f"Failed to decode JSON arguments for tool '{tool_name}': {json_err}")
                                tool_results.append({"tool_call_id": tool_call_id, "tool_name": tool_name, "result": {"error": f"Invalid JSON arguments: {json_err}"}})
                            except Exception as tool_err:
                                logger.error(f"Error executing tool '{tool_name}': {tool_err}", exc_info=True)
                                tool_results.append({"tool_call_id": tool_call_id, "tool_name": tool_name, "result": {"error": f"Tool execution failed: {tool_err}"}})
                        else:
                            logger.warning(f"Malformed tool call received for task {task_id}: {tool_call}")
                            # Decide how to handle malformed calls - skip or return error?

                    # Prepare the next prompt/message including tool results
                    # TODO: Format this based on the specific LLM's requirements for tool responses
                    current_prompt_content = f"Previous Prompt: {current_prompt_content}\nTool Results: {tool_results}"
                    # Add tool results to conversation history if applicable
                    # Format tool results as JSON string for history content
                    try:
                        tool_results_json = json.dumps(tool_results)
                        conversation_history.append({"role": "tool", "content": tool_results_json})
                    except TypeError as e:
                        logger.error(f"Failed to serialize tool_results to JSON for history: {e}")
                        # Fallback to string representation if serialization fails
                        conversation_history.append({"role": "tool", "content": str(tool_results)})

                # Check for final answer text
                elif llm_response.get("text"):
                    final_result = llm_response["text"]
                    logger.info(f"Agent {self.agent_id} received final answer for task {task_id}.")
                    break # Exit loop as we have the final answer
                else:
                    # No text and no tool calls - unexpected state
                    logger.warning(f"LLM response for task {task_id} contained neither text nor tool calls: {llm_response}")
                    return {"error": "LLM response was empty or in unexpected format."}

            # After loop: Check if we got a result or hit max iterations
            if final_result is not None:
                return final_result
            else:
                logger.warning(f"Agent {self.agent_id} reached max iterations ({max_iterations}) for task {task_id} without a final answer.")
                return {"error": f"Agent reached maximum iterations ({max_iterations}) without final answer."}
            # --- End LLM Interaction & Tool Use Loop ---

        except Exception as e:
            logger.error(f"Error executing task {task_id} for agent {self.agent_id}: {e}", exc_info=True)
            # Raise or return an error object
            raise # Re-raise for CrewManager to handle

    def _determine_prompt_name(self, task_definition: Dict[str, Any]) -> str:
        """Placeholder logic to determine which PDD/prompt to use."""
        # TODO: Implement logic based on task type, agent role, metadata etc.
        return f"default_{task_definition.get('type', 'task')}_prompt" # Placeholder
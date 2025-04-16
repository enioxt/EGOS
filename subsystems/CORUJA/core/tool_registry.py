"""
Manages the registration and execution of tools available to CORUJA agents.
"""
# Standard library imports
import importlib
import inspect
from typing import Dict, Any, Optional, Callable, List

# EGOS Subsystem Imports (Placeholders - uncomment/adjust paths when implemented)
from koios.logger import KoiosLogger
from subsystems.CORUJA.schemas.models import ToolDefinition

logger = KoiosLogger.get_logger("CORUJA.ToolRegistry")

class ToolRegistry:
    """
    Manages the definition, registration, and execution of tools
    that can be used by AI agents.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the ToolRegistry.

        Args:
            config: Configuration dictionary, potentially containing paths
                    to tool definition files or modules.
        """
        self.config = config
        self._tools: Dict[str, ToolDefinition] = {} # Store ToolDefinition objects
        self._tool_implementations: Dict[str, Callable] = {} # tool_name -> callable function/method
        logger.info("ToolRegistry initialized.")
        # TODO: Load tools from configuration or predefined locations

    def register_tool(self, tool_definition: ToolDefinition):
        """
        Registers a new tool based on its definition.

        This involves storing the definition and resolving the implementation reference.

        Args:
            tool_definition: A dictionary conforming to the ToolDefinition schema.

        Raises:
            ValueError: If the tool name is missing or already registered.
            ImportError: If the implementation reference cannot be resolved.
            AttributeError: If the referenced attribute is not found or not callable.
        """
        tool_name = tool_definition.name
        implementation_ref = tool_definition.implementation_ref

        if not tool_name:
            raise ValueError("Tool definition must include a 'name'.")
        if not implementation_ref:
            raise ValueError(f"Tool definition for '{tool_name}' must include an 'implementation_ref'.")

        if tool_name in self._tools:
            logger.warning(f"Tool '{tool_name}' is already registered. Overwriting.")
            # raise ValueError(f"Tool '{tool_name}' is already registered.")

        # Resolve implementation
        try:
            module_path, func_name = implementation_ref.rsplit('.', 1)
            module = importlib.import_module(module_path)
            implementation = getattr(module, func_name)
            if not callable(implementation):
                 raise AttributeError(f"Implementation '{implementation_ref}' is not callable.")
            # Check if it's async or sync? Store this info?
            # TODO: Validate input_schema format (JSON Schema)

            self._tools[tool_name] = tool_definition # Store the definition
            self._tool_implementations[tool_name] = implementation # Store the callable
            logger.info(f"Tool '{tool_name}' registered successfully from '{implementation_ref}'.")

        except ImportError:
            logger.error(f"Failed to import module for tool '{tool_name}': {module_path}")
            raise
        except AttributeError:
             logger.error(f"Failed to find function/method '{func_name}' in module '{module_path}' for tool '{tool_name}'.")
             raise
        except Exception as e:
            logger.error(f"Unexpected error registering tool '{tool_name}': {e}", exc_info=True)
            raise

    def load_tools_from_config(self, tool_configs: List[Dict[str, Any]]):
        """Loads multiple tool definitions from a list."""
        for tool_config in tool_configs:
            try:
                self.register_tool(tool_config)
            except (ValueError, ImportError, AttributeError) as e:
                logger.error(f"Skipping tool registration due to error: {e}")

    def get_tool_definition(self, tool_name: str) -> Optional[ToolDefinition]:
        """Retrieves the definition of a registered tool."""
        return self._tools.get(tool_name)

    def list_tools(self) -> List[ToolDefinition]:
        """Returns a list of definitions for all registered tools."""
        return list(self._tools.values())

    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Executes a registered tool with the given arguments.

        Args:
            tool_name: The name of the tool to execute.
            args: A dictionary of arguments for the tool, expected to conform
                  to the tool's input_schema.

        Returns:
            The result returned by the tool's implementation.

        Raises:
            ValueError: If the tool is not registered or if input validation fails.
            Exception: Any exception raised by the tool's implementation.
        """
        if tool_name not in self._tool_implementations:
            logger.error(f"Attempted to execute unregistered tool: '{tool_name}'")
            raise ValueError(f"Tool '{tool_name}' is not registered.")

        # TODO: Validate 'args' against the tool's input_schema using jsonschema or similar
        # try:
        #     jsonschema.validate(instance=args, schema=self._tools[tool_name]['input_schema'])
        # except jsonschema.ValidationError as e:
        #     logger.error(f"Input validation failed for tool '{tool_name}': {e}")
        #     raise ValueError(f"Invalid arguments for tool '{tool_name}': {e.message}") from e

        implementation = self._tool_implementations[tool_name]
        logger.info(f"Executing tool '{tool_name}' with args: {args}")

        try:
            # Check if the implementation is an async function
            if inspect.iscoroutinefunction(implementation):
                result = await implementation(**args)
            else:
                # Run synchronous function in a thread pool executor to avoid blocking asyncio loop?
                # For simplicity now, just call it directly. This might block!
                # Consider using asyncio.to_thread in Python 3.9+
                result = implementation(**args)

            logger.info(f"Tool '{tool_name}' executed successfully.")
            return result
        except Exception as e:
            logger.error(f"Error during execution of tool '{tool_name}': {e}", exc_info=True)
            # Re-raise the exception to be handled by the AgentRuntime/CrewManager
            raise

# Example Tool Implementation (conceptual, e.g., in subsystems/tools/example.py)
# def simple_tool(query: str) -> str:
#     """A simple example tool."""
#     return f"Processed query: {query}"

# Example Registration (conceptual)
# registry = ToolRegistry({})
# tool_def = {
#     "name": "simple_tool_example",
#     "description": "A basic tool for demonstration.",
#     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
#     "implementation_ref": "subsystems.tools.example.simple_tool"
# }
# registry.register_tool(tool_def)
# result = await registry.execute_tool("simple_tool_example", {"query": "hello"})
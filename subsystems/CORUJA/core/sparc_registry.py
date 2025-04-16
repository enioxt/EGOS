"""
Manages the state and lifecycle of SPARC tasks within the CORUJA subsystem.
"""
# Standard library imports
import asyncio
from typing import Dict, Any, Optional, List

# EGOS Subsystem Imports (Placeholders - uncomment/adjust paths when implemented)
from koios.logger import KoiosLogger
from subsystems.CORUJA.schemas.models import TaskDefinition, SPARCTaskState
# from subsystems.MYCELIUM.interfaces import MyceliumInterface # Example adjusted path

logger = KoiosLogger.get_logger("CORUJA.SPARCTaskRegistry")

class SPARCTaskRegistry:
    """
    Manages the lifecycle and state of SPARC tasks. Tracks dependencies
    and facilitates delegation via Mycelium.

    Note: Current implementation uses in-memory storage. Persistence
          (e.g., Redis, DB) might be needed for production/scalability.
    """

    def __init__(self, config: Dict[str, Any]): # TODO: Inject MyceliumInterface
        """
        Initializes the SPARCTaskRegistry.

        Args:
            config: Configuration dictionary for CORUJA.
            # TODO: Inject dependencies (MyceliumInterface, potentially CRONOS for persistence)
        """
        self.config = config
        # self.mycelium_interface: MyceliumInterface = mycelium_interface
        self._tasks: Dict[str, SPARCTaskState] = {} # Store SPARCTaskState objects
        self._task_locks: Dict[str, asyncio.Lock] = {} # To prevent race conditions on task state
        logger.info("SPARCTaskRegistry initialized (in-memory).")

    async def _get_lock(self, task_id: str) -> asyncio.Lock:
        """Gets or creates a lock for a specific task ID."""
        if task_id not in self._task_locks:
            self._task_locks[task_id] = asyncio.Lock()
        return self._task_locks[task_id]

    async def register_task(self, task_def: TaskDefinition) -> str:
        """
        Registers a new SPARC task from a validated TaskDefinition object.

        Args:
            task_def: The validated TaskDefinition object.

        Returns:
            The unique ID of the registered task.

        Raises:
            ValueError: If a task with the same ID already exists.
        """
        task_id = task_def.id
        if not task_id:
            raise ValueError("Task definition must include an 'id'.")

        lock = await self._get_lock(task_id)
        async with lock:
            if task_id in self._tasks:
                logger.warning(f"Task ID {task_id} already registered.")
                raise ValueError(f"Task ID {task_id} already exists.")

            # Create SPARCTaskState object
            initial_state = SPARCTaskState(
                task_id=task_id,
                status="pending",
                current_phase=task_def.type,
                result=None,
                error_message=None,
                history=[{"status": "registered", "timestamp": asyncio.get_event_loop().time()}] # Example history
            )
            self._tasks[task_id] = initial_state # Store SPARCTaskState
            logger.info(f"Task {task_id} registered with status 'pending'.")
            return task_id

    async def update_task_status(self, task_id: str, status: str, result: Optional[Any] = None, error_message: Optional[str] = None):
        """
        Updates the status and result/error of a task.

        Args:
            task_id: The ID of the task to update.
            status: The new status (e.g., 'running', 'completed', 'failed').
            result: The result data if the task completed successfully.
            error_message: The error message if the task failed.
        """
        lock = await self._get_lock(task_id)
        async with lock:
            if task_id not in self._tasks:
                logger.error(f"Attempted to update status for unknown task ID: {task_id}")
                return

            task_state = self._tasks[task_id]
            task_state['status'] = status
            task_state['result'] = result
            task_state['error_message'] = error_message
            task_state['history'].append({"status": status, "timestamp": asyncio.get_event_loop().time()}) # Example history

            logger.info(f"Task {task_id} status updated to '{status}'.")
            # TODO: Potentially publish status update via Mycelium (sparc.task.status.<task-id>)

    async def get_task_state(self, task_id: str) -> Optional[SPARCTaskState]:
        """
        Retrieves the current state object of a task.

        Args:
            task_id: The ID of the task.

        Returns:
            The SPARCTaskState object, or None if not found.
        """
        # No lock needed for read if assignment is atomic, but safer with it for complex states
        lock = await self._get_lock(task_id)
        async with lock:
            return self._tasks.get(task_id)

    async def get_dependencies(self, task_id: str) -> List[str]:
        """
        Retrieves the dependency task IDs for a given task.
        (Requires storing the original TaskDefinition or accessing it).
        """
        # TODO: Need access to the original TaskDefinition to get dependencies
        # This might involve storing it alongside the state or having a separate lookup
        task_state = await self.get_task_state(task_id)
        if task_state:
             # Assuming original TaskDefinition is somehow accessible or stored
             # return task_state.original_task_definition.dependencies
             logger.warning(f"Dependency retrieval logic for task {task_id} needs implementation (requires original TaskDefinition).")
             pass # Fallthrough to return empty list for now
        else:
             logger.warning(f"Cannot get dependencies for unknown task {task_id}")

        return []

    async def delegate_via_mycelium(self, task_id: str, target_subsystem: str, payload: Dict[str, Any]):
        """
        Delegates a task or sub-task to another subsystem via Mycelium.
        """
        topic = f"sparc.task.delegate.{target_subsystem}"
        logger.info(f"Delegating task {task_id} to {target_subsystem} via topic {topic} (Placeholder).")
        # TODO: Use self.mycelium_interface.publish(topic, payload)
        # TODO: Update task status to 'delegated'
        await self.update_task_status(task_id, status=f"delegated_to_{target_subsystem}")

    async def check_dependencies_complete(self, task_id: str) -> bool:
        """
        Checks if all dependencies for a given task are complete.
        """
        dependencies = await self.get_dependencies(task_id)
        dependencies = await self.get_dependencies(task_id) # Call the method to get deps
        if not dependencies:
            return True

        for dep_id in dependencies:
            dep_state = await self.get_task_state(dep_id)
            if not dep_state or dep_state.status != 'completed': # Access attribute directly
                logger.debug(f"Task {task_id} dependency {dep_id} not complete (Status: {dep_state.status if dep_state else 'Not Found'}).")
                return False
        return True
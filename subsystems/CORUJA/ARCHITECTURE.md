# CORUJA Subsystem Architecture

**Version:** 0.1
**Status:** Initial Draft
**Related Documents:**
*   [CORUJA README.md](README.md)
*   [CORUJA Schemas](schemas.py)
*   [MQP.md](../../docs/core_materials/MQP.md)
*   [SPARC Orchestration Rule](../../.cursor/rules/sparc_orchestration.mdc)
*   [Mycelium Interface (Concept)](../MYCELIUM/README.md)

## 1. Overview

This document outlines the internal architecture of the CORUJA subsystem, responsible for AI model interaction, prompt management, agent/crew orchestration, and SPARC task execution within the EGOS framework.

## 2. Core Components

Based on the analysis of requirements from the MQP, SPARC rule, and CORUJA README, the following core components are proposed:

1.  **`MyceliumAdapter`:** Handles all communication with the Mycelium (NATS) network. Subscribes to requests, publishes results/status updates, and manages SPARC delegation messages using standardized schemas defined in `schemas.py`.
2.  **`ConfigurationLoader`:** Securely loads and provides configuration (API keys, model settings, PDD paths, etc.).
3.  **`PromptManager`:** Loads, parses, caches, formats, and injects variables into Prompt Design Documents (PDDs).
4.  **`ModelInterface`:** Unified interface to various LLMs (recommendation: use LiteLLM). Implements model selection logic based on SPARC task type (Reasoning vs. Implementation).
5.  **`ToolRegistry`:** Manages definitions and secure access/invocation of `Tools` available to Agents.
6.  **`Agent`:** Executes a single `Task`. Defined by role, goal, backstory. Uses `ModelInterface` and `Tools`.
7.  **`Task` / `SparcTaskStep`:** Pydantic models defining units of work, inputs, outputs, requirements.
8.  **`CrewManager`:** Orchestrates multi-agent `Crews` for complex, non-SPARC tasks. Manages sequential execution, agent assignment, result synthesis, and ETHIK checks.
9.  **`SPARCTaskRegistry`:** Tracks the state, dependencies, and lifecycle of SPARC tasks across the system (potentially persistent).
10. **`SPARCTaskExecutor`:** Handles the execution logic for individual SPARC task steps assigned to CORUJA. Manages agent assignment for SPARC steps, delegates tasks to other subsystems (Boomerang), updates the registry, and publishes results.

## 3. Key Data Structures / Schemas

All data structures used for internal state and external communication (via Mycelium) are defined using Pydantic models in `schemas.py`. Key schemas include:

*   `ToolDefinition`, `AgentConfig`, `TaskDefinition`, `TaskOutput`
*   `CrewDefinition`, `CrewExecutionRequest`, `CrewExecutionResult`
*   `SPARCTaskBase`, `SPARCTaskCreationRequest`, `SPARCTaskStatusUpdate`, `SPARCTaskDelegation`, `SPARCTaskResult`
*   `MyceliumMessage` (Wrapper for all Mycelium payloads)

Refer to `schemas.py` for detailed field definitions.

## 4. Core Workflows

### 4.1 Workflow: Crew Execution Request (Non-SPARC)

1.  **Request In:** `MyceliumAdapter` receives `CrewExecutionRequest`.
2.  **Forward:** Request passed to `CrewManager`.
3.  **Load & Prepare:** `CrewManager` loads `CrewDefinition`, instantiates `Agents`.
4.  **Execute Sequentially:** `CrewManager` assigns `Tasks` to `Agents` one by one. Agents use `ModelInterface`/`Tools`.
5.  **Collect:** `CrewManager` gathers `TaskOutput`.
6.  **Synthesize & Respond:** `CrewManager` creates `CrewExecutionResult`, sends via `MyceliumAdapter`.

### 4.2 Workflow: SPARC Task Step Execution (Incoming Delegation)

1.  **Delegate In:** `MyceliumAdapter` receives `SPARCTaskDelegation` targeting CORUJA.
2.  **Forward:** Task details passed to `SPARCTaskExecutor`.
3.  **Acknowledge:** `SPARCTaskExecutor` sends `SPARCTaskStatusUpdate` (status='received').
4.  **Assign:** `SPARCTaskExecutor` determines required `Agent` role, instantiates `Agent`, creates `TaskDefinition`.
5.  **Execute:** `Agent` executes the task.
6.  **Result:** `Agent` returns `TaskOutput`.
7.  **Validate & Respond:** `SPARCTaskExecutor` creates `SPARCTaskResult`, sends via `MyceliumAdapter`.
8.  **Update Registry:** `SPARCTaskExecutor` updates `SPARCTaskRegistry`.

### 4.3 Workflow: SPARC Task Delegation (Outgoing)

1.  **Trigger:** `SPARCTaskExecutor` determines delegation is needed for the next step.
2.  **Prepare:** Creates new `SPARCTaskBase` for the delegated step, identifies target subsystem.
3.  **Construct Message:** Creates `SPARCTaskDelegation` message.
4.  **Publish:** Sends message via `MyceliumAdapter` to the target subsystem's topic.
5.  **Update Status:** Updates parent task status in `SPARCTaskRegistry` (e.g., 'delegated').

## 5. Integration Points

*   **Mycelium:** Primary communication channel.
*   **KOIOS:** For standards, PDDs, logging, configuration.
*   **ETHIK:** For ethical validation checks coordinated by `CrewManager`/`SPARCTaskExecutor`.
*   **Other Subsystems (NEXUS, HARMONY, etc.):** Receive delegated SPARC tasks from CORUJA and send results back.
*   **Configuration Sources:** Secure loading of keys/settings.
*   **External LLM APIs:** Accessed via `ModelInterface`.

## 6. Future Considerations

*   Advanced agent memory and planning.
*   Hierarchical crew processes.
*   Asynchronous task execution.
*   Integration with monitoring/observability platforms.
*   More sophisticated error handling and retry logic.
*   Persistent storage options for `SPARCTaskRegistry`.

---
✧༺❀༻∞ EGOS ∞༺❀༻✧

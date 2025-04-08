---
metadata:
  author: EGOS AI Assistant (Eva & Guarani)
  backup_required: true
  category: SUBSYSTEM_DOCUMENTATION
  description: Overview of the CORUJA subsystem, responsible for AI model interaction, prompt management, and orchestration within EGOS.
  documentation_quality: 0.3 # Updated with SPARC integration
  encoding: utf-8
  ethical_validation: false # Subsystem overview
  last_updated: '2025-04-08' # Updated date
  related_files:
    - docs/MQP.md
    - docs/STRATEGY.md
    - docs/templates/PDD_Template.md
    - subsystems/KOIOS/README.md
    - subsystems/ETHIK/README.md
    - subsystems/MYCELIUM/README.md # Assuming future interaction
    - .cursor/rules/sparc_orchestration.mdc # SPARC integration rule
  required: true # Core subsystem README
  review_status: draft
  security_level: 0.5 # Public documentation
  subsystem: CORUJA
  type: documentation
  version: '0.2' # Updated with SPARC integration
  windows_compatibility: true
---

# 🦉 CORUJA Subsystem - AI Orchestration

**Version:** 0.2 (SPARC Integration)
**Status:** In Development

## 1. Overview

CORUJA (Cognitive Orchestration, Reasoning, Understanding, & Action) is the central subsystem within EGOS responsible for managing all interactions with external AI models (LLMs). It acts as the intelligent layer that selects prompts, interacts with models, potentially optimizes requests, and orchestrates AI-driven tasks based on requests from other subsystems or the user via the EGOS AI assistant.

Its primary goal is to provide a standardized, efficient, and ethically-aware interface to diverse AI capabilities, leveraging documented prompts (PDDs) and integrating ETHIK checks.

## 2. Core Responsibilities (Phase 1 Focus - Multi-Agent Enhanced with SPARC)

*   **Model Interaction:** Provide a standardized interface (`ModelInterface`) to communicate with various supported LLMs. Abstract away model-specific API details.
*   **Prompt Management:** Retrieve, format, and utilize prompts defined in Prompt Design Documents (PDDs) managed according to KOIOS standards. Inject context/variables into prompts before sending them to models. **Agents will leverage this for their specific roles and tasks.**
*   **Agent & Crew Orchestration:** **Define, manage, and orchestrate crews of specialized AI Agents (e.g., Researcher, Writer, Coder, Reviewer) to collaboratively execute complex tasks decomposed into specific steps (`Tasks`).**
*   **Task Management:** Define and manage individual `Tasks`, including their description, expected output, assigned agent (role), and required tools.
*   **SPARC Task Delegation:** Implement the Boomerang Tasks pattern for complex problem solving using the SPARC methodology (Specification, Pseudocode, Architecture, Refinement, Completion).
*   **Tool Management:** Define and provide access to a registry of available `Tools` (e.g., web search, file access, specific subsystem functions exposed as tools) that agents can utilize to accomplish tasks.
*   **Response Handling & Synthesis:** Receive responses from individual agent task executions, potentially synthesize results from multiple agents/tasks within a crew, and format the final output.
*   **Integration with ETHIK:** Facilitate ethical checks on agent prompts, actions (tool usage), and final outputs, based on rules defined by ETHIK.
*   **Integration with KOIOS:** Adhere to KOIOS logging standards for all agent interactions, task executions, and crew operations. Utilize KOIOS mechanisms for PDD retrieval and potentially Tool definitions.

## 3. Planned Components (Phase 1 - Multi-Agent Architecture with SPARC)

*   **`Agent`:**
    *   Represents an autonomous unit with a defined `role` (e.g., "Software Documentation Writer"), `goal`, `backstory` (context), and assigned LLM configuration.
    *   Utilizes the `ModelInterface` to interact with its designated LLM.
    *   Can be equipped with specific `Tools` from the `ToolRegistry`, **including tools for secure interaction with external APIs/data sources (potentially leveraging oracle network patterns).**
    *   Executes assigned `Tasks`. May have capability for basic planning or tool selection based on task description (Phase 1 focus is likely direct execution).
    *   **Future Enhancements:** Explore advanced memory management (short/long-term, entity, contextual) and agent-level planning capabilities in later phases.
    *   **Privacy Consideration: Interactions involving sensitive data should ideally leverage appropriate Privacy-Preserving Computation techniques (e.g., Compute-to-Data model for accessing external private data, or processing within secure enclaves if applicable) coordinated by the `CrewManager` and verified by ETHIK.**
*   **`Task`:**
    *   Defines a specific unit of work with a clear `description`, `expected_output` format/criteria, **potentially supporting asynchronous execution and context-based dependencies.**
    *   Assigned to an `Agent` (or agent role).
    *   May specify required `Tools`.
    *   **Future Enhancements:** Structured output objects (like `TaskOutput`) and validation guardrails.
*   **`SPARCTask`:**
    *   Specialized task representation implementing the SPARC methodology workflow.
    *   Supports structured task delegation across subsystems (Boomerang Tasks).
    *   Includes clear acceptance criteria, dependencies, and standardized inputs/outputs.
    *   Integrated with Mycelium for cross-subsystem communication.
*   **`SPARCTaskRegistry`:**
    *   Manages SPARC tasks throughout their lifecycle.
    *   Tracks task status, parent-child relationships, and dependencies.
    *   Enables task delegation and result retrieval between subsystems.
*   **`Tool`:**
    *   Represents a specific capability an `Agent` can use (e.g., `web_search`, `read_file`, `run_code_analysis`, `validate_ethics`).
    *   **May involve secure off-chain computation or interaction with external data sources via trust-minimized mechanisms.**
    *   Defined interface for execution (`execute(input)`).
    *   Managed by `ToolRegistry`.
    *   **Privacy Consideration: Tools accessing external data or performing sensitive computations should be designed with PPC principles in mind.**
*   **`ToolRegistry`:**
    *   Manages the definition and availability of `Tools`, **including those requiring secure external access or off-chain computation.**
    *   Provides a mechanism for `Agents` to access and utilize tools.
*   **`CrewManager` (Replaces BasicOrchestrator):**
    *   Responsible for defining a `Crew` (a collection of `Agents` and their `Tasks`).
    *   Instantiates `Agents` based on crew definition.
    *   Assigns `Tasks` to appropriate `Agents`.
    *   Manages the execution flow of tasks within the crew. **Phase 1 likely sequential, but future phases could incorporate hierarchical processes (with manager agent/LLM) or event-driven Flows.**
    *   **Future Enhancements:** Explore agent-to-agent task delegation within hierarchical processes.
    *   Collects results from `Tasks` and synthesizes the final output.
    *   Coordinates ETHIK checks **(including checks related to PPC usage)**.
    *   Interfaces with external requestors (e.g., MVP Backend, EGOS Assistant) **or potentially triggered by automated systems (inspired by Chainlink Automation).**
*   **`PromptManager`:** (Remains essential)
    *   Loads, parses, and retrieves PDDs for agent roles, task instructions, etc.
    *   Handles variable injection. Used by `CrewManager` and potentially `Agents`.
*   **`ModelInterface`:** (Remains essential)
    *   Abstract interface and concrete implementations for LLM interaction. Used by `Agents`.
    *   **Consider using libraries like LiteLLM for broad compatibility - *Implementation Note***
    *   **SPARC Enhancement:** Model selection based on task type (reasoning vs implementation).
*   **`ConfigurationLoader`:** (Remains essential)
    *   Loads API keys, model configs, tool configs, etc., securely.

## 4. SPARC Integration

CORUJA now implements the SPARC methodology (Specification, Pseudocode, Architecture, Refinement, Completion) for complex problem solving through structured task delegation. Key integration points include:

### 4.1 Model Selection Based on Task Type

Different AI models excel at different task types. CORUJA will leverage this through specialized model selection:

* **Reasoning Tasks** (Specification, Architecture, Planning):
  * Prefer models optimized for reasoning (Claude 3 Opus/Sonnet Thinking, GPT-4o, DeepSeek)
  * Used in early SPARC phases (Specification, Architecture)

* **Implementation Tasks** (Coding, Documentation, Testing):
  * Prefer models optimized for instruction following (Claude 3 Sonnet, GPT-4o, Mistral)
  * Used in later SPARC phases (Code, Test, Documentation)

### 4.2 Task Delegation Pattern (Boomerang Tasks)

SPARC tasks follow a structured delegation pattern:
* Clear task definition with acceptance criteria
* Context isolation between task stages
* Explicit handoffs between subsystems
* Standardized communication via Mycelium
* Task tracking via the `SPARCTaskRegistry`

### 4.3 Communication via Mycelium

SPARC tasks use standardized Mycelium topic patterns:
* Task Creation: `sparc.task.create.<subsystem>`
* Task Status Updates: `sparc.task.status.<task-id>`
* Task Completion: `sparc.task.complete.<task-id>`
* Task Delegation: `sparc.task.delegate.<target-subsystem>`
* Task Results: `sparc.task.results.<task-id>`

## 5. Integration Points (Phase 1 - Multi-Agent Context with SPARC)

*   **Consumers:**
    *   MVP Backend (Content Aggregator): Will **request the `CrewManager` to execute specific predefined crews** (e.g., a 'Summarization Crew') with necessary input data.
    *   EGOS AI Assistant (Conceptual): Will leverage the `CrewManager` to dynamically assemble and execute crews to fulfill complex user requests.
*   **Providers/Dependencies:**
    *   **KOIOS:** Relies on KOIOS for PDD format, logging (`KoiosLogger`), potentially Tool definitions/discovery, and configuration standards.
    *   **ETHIK:** `CrewManager` and potentially `Agents` call ETHIK to perform configured ethical checks on prompts, tool usage, task outputs, and final crew results.
    *   **ATLAS/NEXUS:** Provide specifications and architecture for SPARC tasks that CORUJA implements.
    *   **HARMONY:** Receives test tasks from CORUJA and provides validation results.
    *   **External LLM APIs:** `ModelInterface` implementations connect directly to configured AI model provider APIs. **Leverage libraries like LiteLLM for broader support**.
    *   **Tool Implementations:** `Tools` in the `ToolRegistry` may call other EGOS subsystems (e.g., NEXUS for analysis, CRONOS for file access via defined interfaces) or external APIs/libraries.
    *   **Configuration Source:** `ConfigurationLoader` reads API keys and settings.
    *   **Mycelium:** `CrewManager` receives crew execution requests and publishes results via Mycelium. SPARC tasks communicate via standardized Mycelium topics.
    *   **Monitoring/Observability (Future): Integrate with platforms (e.g., Langfuse, AgentOps) for agent/crew performance tracking.**

## 6. Configuration

*   Requires API keys for target LLM providers, stored securely (e.g., environment variables, `config/api_keys.json` accessed securely).
*   Configuration for default models, parameters (temperature, max tokens), and potentially ETHIK check levels.
*   Path to PDD storage location (initially likely a specific directory within `docs/prompts/`).
*   Model selection configurations for different SPARC task types.

---

✧༺❀༻∞ EGOS ∞༺❀༻✧

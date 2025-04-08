# 🛣️ CORUJA Subsystem Roadmap

**Last Update:** April 8, 2025

This document outlines the detailed tasks and milestones specifically for the **CORUJA** subsystem, complementing the high-level overview in the main project `../../ROADMAP.md`.

---

## 🎯 Phase 2 Focus: Foundation & Advanced Orchestration with SPARC

### Initial Setup (Completed Tasks - Ref Main Roadmap Phase 2a)

* Implement `PromptManager` [DONE]
* Implement `Basic ModelInterface` (ABC) [DONE]
* Implement `GeminiModelInterface` [DONE]
* Implement initial `BasicOrchestrator` [DONE]
* Define `ETHIK` Interface & Dummy Implementation [DONE]
* Integrate `ETHIK` Interface into `BasicOrchestrator` [DONE]
* Integrate `KoiosLogger` into `BasicOrchestrator` [DONE]
* Define Unit Tests for core components [DONE]

### SPARC Methodology Integration (Current - Ref Main Roadmap Phase 2b)

* **Task COR-SPARC-01: Implement SPARC Task Registry**
  * **Relates to:** Main Roadmap Task `SPARC-01`
  * **Goal:** Create a task registry for managing SPARC methodology tasks
  * **Sub-Tasks:**
    * [x] Define `SPARCTask` class with appropriate fields (ID, type, status, etc.)
    * [x] Implement `SPARCTaskRegistry` for managing task creation, status, and retrieval
    * [ ] Add unit tests for the task registry functionality
    * [ ] Integrate with KOIOS logging
  * **Status:** In Progress
  * **Priority:** HIGH

* **Task COR-SPARC-02: Implement SPARC Mycelium Message Formats**
  * **Relates to:** Main Roadmap Task `SPARC-02`
  * **Goal:** Define standardized message formats for SPARC communication via Mycelium
  * **Sub-Tasks:**
    * [x] Create message schema definitions for SPARC tasks
    * [x] Implement factory methods for common message types
    * [x] Define topic naming conventions
    * [ ] Add unit tests for message creation and topic generation
  * **Status:** In Progress
  * **Priority:** HIGH

* **Task COR-SPARC-03: Implement Model Selection Based on Task Type**
  * **Relates to:** Main Roadmap Task `SPARC-03`
  * **Goal:** Enhance the model interface to select appropriate models for different SPARC task types
  * **Sub-Tasks:**
    * [ ] Update model configuration to categorize models by strengths (reasoning vs. implementation)
    * [ ] Implement a model selector based on task type
    * [ ] Create PDDs optimized for different SPARC phases
    * [ ] Add unit tests for model selection logic
  * **Status:** Planned
  * **Priority:** MEDIUM

* **Task COR-SPARC-04: Integrate SPARC with CrewManager**
  * **Relates to:** Main Roadmap Task `SPARC-04`
  * **Goal:** Enable CrewManager to use SPARC methodology for complex tasks
  * **Sub-Tasks:**
    * [ ] Define interfaces between CrewManager and SPARCTaskRegistry
    * [ ] Implement SPARC workflow patterns in CrewManager
    * [ ] Create specialized crews for different SPARC phases
    * [ ] Add integration tests for SPARC workflows
  * **Status:** Planned
  * **Priority:** MEDIUM

* **Task COR-SPARC-05: Implement Boomerang Task Handlers**
  * **Relates to:** Main Roadmap Task `SPARC-05`
  * **Goal:** Create handlers for sending and receiving Boomerang Tasks via Mycelium
  * **Sub-Tasks:**
    * [ ] Implement task delegation mechanisms
    * [ ] Create context isolation utilities
    * [ ] Implement result synthesis for completed tasks
    * [ ] Add integration tests with mocked Mycelium
  * **Status:** Planned
  * **Priority:** HIGH

### Advanced Orchestration Capabilities (Ongoing - Ref Main Roadmap Phase 2)

* **Task COR-ADV-01: Design Complex PDD Handling**
  * **Relates to:** Main Roadmap Task `COR-ADV-01`
  * **Goal:** Define how `BasicOrchestrator` identifies & routes PDDs requiring specialized handlers (non-standard LLM calls).
  * **Sub-Tasks:**
    * [ ] Define PDD metadata field(s) (e.g., `handler_type`, `handler_reference`) for signaling specialized handling. *(Decision: Added `handler_type`, `handler_reference`)*.
    * [ ] Design the routing logic within `BasicOrchestrator.process_request` to check these fields.
    * [ ] Determine how pre/post ETHIK checks should wrap specialized handler calls.
    * [ ] Document the design choices in `subsystems/CORUJA/README.md`.
  * **Status:** Planned
  * **Priority:** HIGH

* **Task COR-ADV-02: POC - Zendesk Ticket Analysis Handler**
  * **Relates to:** Main Roadmap Task `COR-ADV-02`
  * **Goal:** Implement the structural skeleton for handling the `coruja_zendesk_ticket_analysis_v1` PDD using a specialized handler, simulating a CrewAI pattern.
  * **Sub-Tasks:**
    * [x] Create PDD file `docs/prompts/coruja_zendesk_ticket_analysis_v1.pdd` with appropriate metadata. *(File created)*
    * [x] Create handler directory `subsystems/CORUJA/handlers/`. *(Directory created)*
    * [x] Create placeholder handler `subsystems/CORUJA/handlers/zendesk_analyzer_handler.py` with simulated logic and `ModelResponse` wrapping. *(File created)*
    * [ ] Add conceptual routing logic comment to `BasicOrchestrator.process_request` indicating where handler invocation would occur. *(Conceptual logic added)*
    * [ ] Implement the minimal changes in `BasicOrchestrator` to *actually* route based on `handler_type` (even if handler loading isn't complete).
    * [ ] Write basic integration test confirming a request with the Zendesk PDD attempts to route to the specialized path (mocking the handler itself).
  * **Status:** In Progress
  * **Priority:** HIGH

* **Task COR-ADV-03: Design Handler Management Strategy**
  * **Relates to:** Main Roadmap Task `COR-ADV-03`
  * **Goal:** Define how specialized handlers (like the Zendesk one) are registered, discovered, and loaded by the `BasicOrchestrator`.
  * **Sub-Tasks:**
    * [ ] Evaluate strategies (e.g., configuration file mapping `handler_reference` to modules/classes, naming conventions, plugin system).
    * [ ] Define the interface required for a class to be considered a specialized handler (e.g., must have an async `process` method).
    * [ ] Document the chosen strategy.
  * **Status:** Planned
  * **Priority:** MEDIUM

---

## Future Phases (Q3-Q4 2025)

* **SPARC Integration Phase 3**
  * Implement autonomous SPARC workflows (self-organizing)
  * Add advanced task dependency management
  * Create specialized PDDs for each SPARC phase
  * Implement context refinement between phases
  * Create dashboards for SPARC task monitoring

* **Advanced Agent Capabilities**
  * Implement full CrewAI logic within specialized handlers
  * Develop state management for multi-turn interactions
  * Integrate with Mycelium for event-driven orchestration
  * Implement advanced monitoring/observability hooks

---

✧༺❀༻∞ EGOS ∞༺❀༻✧

* **Task: CORUJA - Implement Gemini Interface** (`subsystems/CORUJA/models/gemini_interface.py`) - **Completed**
  * [x] Create `GeminiModelInterface` class inheriting from `AIModelInterface`
  * [x] Implement `__init__` to configure client (handle API key, potential `ImportError`)
  * [x] Implement `generate_response` using `google-generativeai` client and internal helpers/exceptions
  * [x] Implement `count_tokens` using `google-generativeai` client and internal helpers/exceptions
  * [x] Add basic unit tests

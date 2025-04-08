# 🧬 KOIOS Subsystem Roadmap

**Last Update:** April 8, 2025

This document outlines the detailed tasks and milestones specifically for the **KOIOS** subsystem (Standardization, Logging, Search, Documentation), complementing the high-level overview in the main project `../../ROADMAP.md`.

---

## 🎯 Phase 2 Focus: Foundational Logging & Standards Refinement

### Initial Setup (Completed Tasks - Ref Main Roadmap Phase 2a)

* [X] Define basic `KoiosLogger` interface and implementation
* [X] Integrate `KoiosLogger` into `BasicOrchestrator`
* [X] Establish initial Coding Standards (Python, Docs, Commits, etc.)
* [X] **KOI-DOC-01:** Create Troubleshooting Guide - Document common issues (dependencies, imports, schemas, mocks) and resolution steps in `docs/troubleshooting_guide.md`.
* [X] **KOI-DOC-02:** Create Lessons Learned Rule - Define a guideline (`lessons_learned.mdc`) for summarizing key technical takeaways.

### SPARC Methodology Integration (Current - Ref Main Roadmap Phase 2b)

* **Task KOI-SPARC-01: Create SPARC Orchestration Rule**
  * **Relates to:** Main Roadmap Task `SPARC-01`
  * **Goal:** Define a KOIOS standard for implementing SPARC methodology within EGOS
  * **Sub-Tasks:**
    * [x] Create `.cursor/rules/sparc_orchestration.mdc` defining SPARC principles
    * [x] Document subsystem-mode mapping (EGOS to SPARC)
    * [x] Define task delegation patterns and format
    * [x] Document file structure and module best practices
    * [x] Define model selection guidelines based on task type
  * **Status:** Completed
  * **Priority:** HIGH

* **Task KOI-SPARC-02: SPARC Task Schema Definition**
  * **Relates to:** Main Roadmap Task `SPARC-02`
  * **Goal:** Create schema definitions for SPARC task validation
  * **Sub-Tasks:**
    * [ ] Define JSON schema for SPARC tasks
    * [ ] Create validation rules for task properties
    * [ ] Implement schema validation utilities
    * [ ] Create documentation for schema usage
  * **Status:** Planned
  * **Priority:** MEDIUM

* **Task KOI-SPARC-03: SPARC Message Logging**
  * **Relates to:** Main Roadmap Task `SPARC-03`
  * **Goal:** Enhance KoiosLogger to handle SPARC task lifecycle events
  * **Sub-Tasks:**
    * [ ] Define logging format for SPARC task events
    * [ ] Implement specialized logging for task transitions
    * [ ] Create visualization utilities for task graphs
    * [ ] Document logging patterns for SPARC workflows
  * **Status:** Planned
  * **Priority:** MEDIUM

### Foundational Capabilities (Ongoing - Ref Main Roadmap Phase 2)

* **Task KOI-LOG-01: Implement Structured Logging**
  * **Relates to:** Main Roadmap Task `KOI-LOG-01`
  * **Goal:** Enhance `KoiosLogger` to output logs in a structured format (JSON) for easier parsing and analysis.
  * **Sub-Tasks:**
    * [x] Choose or implement a JSON formatter for the `logging` module. *(Implemented `JsonFormatter`)*
    * [x] Update `KoiosLogger._initialize` (or configuration loading) to use the JSON formatter. *(Added `_use_json_logging` flag and logic)*
    * [ ] Define the standard fields expected in the JSON log structure (e.g., timestamp, level, name, message, subsystem, task_id, context_data).
    * [ ] Ensure exception information (`exc_info`) is properly captured in the structured format. *(Basic implementation in `JsonFormatter`)*
  * **Status:** In Progress
  * **Priority:** HIGH

* **Task KOI-LOG-02: Implement File Logging**
  * **Relates to:** Main Roadmap Task `KOI-LOG-02`
  * **Goal:** Add capability for `KoiosLogger` to log to files (e.g., rotating files) in addition to the console.
  * **Sub-Tasks:**
    * [ ] Add file handler configuration (path, rotation settings) - likely loaded from a central config. *(Constants defined, but not external config loading)*
    * [x] Implement file handler setup (e.g., `TimedRotatingFileHandler`) within `KoiosLogger._initialize`. *(Added `TimedRotatingFileHandler` logic)*
    * [x] Ensure file handler uses the same formatter (e.g., JSON) as the console handler. *(Formatter is shared)*
  * **Status:** In Progress
  * **Priority:** MEDIUM

* **Task KOI-LOG-03: Research Mycelium Logging Integration**
  * **Relates to:** Main Roadmap Task `KOI-LOG-03`
  * **Goal:** Investigate feasibility and design for emitting critical log events onto the Mycelium network.
  * **Sub-Tasks:**
    * [ ] Define which log levels/events warrant Mycelium broadcast (e.g., ERROR, CRITICAL).
    * [ ] Define the Mycelium topic structure (e.g., `log.<subsystem>.<level>`).
    * [ ] Define the message payload format for log events.
    * [ ] Design a custom logging handler (`MyceliumHandler`) that publishes messages.
    * [ ] Determine how the handler gets configured/added to `KoiosLogger`.
  * **Status:** Planned
  * **Priority:** LOW

* **Task KOI-STD-01: Refine & Automate Standards**
  * **Relates to:** Ongoing KOIOS mandate (ref `docs/MQP.md`, `subsystems/KOIOS/docs/STANDARDS.md`)
  * **Goal:** Improve enforcement and usability of coding/documentation standards.
  * **Sub-Tasks:**
    * [X] Implement `ruff` for linting/formatting.
    * [X] Configure pre-commit hooks.
    * [X] Standardize directory structures (`core`, `tests`, `services`, etc.).
    * [X] Document core standards (Python style, commits, errors, etc.).
    * [X] Standardize rule files (`.cursor/rules/*.mdc`).
    * [ ] Refine subsystem interaction rules (beyond Mycelium-first).
  * **Status:** In Progress (Core Done, Refinement Ongoing)

* **Task KOI-DOC-01: Create Troubleshooting Guide**
  * [ ] Create `docs/troubleshooting_guide.md`.
  * [ ] Document steps for dependency issues.
  * [ ] Document steps for import path/`__init__.py` issues.
  * [ ] Document steps for Pydantic schema validation errors.
  * [ ] Document steps for test mocking/patching issues.
  * [ ] Document steps for resolving common linter errors.
  * **Status:** Planned

---

## Future Phases (Q3-Q4 2025)

* **SPARC Documentation & Monitoring**
  * Develop SPARC task visualization dashboard
  * Create automated documentation generation from completed tasks
  * Implement SPARC workflow metrics and analytics
  * Build SPARC project templates and examples

* **Knowledge Management**
  * Implement knowledge base search capabilities
  * Develop metadata management services
  * Build centralized configuration management
  * Integrate with potential external monitoring/tracing tools (e.g., OpenTelemetry, Comet Opik)

---

✧༺❀༻∞ EGOS ∞༺❀༻✧

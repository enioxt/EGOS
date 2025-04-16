# EGOS AI Collaboration Governance v1.1

**Status:** Active
**Date:** 2024-07-26 # Updated Date

**Purpose:** This document defines the operational pipeline, roles, responsibilities, workflow guidelines, and handover processes for effective Human-AI and AI-AI collaboration within the EGOS project, particularly when using multiple AI agents within the Cursor IDE environment.

## Core Principles

*   **Clarity:** Instructions and task delegations must be explicit and unambiguous.
*   **Consistency:** Adherence to KOIOS standards, Conventional Commits, and defined workflows is mandatory.
*   **Context Preservation:** Maintaining context across sessions and between agents is critical (See Handover Standard).
*   **Oversight:** Human review and/or Orchestrator AI oversight are necessary for quality and alignment.

## Defined Roles (Example)

*   **Orchestrator (e.g., Gemini 2.5 Pro):** Responsible for strategic planning, complex analysis, code generation requiring deep context, reviewing significant changes, and maintaining overall project coherence.
*   **Task Executor (e.g., Quasar-Alpha via OpenRouter):** Responsible for executing simpler, well-defined tasks as delegated by the user or orchestrator (e.g., creating placeholder files, basic formatting, running linters, simple i18n key additions).

## Workflow Guidelines

1.  **Clear Task Delegation:**
    *   Explicitly assign tasks using comments in planning documents (`ROADMAP.md`, `DEVELOPMENT_PLAN.md`) or the `CURRENT_TASKS.md` file (e.g., `Assignee: Gemini`, `Assignee: Quasar`).
    *   Ensure tasks assigned to the Task Executor are well-defined, specific, and have minimal ambiguity.

2.  **Single Source of Truth:**
    *   Core planning documents (`ROADMAP.md`, `DEVELOPMENT_PLAN.md`, `DESIGN_GUIDE.md`) remain the authoritative source.
    *   All significant changes must be reflected back into these documents by the responsible agent (usually the Orchestrator after review).

3.  **Communication via Git:**
    *   Adhere strictly to Conventional Commits ([commit_messages.mdc](mdc:.cursor/rules/commit_messages.mdc)). Commit messages should clearly indicate the work done.
    *   **Before starting work:** Perform a `git pull` (or IDE equivalent) to ensure the local environment is up-to-date.
    *   Commit work frequently in small, logical chunks.

4.  **Review Process:**
    *   Work completed by the Task Executor, especially code or documentation changes, should ideally be reviewed (by Orchestrator or User) before merging into main branches or relying upon for subsequent tasks.
    *   Pull Requests can be used for formal review if needed.

5.  **Focus Areas / Conflict Avoidance:**
    *   Avoid assigning the *exact same file and task* to both agents simultaneously.
    *   Prefer assigning distinct files, features, or clearly separated sections of a file.
    *   If concurrent work on the same file is necessary, ensure tasks target different, non-overlapping line ranges.

6.  **Orchestrator Oversight:**
    *   The Orchestrator agent (Gemini) is responsible for maintaining overall consistency and ensuring work aligns with the strategic plan and design guidelines.

## Mandatory Handover Standard

*   Before finishing a work session or passing a task between agents or between AI and human, the **outgoing agent MUST generate a complete and detailed Handover Summary** following *all* requirements specified in the **[AI Handover Standard](mdc:.cursor/rules/ai_handover_standard.mdc)**.
*   This includes using structured data formats (JSON/YAML) where recommended and providing specific details (commit SHAs, rationales, verification steps).
*   Failure to provide a compliant handover can disrupt the workflow, lead to context loss, and result in duplicated effort or errors.

---
*These guidelines aim to foster efficient, transparent, and reliable collaboration while minimizing conflicts and ensuring project integrity.*

✧༺❀༻∞ EGOS ∞༺❀༻✧ 

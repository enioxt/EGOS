# EGOS Multi-Agent Workflow Guidelines (Cursor IDE)

**Date:** 2025-04-10

**Purpose:** To define guidelines for coordinating work between multiple AI agents (e.g., Gemini 2.5 Pro as Orchestrator, Quasar-Alpha as Task Executor) within the Cursor IDE environment for the EGOS project.

**Roles:**

* **Orchestrator (Gemini 2.5 Pro):** Responsible for strategic planning, complex analysis, code generation requiring deep context, reviewing significant changes, and maintaining overall project coherence.
* **Task Executor (e.g., Quasar-Alpha via OpenRouter):** Responsible for executing simpler, well-defined tasks as delegated by the user or orchestrator (e.g., creating placeholder files, basic formatting, running linters, simple i18n key additions).

**Guidelines:**

1. **Clear Task Delegation:**
    * Explicitly assign tasks using comments in planning documents (`ROADMAP.md`, `DEVELOPMENT_PLAN.md`) or the `CURRENT_TASKS.md` file (e.g., `Assignee: Gemini`, `Assignee: Quasar`).
    * Ensure tasks assigned to the Task Executor are well-defined, specific, and have minimal ambiguity.

2. **Single Source of Truth:**
    * Core planning documents (`ROADMAP.md`, `DEVELOPMENT_PLAN.md`, `DESIGN_GUIDE.md`) remain the authoritative source.
    * All significant changes must be reflected back into these documents by the responsible agent (usually the Orchestrator after review).

3. **Communication via Git:**
    * Adhere strictly to Conventional Commits (`commit_messages.mdc`). Commit messages should clearly indicate the work done.
    * **Before starting work:** Perform a `git pull` (or IDE equivalent) to ensure the local environment is up-to-date.
    * Commit work frequently in small, logical chunks.

4. **Review Process:**
    * Work completed by the Task Executor, especially code or documentation changes, should ideally be reviewed (by Orchestrator or User) before merging into main branches or relying upon for subsequent tasks.
    * Pull Requests can be used for formal review if needed.

5. **Focus Areas / Conflict Avoidance:**
    * Avoid assigning the *exact same file and task* to both agents simultaneously.
    * Prefer assigning distinct files, features, or clearly separated sections of a file.
    * If concurrent work on the same file is necessary, ensure tasks target different, non-overlapping line ranges.

6. **Orchestrator Oversight:**
    * The Orchestrator agent (Gemini) is responsible for maintaining overall consistency and ensuring work aligns with the strategic plan and design guidelines.

---
*These guidelines aim to foster efficient collaboration while minimizing conflicts and ensuring project integrity.*

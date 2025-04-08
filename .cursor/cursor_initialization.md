# EVA & GUARANI - Cursor Initialization v8.1

**Last Updated:** 2025-04-04

## Unified Quantum Structure

This document details the initialization process for the EVA & GUARANI (EGOS) system in its current unified state. The system comprises interconnected subsystems designed for optimal human-AI interaction and development.

**Core Subsystems:** ATLAS, CORUJA, CRONOS, ETHIK, HARMONY, KOIOS, MYCELIUM, NEXUS, TRANSLATOR.

## Focus on AI Integration

EGOS is fundamentally designed to enhance communication and integration between humans and AI systems:

- **Optimized Communication**: Reduces noise in human-AI interactions.
- **Context Preservation**: Maintains conversational continuity across AI sessions (CRONOS target).
- **Knowledge Structuring**: Information architecture optimized for AI processing.
- **Command Standards**: Simplified interaction protocols for AI understanding.
- **AI-Readable Design**: Directory structure and documentation for easy AI navigation.
- **Minimal Input Principles**: Maximizes AI comprehension from concise prompts.
- **Cross-Model Integration**: Framework for consistent interaction between different AI models.

## Current Cursor Integration

- **Sequential Thinking MCP**: Available for complex problem-solving.
- **Perplexity MCP**: Available for web search.
- **BIOS-Q Integration**: Basic structure established.
- **CRONOS Integration**: Optimized backup system implemented.
- **Mycelium Network**: Core Python implementation (asyncio-based) complete and tested.

## New Chat Session Initialization & Diagnostics

To ensure context continuity (CRONOS principle) when starting a new chat session:

1. **User Provides Context:** The user will initiate the new chat by pasting a summary of the current project state, including project goals, recent tasks, roadmap status, and any relevant "bridge" information from the previous session.
2. **AI Acknowledges & Diagnoses:** Upon receiving this initial context summary, the AI agent (e.g., EVA & GUARANI) must:
    - Acknowledge receipt and confirm understanding of the provided context. The AI's initial acknowledgement should explicitly state that the received summary format triggered the diagnostic procedure.
    - Perform internal diagnostic checks:
        - Verify understanding of the core project (EGOS, MQP v8.1, KOIOS).
        - Confirm understanding of the current `ROADMAP.md` status.
        - Attempt to access key project files (e.g., `ROADMAP.md`, relevant subsystem files if mentioned) to ensure workspace access.
        - Identify any ambiguities or missing information in the provided context.
    - Generate a structured diagnostic report (timestamp, checks performed, success/failure, overall assessment).
3. **AI Reports & Logs:**
    - Provide a concise summary of the diagnostic results directly in the chat.
    - Propose appending the full, structured diagnostic report to the `logs/initialization_diagnostics.log` file for tracking purposes. The user must approve this file modification.
4. **Proceed:** Once the diagnostic is complete and logged, proceed with the user's next requested task.

This process helps verify that the AI has correctly assimilated the context before continuing development work.

## System Initialization and Maintenance

System integrity and state preservation are managed by the CRONOS subsystem. For reliable operation, follow these guidelines:

1. **Consult CRONOS Documentation:** Refer to the CRONOS subsystem implementation and documentation (target location: `subsystems/CRONOS/docs/procedures.md` - *to be created/updated*) for the standard procedures for:
    - Creating clean system backups.
    - Verifying system integrity.
    - Restoring system state.
2. **Prioritize Standard Procedures:** Avoid using outdated scripts or commands found in backups or logs. Use current, documented CRONOS procedures.
3. **Document Procedures (CRONOS Task):** A key task for CRONOS development is to clearly document these standard operating procedures.

*(Previous initialization information referenced scripts like `create_clean_backup.py` and `verify_cleanup.py`, but their status is unverified. Rely on current CRONOS documentation.)*

## Next Steps (Based on Roadmap v8.1 - Q2 2025 Priorities)

1. **System Standardization:**
    - Complete the directory structure migration (Root dir cleanup done, further migration planned).
    - Implement the KOIOS Standardization System.
    - Complete the English language migration.
2. **KOIOS Evolution:**
    - Enhance the core KOIOS system.
    - Improve the search system.
    - Develop the documentation system.
3. **Mycelium Network Integration:**
    - Plan BIOS-Q integration for the Network instance.
    - Integrate pilot subsystems (e.g., KOIOS, CORUJA) with Mycelium.
    - Implement Phase 2 features (Health, Sync, Routing).
4. **Enhance ETHIK:** Continue core validation and enhancement development.
5. **Develop CORUJA:** Continue Phase 1 (Documentation, Templates, Metrics).
6. **Develop MCP Integrations:** Prioritize CRONOS, NEXUS, ETHIK, and ATLAS MCPs.
7. **KOIOS Standardization:** Core modules completed, ongoing for others.
8. **CORUJA Development:** Basic PromptManager and Orchestrator in progress.
9. **Review CRONOS Implementation:** For refactoring opportunities.
10. **Begin Mycelium Technology Selection:** And initial API design.

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧

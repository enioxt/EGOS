---
metadata:
  author: EVA & GUARANI
  backup_required: true
  category: SUBSYSTEM_DOCUMENTATION
  description: Overview of the KOIOS subsystem, responsible for standardization, logging, search, and documentation within EGOS.
  documentation_quality: 0.6 # Initial Draft
  encoding: utf-8
  ethical_validation: false # Subsystem overview
  last_updated: '2025-04-08' # Updated Date
  related_files:
    - subsystems/KOIOS/docs/STANDARDS.md
    - docs/MQP.md
    - ROADMAP.md
  required: true # Core subsystem README
  review_status: draft
  security_level: 0.5 # Public documentation
  subsystem: KOIOS
  type: documentation
  version: '0.1'
  windows_compatibility: true
---

# 🏛️ EVA & GUARANI - KOIOS Subsystem

**Version:** 0.1 (Initial Structure)
**Status:** Active Development

## 1. Overview

KOIOS (Knowledge, Order, Integration, & Operational Standards) is the central nervous system for standardization, documentation, logging, and knowledge management within the EVA & GUARANI Operational System (EGOS).

Its primary goal is to ensure consistency, clarity, and accessibility of information and processes across all subsystems, facilitating both human understanding and AI agent interaction.

## 2. Core Responsibilities & Planned Components

KOIOS encompasses several key functional areas, with components being actively developed or planned:

*   **Standardization Engine:**
    *   *Goal:* Define and enforce project-wide standards.
    *   *Components (Planned/Developing - See Roadmap):*
        *   Naming Convention Validator
        *   Metadata Validation System
        *   Directory Structure Rules
        *   Code Style Guidelines Integration (Future)
        *   Documentation Template System & Validation
*   **Logging System (`core/logger.py`):**
    *   *Goal:* Provide a unified, structured logging mechanism.
    *   *Component (`KoiosLogger`):* Standardized logger used by all subsystems. Features structured logging, context injection, and configurable outputs.
*   **Prompt Management Standards:**
    *   *Goal:* Ensure clarity, consistency, and evaluation for AI prompts.
    *   *Component (Template):* The **Prompt Design Document (PDD)** template (`docs/templates/PDD_Template.md`) defines the standard for documenting prompts.
*   **Search System:**
    *   *Goal:* Enable powerful searching across code, documentation, and potentially other project artifacts.
    *   *Components (Planned/Developing - See Roadmap):*
        *   Semantic Search (Vector Embeddings)
        *   Pattern-Based Search (Regex/AST)
        *   Metadata-Driven Search
        *   Cross-Subsystem Search Aggregation
*   **Documentation System:**
    *   *Goal:* Manage, validate, and enhance project documentation.
    *   *Components (Partially Implemented/Planned):*
        *   MDC Rules Definition (`.cursor/rules/*.mdc`) & Standard.
        *   **Prompt Design Documents (PDDs):** Standard format for documenting prompts (see template).
        *   Documentation Quality Metrics (Future).
        *   Automated Cross-Linking & Validation (Future)
*   **Cross-Reference System:**
    *   *Goal:* Automatically identify and link related entities (files, functions, classes, documentation sections) across the project.
    *   *Components (Planned):* Tightly integrated with Search and Documentation systems.

## 3. Integration

*   **Mycelium:** KOIOS will likely expose services via Mycelium for tasks like on-demand validation, search queries, or documentation generation requests (Future).
*   **All Subsystems:** Every other subsystem relies on KOIOS for logging (`KoiosLogger`) and adherence to its defined standards.
*   **CRONOS:** Backup/Restore operations managed by CRONOS may include KOIOS indices or configuration.
*   **NEXUS/ATLAS:** Search results and cross-references from KOIOS can enrich the analysis and visualization provided by NEXUS and ATLAS.

## 4. Current Status & Next Steps

*   `KoiosLogger` implemented and integrated into key subsystems.
*   Initial documentation standards (MDC Rules) defined.
*   **Completed foundational standardization across the project:** This includes establishing the standard directory structure (`core/`, `tests/`, `services/`, etc.), standardizing linting and formatting with `ruff` and pre-commit hooks, moving service files, creating skeleton subsystems, and resolving initial syntax/linting issues.
*   Roadmap clearly outlines development priorities for Standardization, Search, and Documentation systems (See `ROADMAP.md`, Q2 2025).
*   Next steps focus on implementing the validation scripts and researching semantic search libraries as per the immediate roadmap items.

## 5. Usage Examples

### Using KoiosLogger (Primary Current Interface)

```python
from koios.logger import KoiosLogger

# Get a logger specific to the current module/subsystem
logger = KoiosLogger.get_logger("SUBSYSTEM.ModuleName")

def perform_action(data):
    logger.info("Starting action.", extra={"data_id": data.get("id")})
    try:
        # ... perform action ...
        result = "Success"
        logger.info("Action completed successfully.", extra={"result": result})
        return result
    except Exception as e:
        logger.error("Action failed.", exc_info=True, extra={"error_type": type(e).__name__})
        raise
```

*(Other usage examples will be added as components like Search and Validation are implemented.)*

## 6. Configuration

KOIOS configuration (e.g., logging levels, standard paths, search parameters) will likely be managed centrally within the **EGOS** configuration structure, potentially with a dedicated `koios_config.json` or section.

## 7. Contributing

Contributions should strictly adhere to existing KOIOS standards. When defining new core prompts, utilize the **[PDD Template](../../docs/templates/PDD_Template.md)**. Proposals for new standards require discussion and approval.

✧༺❀༻∞ EGOS ∞༺❀༻✧

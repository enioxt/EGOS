---
metadata:
  author: EVA & GUARANI
  backup_required: true
  category: STANDARD_DOCUMENTATION
  description: Defines the standard directory structure for EGOS subsystems.
  documentation_quality: 0.9 # Reviewed and Aligned
  encoding: utf-8
  ethical_validation: false # Structural standard
  last_updated: '2025-04-08' # Updated Date
  related_files:
    - subsystems/KOIOS/docs/STANDARDS.md
    - subsystems/KOIOS/README.md
  required: true # Core project standard
  review_status: finalized
  security_level: 0.5 # Public documentation
  subsystem: KOIOS
  type: documentation
  version: '1.1' # Updated to align with STANDARDS.md
  windows_compatibility: true
---

# EGOS Subsystem Structure Standard (KOIOS)

**Version:** 1.1
**Status:** Adopted

## Purpose

This standard defines the mandatory and recommended directory structure for all EGOS subsystems located under the `subsystems/` directory. Adhering to this structure ensures consistency, maintainability, and easier navigation for both human developers and AI assistants across the project.

## Standard Structure

Each subsystem directory (e.g., `subsystems/NEXUS/`) **MUST** contain the following top-level files and directories:

*   `__init__.py`: Standard Python package marker. Can be empty or contain minimal initialization logic (e.g., defining `__all__`).
*   `README.md`: High-level overview of the subsystem's purpose, responsibilities, key components, and basic usage instructions.
*   `ROADMAP.md`: Subsystem-specific development roadmap, outlining planned features, tasks, and future milestones. Should align with the main project `ROADMAP.md`.
*   `core/`: **MUST** contain the primary logic, business rules, core classes, and internal functionalities of the subsystem. Complex subsystems may further subdivide `core/` (e.g., `core/analysis`, `core/parsing`).
*   `docs/`: **MUST** contain detailed documentation specific to the subsystem, including design documents, usage guides, API references (if applicable), and explanations beyond the README.
*   `tests/`: **MUST** contain all unit, integration, and functional tests for the subsystem, typically mirroring the structure of the `core/` and `services/` directories (e.g., `tests/core/test_analyzer.py`, `tests/services/test_main_service.py`).

The following files and directories are **RECOMMENDED** or **OPTIONAL** based on the subsystem's needs:

*   `interfaces/`: **RECOMMENDED** if the subsystem provides or consumes clearly defined programmatic interfaces (Abstract Base Classes, Pydantic models for data exchange) separate from its core implementation.
*   `services/`: **RECOMMENDED** for subsystems that expose higher-level service operations, potentially coordinating actions within the `core/` or interacting with external systems/Mycelium. This is preferred over placing large service orchestration logic directly in the subsystem root or `core/`.
*   `utils/`: **OPTIONAL** for utility functions or helper classes specific to the subsystem that don't fit neatly into `core/`. Avoid creating overly generic utils here; consider `subsystems/SHARED_UTILS/` if applicable across multiple subsystems.
*   `config/`: **OPTIONAL** for subsystem-specific configuration file *templates* (e.g., `settings.example.yaml`). Actual configuration (if not managed centrally or via environment variables) should reside outside version control or follow project-wide configuration patterns defined elsewhere.
*   `exceptions.py` (or `exceptions/` dir): **RECOMMENDED** for defining custom exception classes specific to the subsystem, inheriting from base exceptions where appropriate (See `error_handling.mdc` Rule).
*   `schemas/`: **OPTIONAL** for defining data schemas (e.g., Pydantic models) used internally or for validation, if not placed in `interfaces/`.

The following are **DISCOURAGED** directly within the subsystem's root directory:

*   Any `.py` file other than `__init__.py` or `exceptions.py`. Core logic belongs in `core/`, services in `services/`, etc.
*   Test scripts or test artifacts (e.g., `.ps1`, `.coverage`, `.venv`). These belong in `tests/` or should be handled by the root `.gitignore`.
*   Non-standard configuration files (use `config/` for templates or follow central config strategy).
*   Large binary files or data files (consider `resources/` if necessary, but evaluate if they belong in the repository).

## Rationale

A consistent structure:
*   Improves predictability and reduces cognitive load when switching between subsystems.
*   Facilitates automated tooling (testing, documentation generation, AI analysis).
*   Enforces separation of concerns (core logic vs. interfaces vs. tests vs. services).
*   Aligns with common Python project layout practices.

## Enforcement

*   Pre-commit hooks may be added in the future to perform basic structure checks.
*   Code reviews should verify adherence to this standard.
*   AI Assistants (EVA & GUARANI) should use this standard when creating or refactoring subsystem components.

✧༺❀༻∞ KOIOS - EGOS Standards Authority ∞༺❀༻✧

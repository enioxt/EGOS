---
metadata:
  author: EVA & GUARANI
  backup_required: true
  category: STANDARD_DOCUMENTATION
  description: Outlines the framework and tools used for syntax standardization and automated code quality checks in EGOS.
  documentation_quality: 0.8 # Updated to reflect current tooling
  encoding: utf-8
  ethical_validation: false # Tooling/process documentation
  last_updated: '2025-04-08' # Updated Date
  related_files:
    - subsystems/KOIOS/docs/STANDARDS.md
    - .pre-commit-config.yaml
    - pyproject.toml
  required: true # Core development process
  review_status: finalized
  security_level: 0.5 # Internal documentation
  subsystem: KOIOS
  type: documentation
  version: '1.0' # Updated version reflecting tool change
  windows_compatibility: true
---

# KOIOS: Syntax Standardization & Correction Framework

**Version:** 1.0
**Status:** Implemented

## Goal

To minimize syntax errors, enforce consistent coding style, and improve code quality across the EGOS project, ensuring compatibility and readability.

## Scope

-   Python (`.py`)
-   Configuration Files (`.json`, `.yaml`, `.toml`)
-   Documentation (`.md` - Basic checks like whitespace)

## Chosen Tool: Ruff

-   **Primary Tool:** `Ruff` ([https://github.com/astral-sh/ruff](https://github.com/astral-sh/ruff)) serves as both the **linter** and **formatter** for Python code.
-   **Configuration:** Managed via `pyproject.toml` in the project root.
-   **Key Features Used:**
    -   Linting (replaces `flake8`, `pylint`, etc.)
    -   Formatting (replaces `black`)
    -   Import sorting
    -   Fixing capabilities for many common issues.

## Additional Tools (via Pre-Commit Hooks)

-   **General Checks:** `pre-commit-hooks` are used for general file health:
    -   `trailing-whitespace`: Removes trailing whitespace.
    -   `end-of-file-fixer`: Ensures files end with a single newline.
    -   `check-yaml`: Checks YAML files for parseable syntax.
    -   `check-json`: Checks JSON files for parseable syntax.
-   **(Future Consideration):** Tools like `shellcheck` (for `.sh`) or `PSScriptAnalyzer` (for `.ps1`) could be integrated if shell script usage becomes significant.

## Automation Strategy: Pre-Commit Hooks

-   **Primary Mechanism:** Utilize the `pre-commit` framework ([https://pre-commit.com/](https://pre-commit.com/)).
-   **Configuration:** Managed via `.pre-commit-config.yaml` in the project root.
-   **Workflow:**
    1.  Developers run `pre-commit install` once in their local repository clone.
    2.  Before each commit, `pre-commit` automatically runs the configured linters and formatters (`ruff`, `trailing-whitespace`, etc.) on staged files.
    3.  `ruff format` and other fixers automatically correct style and formatting issues.
    4.  `ruff check` reports errors that may need manual correction if not auto-fixable.
    5.  Commits are prevented if any hooks fail.

## Configuration Files

-   `pyproject.toml`: Contains the `[tool.ruff]` section for configuring Ruff's linter rules, formatter settings (like line length), and other options.
-   `.pre-commit-config.yaml`: Defines the specific hooks, repositories, and versions used by the pre-commit framework.

## Implementation Status

-   Ruff is configured as the primary linter and formatter in `pyproject.toml`.
-   Pre-commit hooks for Ruff (linting with `--fix`, formatting) and general file checks are configured in `.pre-commit-config.yaml`.
-   The developer workflow (`pre-commit install`) is documented in KOIOS standards and should be part of onboarding.

✧༺❀༻∞ KOIOS - EGOS Standards Authority ∞༺❀༻✧

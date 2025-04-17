# Process: PROC-VALIDATE-02 - Subsystem Structure Validation

**Version:** 1.0
**Date:** 2025-04-17
**Status:** Active
**Owner:** KOIOS Subsystem

## 1. Purpose

This document describes the usage of the `subsystems/KOIOS/tools/validate_subsystem_structure.py` tool. This script verifies that individual subsystem directories adhere to the standard EGOS subsystem structure defined by KOIOS. Enforcing a consistent structure enhances navigability, maintainability, and automated tooling integration across the project.

## 2. Scope

This process applies to all top-level directories within the `subsystems/` directory (e.g., `subsystems/ATLAS`, `subsystems/CORUJA`, etc.). It checks for the presence of mandatory files and directories within each subsystem.

## 3. Procedure

### 3.1. Running the Script

The script is typically run from the project's root directory and requires the target subsystem directory as an argument.

```powershell
# Example for validating the ATLAS subsystem
python subsystems/KOIOS/tools/validate_subsystem_structure.py subsystems/ATLAS

# Example for validating the HARMONY subsystem
python subsystems/KOIOS/tools/validate_subsystem_structure.py subsystems/HARMONY
```

*(Note: The script could be enhanced to automatically scan and validate all subsystems if run without arguments.)*

### 3.2. Script Functionality

- Takes the path to a subsystem directory as input.
- Checks for the existence of mandatory files and directories within that subsystem's root.
- The specific list of mandatory items is defined within the script (e.g., `README.md`, `src/`, `tests/`, `config/`, `docs/`, etc. - *confirm exact list from script implementation*).
- Reports any missing mandatory items for the specified subsystem.
- Exits with a non-zero status code if validation fails, suitable for use in CI/CD pipelines.

## 4. Expected Structure (Example)

A compliant subsystem (e.g., `subsystems/EXAMPLE/`) should contain at least the mandatory items defined by KOIOS. This might include:

```
subsystems/EXAMPLE/
├── README.md             # Subsystem overview, purpose, key components
├── config/               # Configuration files specific to EXAMPLE
│   └── default_config.yaml
├── docs/                 # Detailed documentation for EXAMPLE
│   └── architecture.md
├── src/                  # Source code for the EXAMPLE subsystem
│   └── __init__.py
│   └── core.py
└── tests/                # Unit and integration tests for EXAMPLE
    └── __init__.py
    └── test_core.py
```

*(The actual mandatory list should be confirmed by inspecting the `validate_subsystem_structure.py` script or related KOIOS standards documents.)*

## 5. Examples & Common Corrections

*   **Error:** `Missing mandatory item: README.md in subsystems/FOOBAR`
    *   *Correction:* Create a `README.md` file in the `subsystems/FOOBAR/` directory with appropriate content.
*   **Error:** `Missing mandatory item: tests/ in subsystems/BAZQUX`
    *   *Correction:* Create a `tests` directory within `subsystems/BAZQUX/` and add initial test files (e.g., `__init__.py`).

## 6. Related Standards

- KOIOS Subsystem Architecture and Directory Structure standards.
- `README.md` content guidelines for subsystems.

## 7. Troubleshooting

- **Script not found:** Ensure you are running the command from the project root directory (`c:\Eva Guarani EGOS`).
- **Invalid subsystem path:** Double-check that the path provided as an argument exists and points to a valid subsystem directory (e.g., `subsystems/ATLAS`).
- **Incorrect validation:** If the script incorrectly reports missing items that exist, or fails to report genuinely missing items, verify the mandatory list within the script aligns with current KOIOS standards. Open an issue if discrepancies are found.

---
✧༺❀༻∞ EGOS ∞༺❀༻✧

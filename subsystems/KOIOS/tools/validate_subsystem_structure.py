"""
EGOS/KOIOS Validation Script: Subsystem Structure

Checks all directories under `subsystems/` against the standard structure
defined in `subsystems/KOIOS/docs/subsystem_structure.md`.

Usage:
    python validate_subsystem_structure.py
"""

import argparse
import os
# TODO: Import KoiosLogger
# TODO: Import MyceliumInterface (or use a NATS client directly)

MANDATORY_ITEMS = [
    "__init__.py",
    "README.md",
    "ROADMAP.md",
    "core",
    "docs",
    "tests",
]

RECOMMENDED_ITEMS = [
    "interfaces",
    "services",
    "utils",
    "config",
    "exceptions.py", # or exceptions/
    "schemas",
]

def validate_structure(subsystem_path):
    """Validates the structure of a single subsystem directory."""
    violations = []
    warnings = []
    subsystem_name = os.path.basename(subsystem_path)

    if not os.path.isdir(subsystem_path):
        return [f"{subsystem_name}: Is not a directory."], []

    actual_items = set(os.listdir(subsystem_path))

    # Check mandatory items
    for item in MANDATORY_ITEMS:
        if item not in actual_items:
            item_type = "directory" if "/" in item or item in ["core", "docs", "tests"] else "file"
            violations.append(f"{subsystem_name}: Missing mandatory {item_type} '{item}'.")
        # Optional: Check if dirs are actually dirs, files are files
        elif item in ["core", "docs", "tests"] and not os.path.isdir(os.path.join(subsystem_path, item)):
             violations.append(f"{subsystem_name}: Mandatory item '{item}' exists but is not a directory.")
        elif item not in ["core", "docs", "tests"] and not os.path.isfile(os.path.join(subsystem_path, item)):
             violations.append(f"{subsystem_name}: Mandatory item '{item}' exists but is not a file.")

    # Check recommended items (as warnings)
    # Simplified check for presence only
    # for item in RECOMMENDED_ITEMS:
    #     if item not in actual_items and item != "exceptions/" and not os.path.exists(os.path.join(subsystem_path, "exceptions")):
    #          warnings.append(f"{subsystem_name}: Missing recommended item '{item}'.")

    # Check for discouraged items (root .py files other than __init__.py/exceptions.py)
    for item in actual_items:
        if item.endswith(".py") and item not in ["__init__.py", "exceptions.py"]:
            violations.append(f"{subsystem_name}: Discouraged root Python file '{item}'. Should be in core/, services/, utils/ etc.")

    return violations, warnings

def main():
    parser = argparse.ArgumentParser(description="Validate subsystem directory structures.")
    args = parser.parse_args()

    # TODO: Initialize KoiosLogger
    # TODO: Initialize Mycelium connection

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    subsystems_dir = os.path.join(project_root, 'subsystems')

    all_violations = []
    all_warnings = []

    if not os.path.isdir(subsystems_dir):
        print(f"[ERROR] Subsystems directory not found: {subsystems_dir}")
        return

    print(f"Scanning subsystems in: {subsystems_dir}\n")

    for item_name in os.listdir(subsystems_dir):
        item_path = os.path.join(subsystems_dir, item_name)
        if os.path.isdir(item_path):
            # Simple check to avoid validating things like __pycache__ if present
            if not item_name.startswith("_") and item_name != "SHARED_UTILS": # TODO: Define skip list
                violations, warnings = validate_structure(item_path)
                all_violations.extend(violations)
                all_warnings.extend(warnings)

    print("--- Validation Results ---")
    if not all_violations and not all_warnings:
        print("All checked subsystems adhere to the structure standard.")
        validation_status = "passed"
    else:
        validation_status = "failed"
        if all_violations:
            print("\n[VIOLATIONS] Mandatory rules not met:")
            for v in all_violations:
                print(f"- {v}")
        # if all_warnings:
        #     print("\n[WARNINGS] Recommended items missing:")
        #     for w in all_warnings:
        #         print(f"- {w}")

    print("\n--- Scan Complete ---")
    # TODO: Publish final status to Mycelium (e.g., event.koios.validation.structure.complete, status=validation_status, details=...)

if __name__ == "__main__":
    main()

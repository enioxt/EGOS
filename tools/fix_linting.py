#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVA & GUARANI - KOIOS Linting Auto-Fix Tool
===========================================

Automatically fixes common linting errors in the codebase:
- E501: Line too long
- F841: Unused variable
- F821: Undefined name
- E712: Comparison to boolean literals

Version: 1.0.0
"""

import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Dict, List

# --- Configuration ---
PROJECT_ROOT = Path(__file__).parent.resolve()
MAX_LINE_LENGTH = 100
IGNORED_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "venv",
    ".venv",
    "build",
    "dist",
    "logs",
    "backups",
}


def find_project_root() -> Path:
    """Find the project root by looking for .git directory or pyproject.toml file."""
    current = PROJECT_ROOT

    while current != current.parent:
        if (current / ".git").exists() or (current / "pyproject.toml").exists():
            return current
        current = current.parent

    print(f"Could not find project root, using {PROJECT_ROOT}")
    return PROJECT_ROOT


def should_ignore_path(path: Path) -> bool:
    """Determine if a path should be ignored."""
    parts = path.parts
    for part in parts:
        if part in IGNORED_DIRS:
            return True
    return False


def find_python_files(root_dir: Path) -> List[Path]:
    """Find all Python files in the project."""
    python_files = []

    for path in root_dir.glob("**/*.py"):
        if not should_ignore_path(path):
            python_files.append(path)

    return python_files


def run_ruff_check(file_path: Path) -> List[Dict]:
    """Run ruff check on a file and return diagnostics."""
    try:
        # Run ruff check with --format=json and capture output
        result = subprocess.run(
            ["ruff", "check", str(file_path), "--format=json"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Check if ruff command was successful
        if result.returncode == 0:
            print(" no issues found")
            return []

        try:
            # Try to parse JSON output
            diagnostics = json.loads(result.stdout)
            return diagnostics
        except json.JSONDecodeError:
            # If JSON parsing fails, check if there's any stdout
            if result.stdout.strip():
                print(" found issues but couldn't parse output")
                print(result.stdout)
            else:
                print(" no issues found")
            return []

    except FileNotFoundError:
        print("Error: ruff is not installed. Please install it with: pip install ruff")
        sys.exit(1)
    except Exception as e:
        print(f"Error running ruff on {file_path}: {str(e)}")
        return []


def fix_file(file_path, diagnostics):
    """Apply fixes for common linting errors in a file."""
    if not diagnostics:
        return

    print(f"Fixing {len(diagnostics)} issues in {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    fixes_made = {"E501": 0, "F841": 0, "E712": 0, "F821": 0}

    modified = False

    for diagnostic in diagnostics:
        code = diagnostic.get("code", "")
        message = diagnostic.get("message", "")
        line_num = diagnostic.get("location", {}).get("row", 0) - 1  # Convert to 0-based

        if 0 <= line_num < len(lines):
            if code == "E501":  # Line too long
                # Try to break the line at a reasonable point
                line = lines[line_num]
                if len(line) > 100:
                    # Simple approach: break at the last space before column 100
                    last_space = line[:100].rfind(" ")
                    if last_space > 0:
                        lines[line_num] = (
                            line[:last_space] + "\\\n" + " " * 4 + line[last_space + 1 :]
                        )
                        fixes_made["E501"] += 1
                        modified = True

            elif code == "F841":  # Unused variable
                # Comment out the line with the unused variable
                lines[line_num] = "# " + lines[line_num]  # Simple fix - comment out
                fixes_made["F841"] += 1
                modified = True

            elif code == "E712":  # Comparison to bool
                line = lines[line_num]
                line = line.replace("== True", "").replace("== False", " not ")
                lines[line_num] = line
                fixes_made["E712"] += 1
                modified = True

            elif code == "F821":  # Undefined name
                # Add import at the top if it's a common module
                if any(mod in message for mod in ["os", "sys", "json", "re"]):
                    mod = next(mod for mod in ["os", "sys", "json", "re"] if mod in message)
                    lines.insert(0, f"import {mod}\n")
                    fixes_made["F821"] += 1
                    modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return fixes_made


def process_file(file_path):
    """Process a single file for linting issues."""
    print(f"Processing {os.path.relpath(file_path)}...", end="")

    # Run ruff check
    diagnostics = run_ruff_check(file_path)

    # Apply fixes if there are any issues
    if diagnostics:
        fixes = fix_file(file_path, diagnostics)
        fixed = sum(fixes.values())
        if fixed > 0:
            print(
                f" fixed {fixed} issues (E501: {fixes['E501']}, F841: {fixes['F841']}, "
                f"E712: {fixes['E712']}, F821: {fixes['F821']})"
            )
        else:
            print(" no issues found")
    else:
        print(" no issues found")

    return fixes if diagnostics else {"E501": 0, "F841": 0, "E712": 0, "F821": 0}


def main():
    """Main entry point."""
    print("EVA & GUARANI - KOIOS Linting Auto-Fix Tool")
    print("===========================================")

    # Find project root
    project_root = find_project_root()
    print(f"Project root: {project_root}")

    # Find all Python files
    python_files = find_python_files(project_root)
    print(f"Found {len(python_files)} Python files to check")

    # Process each file
    total_fixed = 0
    total_e501 = 0
    total_f841 = 0
    total_e712 = 0
    total_f821 = 0

    for i, file_path in enumerate(python_files):
        print(
            f"[{i + 1}/{len(python_files)}] Processing {file_path.relative_to(project_root)}...",
            end="",
        )

        fixes = process_file(file_path)
        fixed = sum(fixes.values())

        total_fixed += fixed
        total_e501 += fixes["E501"]
        total_f841 += fixes["F841"]
        total_e712 += fixes["E712"]
        total_f821 += fixes["F821"]

        if fixed > 0:
            print(
                f" fixed {fixed} issues (E501: {fixes['E501']}, F841: {fixes['F841']}, "
                f"E712: {fixes['E712']}, F821: {fixes['F821']})"
            )
        else:
            print(" no issues found")

    print("\nSummary:")
    print(f"Total files processed: {len(python_files)}")
    print(f"Total issues fixed: {total_fixed}")
    print(f"- E501 (line too long): {total_e501}")
    print(f"- F841 (unused variable): {total_f841}")
    print(f"- E712 (comparison to bool): {total_e712}")
    print(f"- F821 (undefined name): {total_f821}")
    print("\nRun pre-commit again to verify all issues have been resolved:")
    print("    git add .")
    print("    pre-commit run --all-files")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KOIOS Naming Convention Validator
================================

Scans project directories and files to ensure adherence to EGOS
naming conventions defined in KOIOS standards.

Version: 1.0
Last Updated: 2025-04-07
"""

import argparse
from pathlib import Path
import re
import sys
from typing import List

# Adjust import based on project structure
from subsystems.KOIOS.core.logging import KoiosLogger

# Initialize logger for the validator script
logger = KoiosLogger.get_logger("KOIOS.NamingValidator")

# --- Naming Convention Rules ---
# Based on KOIOS standards documentation (e.g., STANDARDS.md)
# Refined regex patterns for clarity and accuracy

# File patterns
PYTHON_FILE_PATTERN = r"^[a-z0-9_]+\.py$"  # snake_case.py
PYTHON_TEST_PATTERN = r"^test_[a-z0-9_]+\.py$"  # test_snake_case.py
MARKDOWN_GENERAL_PATTERN = r"^[a-z0-9_-]+\.md$"  # snake_case.md or kebab-case.md
MARKDOWN_SPECIFIC_PATTERN = r"^[A-Z_]+\.md$"  # UPPERCASE_SNAKE.md (e.g., README.md)
CONFIG_PATTERN = r"^[a-z0-9_.-]+\.(json|yaml|yml|toml|ini|cfg|env)$"
SCRIPT_PATTERN = r"^[a-z0-9_-]+\.(sh|bat|ps1)$"
SQL_PATTERN = r"^[a-z0-9_-]+\.(sql|ddl)$"
DOCKER_PATTERN = r"^(dockerfile|docker-compose\.yml)$"  # Specific names

# Directory patterns
DIR_SNAKE_KEBAB_PATTERN = r"^[a-z0-9_-]+$"  # General directories (snake_case or kebab-case)
DIR_UPPERCASE_PATTERN = r"^[A-Z0-9_]+$"  # Primarily for top-level subsystems

# Explicitly allowed file names (case-sensitive)
ALLOWED_SPECIFIC_FILES = {
    "README.md",
    "ROADMAP.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "LICENSE.md",
    "pyproject.toml",
    "requirements.txt",
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    ".env",
    ".pre-commit-config.yaml",
    "go.mod",  # Example if Go is used
    "__init__.py",
    "dockerfile",  # Allow lowercase dockerfile
    "docker-compose.yml",
    # Add other project-specific allowed files
}

# Directories whose *contents* should be ignored (not the directory itself)
# Case-sensitive directory names
IGNORE_CONTENTS_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    ".vscode",
    ".idea",
    ".cursor",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "build",
    "dist",
    "htmlcov",
    "logs",
    "temp",
    "tmp",
    "backups",
    "artifacts",
    "data",  # Often contains generated or downloaded files
    "*.egg-info",  # Build artifacts
}

# Top-level subsystem directories under /subsystems/ (expected UPPERCASE)
EXPECTED_UPPERCASE_SUBDIRS = {
    "ATLAS",
    "CRONOS",
    "ETHIK",
    "KOIOS",
    "MASTER",
    "MYCELIUM",
    "NEXUS",
    "CORUJA",
    "HARMONY",
    "SYNC",
    "TRANSLATOR",
    "BIOS-Q",
    # Add other official subsystems as needed
}

# --- Core Validation Logic ---


def validate_name(name: str, item_path: Path, is_dir: bool, project_root: Path) -> List[str]:
    """Validates a single file or directory name against EGOS conventions.

    Uses defined regex patterns and allowed lists to check the name.
    Skips files within ignored directories.

    Args:
        name: The base name of the file or directory.
        item_path: The full Path object of the item.
        is_dir: Boolean indicating if the item is a directory.
        project_root: The root Path of the project for context.

    Returns:
        A list of violation messages (strings). Empty if valid.
    """
    violations = []
    try:
        # Use relative path for clearer violation messages
        relative_path = str(item_path.relative_to(project_root))
    except ValueError:
        # Fallback if item is somehow outside the detected project root
        relative_path = str(item_path)
        logger.warning(
            f"Item '{item_path}' seems outside project root '{project_root}'. Using absolute path."
        )

    # --- Initial Skip Checks ---
    # 1. Skip specifically allowed file names (case-sensitive)
    if not is_dir and name in ALLOWED_SPECIFIC_FILES:
        logger.debug(f"Skipping allowed file: '{relative_path}'")
        return []

    # 2. Skip if item is within an explicitly ignored directory path
    # Check all parent directory names against the ignore list
    if any(part in IGNORE_CONTENTS_DIRS for part in item_path.parent.parts):
        logger.debug(f"Skipping item '{relative_path}' inside an ignored directory.")
        return []

    # 3. Skip the ignored directory *itself* from name validation
    # (but its contents are already skipped by check #2)
    if is_dir and name in IGNORE_CONTENTS_DIRS:
        logger.debug(f"Skipping validation for ignored directory name: '{relative_path}'")
        return []

    # --- Validation Rules ---
    if is_dir:
        # Directory Validation
        path_parts = item_path.relative_to(project_root).parts
        is_subsystem_root_dir = len(path_parts) == 2 and path_parts[0] == "subsystems"

        if is_subsystem_root_dir:
            # Rule: Directories directly under 'subsystems/' MUST be UPPERCASE_SNAKE
            if not re.fullmatch(DIR_UPPERCASE_PATTERN, name):
                violations.append(
                    f"Subsystem Directory Violation [KOIOS-N-D01]: Path '{relative_path}'. "
                    f"Expected UPPERCASE_SNAKE name, found '{name}'."
                )
            # Optional: Check against known subsystems
            elif name not in EXPECTED_UPPERCASE_SUBDIRS:
                logger.warning(
                    f"Potential Subsystem Directory [KOIOS-N-D02]: Path '{relative_path}'. "
                    f"Name '{name}' is uppercase but not in the known list."
                )
        else:
            # Rule: All other directories MUST be snake_case or kebab-case.
            if not re.fullmatch(DIR_SNAKE_KEBAB_PATTERN, name):
                violations.append(
                    f"Directory Name Violation [KOIOS-N-D03]: Path '{relative_path}'. "
                    f"Expected snake_case or kebab-case, found '{name}'."
                )
    else:
        # File Validation
        ext = item_path.suffix.lower()
        # Apply rules based on file extension
        if ext == ".py":
            if name.startswith("test_"):
                if not re.fullmatch(PYTHON_TEST_PATTERN, name):
                    violations.append(
                        f"Python Test File Violation [KOIOS-N-F01]: Path '{relative_path}'. "
                        f"Expected 'test_snake_case.py', found '{name}'."
                    )
            elif not re.fullmatch(PYTHON_FILE_PATTERN, name):
                # Exclude __init__.py as it's handled by ALLOWED_SPECIFIC_FILES
                violations.append(
                    f"Python File Violation [KOIOS-N-F02]: Path '{relative_path}'. "
                    f"Expected 'snake_case.py', found '{name}'."
                )
        elif ext == ".md":
            is_general = re.fullmatch(MARKDOWN_GENERAL_PATTERN, name)
            is_specific = re.fullmatch(MARKDOWN_SPECIFIC_PATTERN, name)
            if not (is_general or is_specific):
                violations.append(
                    f"Markdown File Violation [KOIOS-N-F03]: Path '{relative_path}'. "
                    f"Expected 'snake_case/kebab-case.md' or 'UPPERCASE_SNAKE.md', "
                    f"found '{name}'."
                )
        elif ext in [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env"]:
            if not re.fullmatch(CONFIG_PATTERN, name):
                violations.append(
                    f"Config File Violation [KOIOS-N-F04]: Path '{relative_path}'. "
                    f"Unexpected format/extension '{name}'."
                )
        elif ext in [".sh", ".bat", ".ps1"]:
            if not re.fullmatch(SCRIPT_PATTERN, name):
                violations.append(
                    f"Script File Violation [KOIOS-N-F05]: Path '{relative_path}'. "
                    f"Expected 'snake_case/kebab-case.{ext}', found '{name}'."
                )
        elif ext in [".sql", ".ddl"]:
            if not re.fullmatch(SQL_PATTERN, name):
                violations.append(
                    f"SQL File Violation [KOIOS-N-F06]: Path '{relative_path}'. "
                    f"Expected 'snake_case/kebab-case.{ext}', found '{name}'."
                )
        elif name == "dockerfile" or name == "docker-compose.yml":
            # These specific names are allowed via ALLOWED_SPECIFIC_FILES, no pattern needed here
            pass
        else:
            # Handle files with extensions not covered above
            if ext:
                violations.append(
                    f"Unknown File Type Violation [KOIOS-N-F98]: Path '{relative_path}'. "
                    f"Unrecognized/disallowed file extension '{ext}' for name '{name}'."
                )
            # Handle extensionless files not in the allowed list
            elif name not in ALLOWED_SPECIFIC_FILES:  # Double check, already done at start
                violations.append(
                    f"Extensionless File Violation [KOIOS-N-F99]: Path '{relative_path}'. "
                    f"Files without extensions are generally disallowed (found '{name}')."
                )

    # Log violations if found for this specific item
    if violations:
        logger.debug(f"Violations found for '{relative_path}': {violations}")

    return violations


def scan_directory(target_dir: Path, project_root: Path) -> List[str]:
    """Recursively scans a directory and validates file/subdir names.

    Args:
        target_dir: The directory Path to start scanning from.
        project_root: The root Path of the project for context.

    Returns:
        A flat list of all violation messages found during the scan.
    """
    all_violations = []
    logger.info(f"Scanning directory for naming conventions: {target_dir}")

    try:
        for item in target_dir.iterdir():
            item_name = item.name
            is_dir = item.is_dir()

            # Validate the name of the current item (file or directory)
            # The validation function handles skipping based on ignore lists
            violations = validate_name(item_name, item, is_dir, project_root)
            all_violations.extend(violations)

            # Recursively scan subdirectories if it's a directory AND
            # its name is not in the ignore list (contents of ignored dirs are skipped inside validate_name)
            if is_dir and item_name not in IGNORE_CONTENTS_DIRS:
                all_violations.extend(scan_directory(item, project_root))

    except PermissionError:
        logger.error(f"Permission denied accessing {target_dir}. Skipping scan of this directory.")
    except Exception as e:
        logger.exception(f"Unexpected error scanning directory {target_dir}: {e}")

    return all_violations


def find_project_root(start_path: Path) -> Path:
    """Find the project root by looking for common markers.

    Searches upwards from `start_path` for `.git` directory or `pyproject.toml`.

    Args:
        start_path: The Path object to start searching from.

    Returns:
        The resolved Path object of the detected project root.
        Falls back to the resolved `start_path` if no marker is found.
    """
    current_path = start_path.resolve()
    while True:
        if (current_path / ".git").is_dir() or (current_path / "pyproject.toml").is_file():
            logger.debug(f"Project root marker found at: {current_path}")
            return current_path
        if current_path.parent == current_path:  # Reached the filesystem root
            logger.warning(
                "Could not find project root marker (.git/pyproject.toml). "
                "Using starting directory as fallback: {start_path.resolve()}"
            )
            return start_path.resolve()  # Fallback to starting directory
        current_path = current_path.parent


def main():
    """Main execution function for the naming validator script."""
    parser = argparse.ArgumentParser(description="Validate EGOS naming conventions.")
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target directory or file to scan (defaults to current directory).",
    )
    # TODO: Add arguments for --exclude, --rules-file, etc.
    args = parser.parse_args()

    start_scan_path = Path(args.target).resolve()
    project_root = find_project_root(start_scan_path)
    logger.info(f"Determined project root: {project_root}")

    if not start_scan_path.exists():
        logger.critical(f"Target path does not exist: {start_scan_path}")
        return 1  # Indicate error

    violations = []
    if start_scan_path.is_dir():
        logger.info(f"Starting naming convention validation for directory: {start_scan_path}")
        violations = scan_directory(start_scan_path, project_root)
    elif start_scan_path.is_file():
        logger.info(f"Starting naming convention validation for file: {start_scan_path}")
        violations = validate_name(start_scan_path.name, start_scan_path, False, project_root)
    else:
        logger.error(f"Target path is neither a file nor a directory: {start_scan_path}")
        return 1  # Indicate error

    if violations:
        logger.warning("Naming convention violations found:")
        # Sort and remove duplicates for cleaner output
        unique_violations = sorted(list(set(violations)))
        for violation in unique_violations:
            logger.warning(f"- {violation}")
        print(f"\nFound {len(unique_violations)} naming violation(s).")
        return 1  # Indicate violations found
    else:
        logger.info("No naming convention violations found.")
        return 0  # Indicate success


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


# ✧༺❀༻∞ EGOS ∞༺❀༻✧

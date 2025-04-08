#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KOIOS Metadata Validator
========================

Scans project files (Python, Markdown) to ensure they contain required
metadata fields according to KOIOS standards.

Version: 1.1
Last Updated: 2025-04-07

TODO:
- Define the definitive metadata schema (load from config?).
- Implement robust Python metadata extraction (AST).
- Add more sophisticated validation logic (type checking, value constraints).
- Add command-line options (e.g., --schema-file, --exclude).
"""

import argparse
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

# --- YAML Dependency ---
try:
    import yaml
except ImportError:
    print("ERROR: PyYAML library not found. Please install it:")
    print("pip install PyYAML>=6.0")
    sys.exit(1)

# --- Project Imports ---
# Use absolute imports
try:
    from subsystems.KOIOS.core.logging import KoiosLogger

    # Reuse root finding and ignore list from naming validator for consistency
    from subsystems.KOIOS.validation.naming_validator import (
        IGNORE_CONTENTS_DIRS,
        find_project_root,
    )
except ImportError as e:
    print(f"Error importing validator components: {e}")
    print("Ensure the script is run correctly relative to the project root,")
    print("or adjust PYTHONPATH if necessary.")
    sys.exit(1)

# --- Globals & Constants ---
logger = KoiosLogger.get_logger("KOIOS.MetadataValidator")  # Updated logger name

# Placeholder Schema - Replace with actual schema definition later
PYTHON_REQUIRED_METADATA = {"description", "version", "author"}  # Example
MARKDOWN_REQUIRED_METADATA = {"description", "version", "status", "last_updated"}  # Example


# --- Core Functions ---
def extract_metadata_from_py(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Extracts metadata from a Python file.

    Placeholder implementation - needs robust parsing (e.g., AST, regex).
    Currently performs a very basic check for __version__ and __author__.

    Args:
        file_path: Path to the Python source file.

    Returns:
        A dictionary containing the found metadata, or None if none found
        or an error occurs.
    """
    logger.debug(f"Attempting metadata extraction from Python file: {file_path}")
    # TODO: Implement robust Python metadata extraction using AST
    metadata = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[:20]:  # Check first 20 lines only
                if line.startswith("__version__"):
                    metadata["version"] = line.split("=")[1].strip().strip("'\"")
                elif line.startswith("__author__"):
                    metadata["author"] = line.split("=")[1].strip().strip("'\"")
        if not metadata:
            logger.warning(
                f"No simple metadata found in Python file: {file_path}. Needs proper parsing."
            )
            return None
        # Placeholder: Assume description might be in module docstring (requires parsing)
        # metadata['description'] = parse_module_docstring(lines)
        return metadata
    except Exception as e:
        logger.error(f"Error extracting metadata from {file_path}: {e}", exc_info=True)
        return None


def extract_metadata_from_md(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Extracts metadata from YAML frontmatter in a Markdown file.

    Looks for content between `---` separators at the start of the file.

    Args:
        file_path: Path to the Markdown file.

    Returns:
        A dictionary containing the parsed metadata from the frontmatter,
        or None if no valid frontmatter is found or a parsing error occurs.
    """
    logger.debug(f"Attempting metadata extraction from Markdown file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.startswith("---"):
                logger.debug(f"No YAML frontmatter detected (missing initial '---') in {file_path}")
                return None  # File doesn't start with ---

            # Find the second --- separator
            end_marker_pos = content.find("---", 3)  # Start search after the first 3 chars
            if end_marker_pos == -1:
                logger.debug(f"No closing '---' found for YAML frontmatter in {file_path}")
                return None  # No closing marker found

            frontmatter = content[3:end_marker_pos].strip()
            if not frontmatter:
                logger.debug(f"YAML frontmatter section is empty in {file_path}")
                return None  # Empty frontmatter

            metadata = yaml.safe_load(frontmatter)

            if not isinstance(metadata, dict):
                logger.warning(
                    f"Could not parse YAML frontmatter into a dictionary in {file_path}. "
                    f"Found type: {type(metadata)}."
                )
                return None

            # KOIOS standard often uses a top-level `description` or specific keys.
            # Adjust based on actual standard. Assuming top-level keys for now.
            return metadata

    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML frontmatter in {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading or processing {file_path}: {e}", exc_info=True)
        return None


def validate_metadata(metadata: Optional[Dict[str, Any]], file_path: Path) -> List[str]:
    """
    Validates extracted metadata against a basic required schema for the file type.

    Currently uses placeholder schemas. Returns a list of violation messages.

    Args:
        metadata: The extracted metadata dictionary, or None if extraction failed.
        file_path: Path object of the file being validated.

    Returns:
        A list of strings, each describing a validation violation.
    """
    violations = []
    relative_path_str = str(file_path)  # Placeholder for potential relative path

    if metadata is None:
        # If extraction failed for a type we *should* handle, it might be an issue.
        # For now, we only log debug and proceed.
        logger.debug(
            f"No metadata to validate for {relative_path_str} (extraction failed or not applicable)."
        )
        return violations

    if not isinstance(metadata, dict):
        violations.append(
            f"Invalid Format [KOIOS-M-F01]: Expected metadata dictionary, "
            f"found {type(metadata)} in '{relative_path_str}'."
        )
        return violations  # Cannot proceed if not a dict

    required_fields = set()
    file_ext = file_path.suffix.lower()

    # Select schema based on file type
    if file_ext == ".py":
        required_fields = PYTHON_REQUIRED_METADATA
    elif file_ext == ".md":
        required_fields = MARKDOWN_REQUIRED_METADATA
    else:
        # Don't validate types we don't have explicit rules for yet
        logger.debug(f"Skipping metadata validation for unhandled file type: {relative_path_str}")
        return violations

    # Check for missing required fields
    missing_fields = required_fields - metadata.keys()
    if missing_fields:
        for field in sorted(list(missing_fields)):
            violations.append(
                f"Metadata Missing [KOIOS-M-M01]: Required field '{field}' missing in '{relative_path_str}'."
            )

    # TODO: Implement more detailed validation (type checking, value constraints)
    # e.g., check if version is SemVer, status is known value, etc.

    return violations


def scan_directory_metadata(target_dir: Path, project_root: Path) -> List[str]:
    """
    Recursively scans a directory, extracts metadata from relevant files,
    and validates it against defined standards.

    Args:
        target_dir: The directory Path object to start scanning from.
        project_root: The root Path object of the project for context.

    Returns:
        A flat list of all violation messages found during the scan.
    """
    all_violations = []
    logger.info(f"Scanning directory for metadata compliance: {target_dir}")

    try:
        for item in target_dir.iterdir():
            try:
                relative_item_path = item.relative_to(project_root)
            except ValueError:
                logger.warning(f"Item {item} seems outside project root {project_root}. Skipping.")
                continue

            item_name = item.name
            is_dir = item.is_dir()

            # --- Skipping Logic (use from naming_validator) ---
            should_skip = False
            # Check if item itself is an ignored dir name
            if is_dir and item_name in IGNORE_CONTENTS_DIRS:
                logger.debug(f"[Metadata Scan] Skipping ignored directory: '{relative_item_path}'")
                should_skip = True
            else:
                # Check if any parent directory is ignored
                parent_parts = relative_item_path.parent.parts
                if parent_parts and any(part in IGNORE_CONTENTS_DIRS for part in parent_parts):
                    logger.debug(
                        f"[Metadata Scan] Skipping item '{relative_item_path}' "
                        f"inside an ignored directory."
                    )
                    should_skip = True

            if should_skip:
                continue
            # --- End Skipping Logic ---

            if is_dir:
                # Recursively scan subdirectories
                all_violations.extend(scan_directory_metadata(item, project_root))
            else:
                # Process files: Extract and Validate Metadata
                file_ext = item.suffix.lower()
                metadata: Optional[Dict[str, Any]] = None
                requires_validation = False

                # Determine if metadata extraction should be attempted
                if file_ext == ".py":
                    metadata = extract_metadata_from_py(item)
                    requires_validation = True  # We expect metadata for .py files
                elif file_ext == ".md":
                    metadata = extract_metadata_from_md(item)
                    requires_validation = True  # We expect metadata for .md files
                # Add other supported file types here...

                # Validate if the file type is one we handle
                if requires_validation:
                    # Pass the extracted metadata (even if None) to validation
                    file_violations = validate_metadata(metadata, item)
                    if file_violations:
                        logger.debug(f"Metadata violations found in {item}: {file_violations}")
                        all_violations.extend(file_violations)
                    elif metadata is not None:
                        logger.debug(f"Metadata validated successfully for {item.name}")

    except PermissionError:
        logger.error(f"[Metadata Scan] Permission denied accessing {target_dir}. Skipping.")
    except Exception as e:
        # Catch any other unexpected error during directory scan
        logger.exception(f"[Metadata Scan] Unexpected error scanning directory {target_dir}: {e}")

    return all_violations


# --- Main Execution ---
def main():
    """Main execution function for the metadata validator script."""
    parser = argparse.ArgumentParser(
        description="Validate EGOS metadata presence and basic structure in project files."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target directory or file to scan (defaults to current directory).",
    )
    # TODO: Add --schema argument
    args = parser.parse_args()

    start_scan_path = Path(args.target).resolve()
    # Find project root consistently using the helper function
    project_root = find_project_root(start_scan_path)
    logger.info(f"Determined project root: {project_root}")

    if not start_scan_path.exists():
        logger.critical(f"Target path does not exist: {start_scan_path}")
        return 1  # Indicate error

    violations = []
    if start_scan_path.is_dir():
        logger.info(f"Starting metadata validation scan for directory: {start_scan_path}")
        violations = scan_directory_metadata(start_scan_path, project_root)
    elif start_scan_path.is_file():
        logger.info(f"Starting metadata validation for file: {start_scan_path}")
        # Extract and validate metadata for the single file
        file_ext = start_scan_path.suffix.lower()
        metadata = None
        if file_ext == ".py":
            metadata = extract_metadata_from_py(start_scan_path)
        elif file_ext == ".md":
            metadata = extract_metadata_from_md(start_scan_path)
        # Validate only if extraction was attempted
        if file_ext in [".py", ".md"]:
            violations = validate_metadata(metadata, start_scan_path)
        else:
            logger.info(f"Metadata validation not applicable for file type: {start_scan_path}")
    else:
        logger.error(f"Target path is neither a file nor a directory: {start_scan_path}")
        return 1  # Indicate error

    if violations:
        logger.warning("Metadata validation violations found:")
        # Sort and remove duplicates for cleaner output
        unique_violations = sorted(list(set(violations)))
        for violation in unique_violations:
            logger.warning(f"- {violation}")
        print(f"\nFound {len(unique_violations)} metadata violation(s).")
        return 1  # Indicate violations found
    else:
        logger.info("No metadata validation violations found.")
        return 0  # Indicate success


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


# ✧༺❀༻∞ EGOS ∞༺❀༻✧

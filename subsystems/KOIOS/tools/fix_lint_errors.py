#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOIOS Lint Error Auto-fixer

This script attempts to automatically fix common linting errors in Python code,
primarily focusing on whitespace issues (W291/W293) and line length (E501).
It provides a report of attempted fixes and potential remaining issues.

Version: 1.0
Last Updated: 2025-04-08
"""

import argparse
from pathlib import Path
import re
import sys
from typing import List, Optional, Tuple

# TODO: Integrate with KoiosLogger
# from subsystems.KOIOS.core.logging import KoiosLogger
# logger = KoiosLogger.get_logger(__name__)


def fix_trailing_whitespace(content: str) -> str:
    """Remove trailing whitespace from all lines and blank lines."""
    # W291: trailing whitespace
    content = re.sub(r"[ \t]+$", "", content, flags=re.MULTILINE)
    # W293: blank line contains whitespace
    content = re.sub(r"^[ \t]+$", "", content, flags=re.MULTILINE)
    return content


def fix_long_lines(content: str, max_length: int = 100) -> str:
    """Attempt to split long lines (E501) safely.

    Focuses on splitting comments and potentially simple string assignments.
    More complex line splitting (e.g., complex expressions, function calls)
    is generally better handled by formatters like Ruff or Black.

    Args:
        content: The file content as a single string.
        max_length: The maximum allowed line length.

    Returns:
        The content with attempted line splitting.
    """
    lines = content.splitlines()
    result = []
    in_multiline_string = False  # Basic state tracking for triple-quoted strings

    for line in lines:
        # Toggle multiline string state
        if '"""' in line or "'''" in line:
            # Simple toggle; doesn't handle quotes within the multiline string itself well
            in_multiline_string = not in_multiline_string

        if len(line) <= max_length or in_multiline_string:
            result.append(line)
            continue

        # Attempt to fix comments
        stripped_line = line.lstrip()
        if stripped_line.startswith("#"):
            indent = line[: len(line) - len(stripped_line)]
            comment_body = stripped_line[1:].lstrip()  # Text after #
            current_line = f"{indent}# {comment_body}"

            # Split comment if too long
            if len(current_line) > max_length:
                split_point = -1
                # Find the last space before max_length
                for i in range(max_length - len(indent) - 2, 0, -1):
                    if current_line[i] == " ":
                        split_point = i
                        break

                if split_point > len(indent) + 2:  # Found a suitable space
                    result.append(current_line[:split_point])
                    remaining_comment = current_line[split_point:].lstrip()
                    # Add continuation lines, respecting indentation
                    # This is basic; a more robust solution might re-wrap words
                    result.append(f"{indent}# {remaining_comment}")
                else:
                    # Cannot split nicely, append original long comment
                    result.append(line)
            else:
                result.append(line)
            continue  # Move to next line after handling comment

        # Very basic attempt to split long assignments with simple strings
        # Example: long_variable_name = "this is a very very long string that needs splitting"
        # Note: This is fragile and might break complex lines.
        match = re.match(r'^(\\s*)(\\S+\\s*=\\s*)[\'\\"](.*)[\'\\"]\\s*$', line)
        if match:
            indent, assignment, str_content = match.groups()
            if len(line) > max_length:
                # Try to wrap using parentheses (preferred Python style for implicit concatenation)
                result.append(f"{indent}{assignment}(")
                # Using repr() ensures quotes and escapes are handled correctly.
                # Place the repr string on the next line, indented.
                # NOTE: This simple approach doesn't handle cases where repr_str itself
                # is longer than the max length minus indentation. A robust solution
                # would require further splitting logic within the repr_str.
                repr_str = repr(str_content)
                result.append(f"{indent}    {repr_str}")
                result.append(f"{indent})")
                continue  # Handled, move to next line

        # If no specific handling applied, add the long line as is
        # TODO: Add more robust line splitting logic if required,
        # potentially leveraging AST or external libraries, or recommend using Black/Ruff.
        result.append(line)

    # Join lines back, ensuring newline at the end if original had one
    final_content = "\n".join(result)
    if content.endswith("\n") and not final_content.endswith("\n"):
        final_content += "\n"
    return final_content


def process_file(
    file_path: Path, dry_run: bool = False, max_line_length: int = 100
) -> Tuple[bool, List[str]]:
    """Process a single file, fixing whitespace and attempting to fix long lines.

    Args:
        file_path: Path to the Python file.
        dry_run: If True, do not modify the file.
        max_line_length: Maximum line length for E501 fix attempts.

    Returns:
        A tuple: (bool indicating if changes were made, list of messages).
    """
    messages = []
    changed = False
    try:
        # Detect encoding - important for reading/writing correctly
        # Using a simple approach for now, enhance if needed
        encoding = "utf-8"  # Default
        try:
            with open(file_path, "rb") as fb:
                # Basic check for UTF-8 BOM
                if fb.read(3) == b"\xef\xbb\xbf":
                    encoding = "utf-8-sig"
        except Exception:
            pass  # Fallback to utf-8

        with open(file_path, "r", encoding=encoding) as f:
            original_content = f.read()

        # Apply fixes
        fixed_content = fix_trailing_whitespace(original_content)
        fixed_content = fix_long_lines(fixed_content, max_length=max_line_length)

        if fixed_content != original_content:
            changed = True
            messages.append(f"Applied fixes to {file_path.name}")
            if not dry_run:
                try:
                    with open(file_path, "w", encoding=encoding) as f:
                        f.write(fixed_content)
                except IOError as e:
                    messages.append(f"ERROR: Could not write changes to {file_path.name}: {e}")
                    # Revert changed status if write failed
                    changed = False
        else:
            messages.append(f"No changes needed for {file_path.name}")

        return changed, messages

    except Exception as e:
        return False, [f"ERROR: Could not process {file_path.name}: {e}"]


def find_python_files(directory: Path, exclude_patterns: Optional[List[str]] = None) -> List[Path]:
    """Find all Python files (.py) in a directory recursively.

    Args:
        directory: The root directory Path object to search.
        exclude_patterns: A list of regex patterns for paths to exclude.
                          Patterns match against the full path string.

    Returns:
        A list of Path objects for found Python files.
    """
    if exclude_patterns is None:
        exclude_patterns = []

    compiled_excludes = [re.compile(p) for p in exclude_patterns]
    py_files = []

    for item in directory.rglob("*.py"):  # Use rglob for recursive search
        if item.is_file():
            full_path_str = str(item.resolve())
            # Check if the path matches any exclude patterns
            if not any(pattern.search(full_path_str) for pattern in compiled_excludes):
                py_files.append(item)

    return py_files


def main():
    """Main execution function for the lint fixer script."""
    parser = argparse.ArgumentParser(
        description="Fix common linting errors (whitespace, line length) in Python code."
    )
    parser.add_argument("path", help="File or directory path to process")
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=[],
        help="Regex patterns for full paths to exclude (e.g., '\\.venv/', 'tests/')",  # Escaped backslash
    )
    parser.add_argument(
        "--max-length", type=int, default=100, help="Maximum line length (default: 100)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be changed without modifying files."
    )
    args = parser.parse_args()

    target_path = Path(args.path)

    if not target_path.exists():
        print(f"Error: Path not found: {target_path}", file=sys.stderr)
        return 1

    if target_path.is_file():
        if target_path.suffix == ".py":
            files_to_process = [target_path]
        else:
            print(f"Error: Target file is not a Python file: {target_path}", file=sys.stderr)
            return 1
    elif target_path.is_dir():
        print(f"Scanning directory: {target_path}")
        files_to_process = find_python_files(target_path, args.exclude)
    else:
        print(f"Error: Path is not a file or directory: {target_path}", file=sys.stderr)
        return 1

    if not files_to_process:
        print("No Python files found to process.")
        return 0

    print(f"Processing {len(files_to_process)} Python files...")

    total_changed = 0
    total_errors = 0
    results_summary = []

    for file_p in files_to_process:
        changed, messages = process_file(file_p, args.dry_run, args.max_length)
        results_summary.extend(messages)
        if any("ERROR:" in msg for msg in messages):
            total_errors += 1
        elif changed:
            total_changed += 1

    # Print detailed results
    print("\n--- Processing Results ---")
    for msg in results_summary:
        print(msg)

    print("\n--- Summary ---")
    action = "Would change" if args.dry_run else "Changed"
    print(f"{action}: {total_changed} file(s)")
    print(f"Errors encountered: {total_errors} file(s)")
    print(f"Total files processed: {len(files_to_process)}")

    if args.dry_run and total_changed > 0:
        print("\nRun without --dry-run to apply changes.")

    # Return success (0) if no errors, error (1) otherwise
    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())


# ✧༺❀༻∞ EGOS ∞༺❀༻✧

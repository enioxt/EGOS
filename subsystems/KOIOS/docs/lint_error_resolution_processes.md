---
metadata:
  author: EVA & GUARANI
  backup_required: true
  category: PROCESS_DOCUMENTATION
  description: Standard operating procedures for identifying and resolving common linting errors (whitespace, line length, undefined variables) in EGOS Python code using Ruff.
  documentation_quality: 0.8 # Translated and Standardized
  encoding: utf-8
  ethical_validation: false # Process documentation
  last_updated: '2025-04-08' # Updated Date
  related_files:
    - subsystems/KOIOS/docs/STANDARDS.md
    - subsystems/KOIOS/tools/fix_lint_errors.py
    - .pre-commit-config.yaml
    - pyproject.toml
  required: true # Core development process
  review_status: reviewed
  security_level: 0.5 # Internal documentation
  subsystem: KOIOS
  type: documentation
  version: '1.1' # Updated for translation & standardization
  windows_compatibility: true
---

# KOIOS Process Documentation: Lint Error Resolution

**Version:** 1.1
**Date:** 2025-04-08
**Subsystem:** KOIOS
**Document Type:** Processes

## Overview

This document defines the standard processes for identifying and resolving common linting errors in EGOS Python code. The processes established here should be used to maintain code consistency throughout the system, improve readability, and prevent future issues.

## Table of Contents

1. [PR-LINT-01: Trailing Whitespace Resolution (W291/W293)](#pr-lint-01-trailing-whitespace-resolution-w291w293)
2. [PR-LINT-02: Line Length Resolution (E501)](#pr-lint-02-line-length-resolution-e501)
3. [PR-LINT-03: Undefined Variable Resolution (F821)](#pr-lint-03-undefined-variable-resolution-f821)
4. [PR-LINT-04: Lint Error Prevention Strategy](#pr-lint-04-lint-error-prevention-strategy)
5. [Root Cause Analysis](#root-cause-analysis)
6. [Related Tools](#related-tools)

## PR-LINT-01: Trailing Whitespace Resolution (W291/W293)

**Purpose:** Remove trailing whitespace and blank lines to maintain clean and consistent code.

**Inputs:** Files with linting errors W291 or W293.
**Outputs:** Files with consistent whitespace.

**Steps:**

1. **Identification:**
    * Run `ruff check <directory_or_file> --select=W291,W293` to identify files with whitespace issues.
    * Note the files and line numbers in the output.

2. **Resolution Options:**
    * **Option A: Automatically via Tool:**
        1. Run `ruff check <file_path> --fix` to automatically correct simple whitespace issues.
        2. Verify corrections: `ruff check <file_path> --select=W291,W293`.

    * **Option B: IDE Features:**
        1. Open the file in your IDE.
        2. Use the "Trim Trailing Whitespace" feature (common in most IDEs).
        3. Save the file.
        4. Verify: `ruff check <file_path> --select=W291,W293`.

    * **Option C: Manual Correction:**
        1. Open the file in your editor.
        2. Navigate to the lines with trailing whitespace.
        3. Remove all trailing spaces and tabs from each line.
        4. For blank lines with whitespace, remove all content.
        5. Save the file.
        6. Verify: `ruff check <file_path> --select=W291,W293`.

    * **Option D: Correction via Script:**
        1. Use the script `fix_lint_errors.py` (located in `subsystems/KOIOS/tools/`).
        2. Run: `python subsystems/KOIOS/tools/fix_lint_errors.py <file_path>`.
        3. Verify: `ruff check <file_path> --select=W291,W293`.

3. **Prevention:**
    * Configure your IDE to automatically remove trailing whitespace on save.
    * Add a pre-commit hook that catches and fixes whitespace issues before commits.
    * Review editor settings for visible whitespace to detect these issues during coding.

## PR-LINT-02: Line Length Resolution (E501)

**Purpose:** Ensure code lines do not exceed the 100-character limit to improve readability.

**Inputs:** Files with linting errors E501.
**Outputs:** Files with appropriate line length formatting.

**Steps:**

1. **Identification:**
    * Run `ruff check <directory_or_file> --select=E501` to identify files with line length issues.
    * Note the files and line numbers in the output.

2. **Assessment:**
    * Examine each flagged line to determine its content type:
        * Comment
        * String literal
        * Function/method call
        * Data structure definition
        * Import statement

3. **Resolution by Content Type:**
    * **Comments:**
        * Break long comments into multiple lines.
        * Keep the comment marker (#) on each line.

        ```python
        # This is a very long comment that exceeds the 100-character limit and needs to be broken up
        # Corrected:
        # This is a very long comment that exceeds the 100-character limit
        # and needs to be broken up.
        ```

    * **String Literals:**
        * Use Python's string concatenation (implicit within parentheses) or multi-line strings.

        ```python
        long_text = "This is a very long string that exceeds the maximum line length"
        # Change to:
        long_text = (
            "This is a very long string "
            "that exceeds the maximum line length"
        )
        # OR (use triple quotes sparingly for actual multi-line content):
        # long_text = """
        # This is a very long string
        # that exceeds the maximum line length
        # """
        ```

    * **Function/Method Calls:**
        * Place each parameter on a new line with proper indentation.

        ```python
        result = some_function(param1, param2, param3, param4, param5, param6, keyword1=value1, keyword2=value2)
        # Change to:
        result = some_function(
            param1, param2, param3,
            param4, param5, param6,
            keyword1=value1,
            keyword2=value2,
        )
        ```

    * **Data Structures:**
        * Format each element on a new line.

        ```python
        my_list = [item1, item2, item3, item4, item5, item6, item7, item8, item9, item10]
        # Change to:
        my_list = [
            item1, item2, item3,
            item4, item5, item6,
            item7, item8, item9, item10,
        ]
        ```

    * **Import Statements:**
        * Use parentheses for long `from ... import` statements or multiple separate imports.

        ```python
        from some_module import function1, function2, function3, function4, function5, function6
        # Change to:
        from some_module import (
            function1, function2, function3,
            function4, function5, function6,
        )
        # OR (less common):
        # from some_module import function1
        # from some_module import function2
        # etc.
        ```

4. **Verification:**
    * Run `ruff check <file_path> --select=E501` to verify that line length issues have been resolved.

5. **Prevention:**
    * Configure your IDE to show a vertical ruler at column 100.
    * Set up auto-wrapping for comments in your editor.
    * Review code before committing to identify long lines.
    * Use the provided script for regular checks.

## PR-LINT-03: Undefined Variable Resolution (F821)

**Purpose:** Correct undefined variable errors to prevent runtime exceptions.

**Inputs:** Files with linting errors F821.
**Outputs:** Files with all variables properly defined.

**Steps:**

1. **Identification:**
    * Run `ruff check <directory_or_file> --select=F821` to identify undefined variables.
    * Note the files, line numbers, and variable names.

2. **Analysis:**
    * For each undefined variable, determine:
        * Is it a missing import?
        * Is it a typo?
        * Is it a variable used before definition?
        * Is it a variable that should be passed as a parameter?

3. **Resolution:**
    * **For Missing Imports:**
        * Add the necessary import statement at the top of the file.

    * **For Typos:**
        * Correct the variable name to match the defined variable.

    * **For Variables Used Before Definition:**
        * Move the variable definition before its use.
        * Or restructure the code to ensure the correct definition order.

    * **For Missing Parameters:**
        * Add the variable as a parameter to the function/method.
        * Update function calls to provide the necessary parameter.

4. **Verification:**
    * Run `ruff check <file_path> --select=F821` to verify that all undefined variables have been resolved.
    * Run any relevant tests to ensure functionality is maintained.

5. **Prevention:**
    * Use type hints to clarify variable expectations.
    * Configure your IDE for real-time linting.
    * Ensure code is tested with good coverage.
    * Develop with linting enabled during coding.

## PR-LINT-04: Lint Error Prevention Strategy

**Purpose:** Establish a systematic approach to prevent common linting errors in new code.

**Steps:**

1. **IDE Configuration:**
    * Configure your editor to automatically:
        * Remove trailing whitespace on save.
        * Show whitespace characters.
        * Display a vertical ruler at column 100.
        * Enable real-time linting.

    * **For VSCode (`.vscode/settings.json`):**

        ```json
        {
          "editor.trimTrailingWhitespace": true,
          "editor.renderWhitespace": "boundary",
          "editor.rulers": [100],
          "python.linting.enabled": true,
          "python.linting.ruffEnabled": true,
          "[python]": {
              "editor.defaultFormatter": "charliermarsh.ruff"
          }
        }
        ```

2. **Pre-Commit Hook Configuration:**
    * Install pre-commit: `pip install pre-commit`.
    * Ensure `.pre-commit-config.yaml` exists in the project root with Ruff configured:

        ```yaml
        # .pre-commit-config.yaml
        repos:
        -   repo: https://github.com/astral-sh/ruff-pre-commit
            # Ruff version should be pinned explicitly.
            # See https://astral.sh/ruff/docs/guides/pre-commit#configuration
            rev: v0.4.1 # Or latest appropriate version
            hooks:
            # Run the linter.
            -   id: ruff
                args: [--fix]
            # Run the formatter.
            -   id: ruff-format
        -   repo: https://github.com/pre-commit/pre-commit-hooks
            rev: v4.6.0 # Or latest appropriate version
            hooks:
            -   id: trailing-whitespace
            -   id: end-of-file-fixer
            -   id: check-yaml
            -   id: check-json
        ```

    * Install the hooks: `pre-commit install`.

3. **Development Workflow:**
    * Code with real-time linting enabled in the IDE.
    * Run `ruff check .` and `ruff format .` periodically during development.
    * Allow pre-commit hooks to run and fix issues before finalizing the commit.
    * Address any remaining issues reported by the hooks or CI pipeline.

## Root Cause Analysis

If lint errors persist despite prevention measures:

1. **Identify the Pattern:** Are specific error types recurring? In specific files or subsystems?
2. **Check Configuration:** Verify `.pre-commit-config.yaml`, `pyproject.toml` (Ruff settings), and IDE settings are correct and committed.
3. **Environment Issues:** Ensure the correct Python environment with necessary tools (Ruff, pre-commit) is active.
4. **Workflow Deviation:** Confirm developers are following the standard workflow (IDE checks, pre-commit usage).
5. **Update Documentation/Training:** If a misunderstanding of standards is the cause, update KOIOS documentation or provide clarification.

## Related Tools

* **Ruff:** (`pip install ruff`) - Linter and formatter.
* **Pre-commit:** (`pip install pre-commit`) - Framework for managing pre-commit hooks.
* **`fix_lint_errors.py`:** (`subsystems/KOIOS/tools/`) - Custom script for bulk fixing specific lint issues (use with caution).

---

✧༺❀༻∞ EGOS - KOIOS Process Documentation ∞༺❀༻✧

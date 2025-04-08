---
metadata:
  author: EVA & GUARANI
  backup_required: true
  category: STANDARDS
  description: Standard for creating and maintaining .mdc rule files in Cursor IDE
  documentation_quality: 0.95
  encoding: utf-8
  ethical_validation: true
  last_updated: '2025-04-08'
  related_files:
    - ROADMAP.md
    - subsystems/KOIOS/docs/STANDARDS.md
  required: true
  review_status: approved
  security_level: 0.9
  subsystem: KOIOS
  type: documentation
  version: '1.0'
  windows_compatibility: true
---

# EGOS Standard for `.mdc` Rule Files

**Last Update:** April 8, 2025
**Status:** Active
**Subsystem:** KOIOS
**Version:** 1.0

## Overview

This document defines the standard structure and format for `.mdc` (Markdown Context) rule files within the EGOS project. These files serve as context rules for the AI within the Cursor IDE, providing domain-specific guidance and reinforcing project standards.

## File Location

All `.mdc` files should be stored in the `.cursor/rules/` directory at the project root. This ensures they are automatically loaded when matching files are referenced.

## File Naming Convention

- Use lowercase, underscore-separated naming (snake_case)
- Be descriptive and specific to the rule's purpose
- End with `.mdc` extension
- Examples: `python_logging.mdc`, `commit_messages.mdc`, `subsystem_boundaries.mdc`

## Standard Structure

Each `.mdc` file should follow this structure:

```markdown
---
description: Brief description of the rule's purpose (required)
globs: ["**/*.py"] # File patterns this rule applies to (optional but recommended)
alwaysApply: false # Whether to apply regardless of file match (optional, default false)
---
# Rule Title (KOIOS Standard)

## Rule

Clear and concise statement of the rule.

## Rationale

Explanation of why this rule exists and its importance.

## Examples

### Correct Usage

```python
# Example of code following the rule
```

### Incorrect Usage

```python
# Example of code violating the rule
```

**Closing statement reiterating the rule.**
```

## Required Elements

1. **Frontmatter:** YAML block containing at minimum a description and ideally globs/alwaysApply settings
2. **Title:** H1 heading with rule name and reference to KOIOS
3. **Core Sections:** Rule statement, rationale, and examples
4. **Examples:** Both correct and incorrect usage examples where applicable
5. **Closing Statement:** Brief reinforcement of the rule

## Content Guidelines

1. **Be Specific:** Rules should be clear, unambiguous, and enforceable
2. **Be Concise:** Rules should be easy to understand at a glance
3. **Provide Context:** Include rationale explaining the "why" behind each rule
4. **Show Examples:** Concrete examples help clarify expectations
5. **Target Implementation:** Focus on machine-actionable instructions over verbose explanations
6. **Cross-Reference:** Reference relevant KOIOS standards documents when applicable

## Activation & Usage

For `.mdc` rules to be most effective:

1. Enable Cursor's rules integration in settings (Rules for AI + Include .cursorrules file)
2. Rules are most effective when using Cursor's Agent mode
3. Rules apply to files matching the specified glob patterns
4. Rules marked `alwaysApply: true` will be considered for all files

## Integration with KOIOS Standards

These `.mdc` files should be derived from and reference the comprehensive standards defined in `subsystems/KOIOS/docs/STANDARDS.md`. They serve as targeted, machine-actionable reinforcement of those standards within the development environment.

## Example Files

The following rule files have been implemented:

1. `quantum_prompt_core.mdc`: Core directives for EVA & GUARANI interactions
2. `python_logging.mdc`: Standards for Python logging following KOIOS guidelines
3. `commit_messages.mdc`: Guidelines for Git commits following Conventional Commits
4. `subsystem_boundaries.mdc`: Rules for subsystem interactions via Mycelium
5. `python_documentation.mdc`: Standards for Python docstrings and documentation
6. `error_handling.mdc`: Guidelines for error handling
7. `python_coding_standards.mdc`: General Python best practices
8. `security_practices.mdc`: Security guidelines
9. `smart-tips.mdc`: AI behavior guideline for providing tips
10. `testing_standards.mdc`: Standards for unit and integration tests
11. `git_workflow_standards.mdc`: Standards for Git usage
12. `lessons_learned.mdc`: Guideline for capturing project lessons
13. `ai_interaction_logging.mdc`: Guidelines for logging AI model calls

## Review & Maintenance

`.mdc` rules should be:

1. Reviewed whenever related KOIOS standards are updated
2. Tested to verify they effectively guide AI behavior
3. Updated to reflect evolving project requirements
4. Documented in the project roadmap

---

✧༺❀༻∞ KOIOS - EGOS Standards Authority ∞༺❀༻✧

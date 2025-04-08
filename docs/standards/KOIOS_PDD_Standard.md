# KOIOS Standard: Prompt Design Document (PDD)

**Status:** Draft
**Version:** 0.1
**Owner:** KOIOS Team
**Last Updated:** YYYY-MM-DD

## 1. Introduction

This document defines the standard format and best practices for creating Prompt Design Documents (PDDs) within the EGOS system. PDDs are essential artifacts for managing, versioning, and standardizing the prompts used by the CORUJA subsystem and other AI interaction points.

Adherence to this standard ensures consistency, facilitates validation, enables better prompt management, and supports ethical review processes.

## 2. PDD Purpose

PDDs serve several key purposes:
*   **Standardization:** Define a consistent structure for all prompts.
*   **Clarity:** Clearly document the prompt's intent, parameters, and expected behavior.
*   **Validation:** Allow automated validation of prompt structure via the PDD schema (`subsystems/KOIOS/schemas/pdd_schema.py`).
*   **Versioning:** Track changes to prompts over time.
*   **Discoverability:** Facilitate finding and reusing prompts.
*   **Ethical Governance:** Provide a designated place to specify ETHIK guidelines relevant to the prompt.
*   **Collaboration:** Offer a shared format for teams designing and reviewing prompts.

## 3. PDD File Format and Location

*   **Format:** YAML (`.yaml` extension).
*   **Encoding:** UTF-8.
*   **Location:** Stored within the `docs/prompts/pdds/` directory.
*   **Naming Convention:** Filenames MUST use `snake_case` and correspond directly to the `id` field within the PDD (e.g., `generate_python_docstring.yaml` must contain `id: generate_python_docstring`).

## 4. PDD Schema Definition

The authoritative definition of the PDD structure is the Pydantic model located at `subsystems/KOIOS/schemas/pdd_schema.py`.

*(This section will be expanded to detail each field from the Pydantic model, explaining its purpose, data type, and providing examples, mirroring the template comments.)*

### 4.1. Required Fields

*   `id` (string): ...
*   `name` (string): ...
*   `description` (string): ...
*   `version` (string): ...
*   `parameters` (list[string]): ...
*   `template` (string): ...

### 4.2. Optional Fields

*   `metadata` (object: PddMetadata):
    *   `author` (string|null): ...
    *   `created_date` (string|null): ...
    *   `last_updated` (string|null): ...
    *   `tags` (list[string]): ...
    *   `related_pdds` (list[string]): ...
*   `ethik_guidelines` (object: PddEthikGuidelines):
    *   `pii_handling` (string|null): ...
    *   `bias_mitigation_ref` (string|null): ...
    *   `forbidden_topics` (list[string]): ...
    *   `output_tone` (string|null): ...

## 5. Best Practices for PDD Creation

*(This section will include guidelines on writing effective descriptions, choosing good IDs and names, versioning strategies, writing clear templates, using parameters effectively, and applying meaningful metadata and ETHIK guidelines.)*

## 6. Template

A template file is available at `docs/templates/PDD_Template.yaml`.

## 7. Validation

PDDs are automatically validated against the schema by the `CORUJA.PromptManager` upon loading. Errors will be logged via `KoiosLogger`.

## 8. Version History

*   **v0.1 (YYYY-MM-DD):** Initial draft.

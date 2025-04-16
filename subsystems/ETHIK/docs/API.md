# ETHIK Subsystem - Mycelium API Contracts (v1)

**Version:** 1.0
**Status:** Defined

This document outlines the Mycelium Network message contracts used for interacting with the ETHIK subsystem. All interactions adhere to the standards defined in `.cursor/rules/api_design_contracts.mdc`.

## 1. Overview

Subsystems interact with ETHIK primarily for two purposes:

1.  **Validation:** To check if a proposed action, data, or content adheres to defined ethical rules.
2.  **Sanitization:** To clean or modify content to remove or flag ethically problematic elements.

Communication occurs via specific Mycelium topics, with payloads defined by Pydantic models located in `subsystems/MYCELIUM/schemas/ethik_contracts.py`.

## 2. Validation API

### 2.1. Request Validation

*   **Topic:** `request.ethik.validate.v1`
*   **Purpose:** Request validation of an action or content against ETHIK rules.
*   **Sender:** Any subsystem requiring ethical validation (e.g., CORUJA before executing an AI action, a user input handler).
*   **Receiver:** ETHIK (`EthikValidator` component via `EthikService`).
*   **Payload Schema:** `EthikValidationRequestV1` (see `subsystems/MYCELIUM/schemas/ethik_contracts.py`)
    *   `request_id`: Unique ID for tracking.
    *   `action_context`: Dictionary describing the action/content.
    *   `params` (Optional): Additional parameters for validation logic.
    *   `rule_ids` (Optional): Specific rules to apply (defaults to standard ruleset).
*   **Response:** Via `response.ethik.validate.v1.{request_id}` topic.

### 2.2. Validation Response

*   **Topic:** `response.ethik.validate.v1.{request_id}` (where `{request_id}` matches the request)
*   **Purpose:** Provide the result of an ETHIK validation request.
*   **Sender:** ETHIK (`EthikValidator` component via `EthikService`).
*   **Receiver:** The original requesting subsystem.
*   **Payload Schema:** `EthikValidationResponseV1` (see `subsystems/MYCELIUM/schemas/ethik_contracts.py`)
    *   `request_id`: Matches the original request ID.
    *   `is_valid`: Boolean result of the validation.
    *   `action_taken`: Action ETHIK determined (e.g., 'allowed', 'blocked').
    *   `severity` (Optional): Severity if invalid/warning.
    *   `score` (Optional): Numerical score.
    *   `details`: List of violation/warning details.
    *   `error` (Optional): Error message if validation process failed.

## 3. Sanitization API

### 3.1. Request Sanitization

*   **Topic:** `request.ethik.sanitize.v1`
*   **Purpose:** Request sanitization of text content.
*   **Sender:** Any subsystem handling potentially sensitive or problematic text (e.g., CORUJA before logging AI output, a data ingestion pipeline).
*   **Receiver:** ETHIK (`EthikSanitizer` component via `EthikService`).
*   **Payload Schema:** `EthikSanitizationRequestV1` (see `subsystems/MYCELIUM/schemas/ethik_contracts.py`)
    *   `request_id`: Unique ID for tracking.
    *   `content`: The text content to sanitize.
    *   `context` (Optional): Context about the content.
    *   `rule_ids` (Optional): Specific rules to apply (defaults to standard ruleset).
*   **Response:** Via `response.ethik.sanitize.v1.{request_id}` topic.

### 3.2. Sanitization Response

*   **Topic:** `response.ethik.sanitize.v1.{request_id}` (where `{request_id}` matches the request)
*   **Purpose:** Provide the result of content sanitization.
*   **Sender:** ETHIK (`EthikSanitizer` component via `EthikService`).
*   **Receiver:** The original requesting subsystem.
*   **Payload Schema:** `EthikSanitizationResponseV1` (see `subsystems/MYCELIUM/schemas/ethik_contracts.py`)
    *   `request_id`: Matches the original request ID.
    *   `sanitized_content`: The content after sanitization.
    *   `actions_taken`: List detailing specific changes made.
    *   `error` (Optional): Error message if sanitization process failed.

---
✧༺❀༻∞ EGOS ∞༺❀༻✧
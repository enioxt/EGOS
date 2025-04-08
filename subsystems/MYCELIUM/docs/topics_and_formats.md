# MYCELIUM NATS Topics & Payload Formats

**Version:** 1.0
**Date:** 2025-04-08
**Status:** Initial Draft

## 1. Introduction

This document defines the standard NATS subject (topic) naming conventions and the common JSON payload structure for messages transmitted over the MYCELIUM Network within EGOS. Adherence to these standards is crucial for ensuring consistent and reliable inter-subsystem communication.

## 2. Standard Payload Format

All messages published to MYCELIUM should adhere to the following JSON structure:

```json
{
  "message_id": "string (UUID recommended)",   // Unique identifier for this specific message instance
  "timestamp": "string (ISO 8601 format)", // Time the message was generated (UTC)
  "source_subsystem": "string",              // Name of the originating subsystem (e.g., "CORUJA", "CRONOS")
  "correlation_id": "string | null",       // Optional: UUID to link responses back to requests
  "payload": {                            // Object containing the specific data for the message
    // Subsystem-specific data structure goes here...
  },
  "metadata": {                           // Optional: Object for additional metadata
    // e.g., "priority": "high", "trace_id": "...", "schema_version": "1.0"
  }
}
```

*   **`message_id`**: MUST be unique for each message sent.
*   **`timestamp`**: MUST be in ISO 8601 format and UTC.
*   **`source_subsystem`**: MUST accurately identify the sender.
*   **`correlation_id`**: SHOULD be included in request messages to allow receivers to link their responses. Responses SHOULD include the `correlation_id` from the original request.
*   **`payload`**: The structure of this object is message-specific and should be documented by the interacting subsystems. Consider using JSON Schemas for validation.
*   **`metadata`**: Use for cross-cutting concerns or contextual information not part of the core payload.

## 3. NATS Subject Naming Convention

NATS subjects use a dot-separated hierarchical structure. The standard EGOS convention is:

**`<type>.<context>.<action_or_event>`**

*   **`<type>`**: Defines the nature of the message. Common types:
    *   `request`: For Request/Reply interactions (sent by the requester).
    *   `event`: For Publish/Subscribe notifications about occurrences.
    *   `log`: For publishing log messages system-wide.
    *   *Note:* NATS handles response routing implicitly via reply subjects, so a `response` type might not be strictly necessary at the subject level but can be indicated via `correlation_id`.
*   **`<context>`**: Provides scope. Typically:
    *   The target subsystem for `request` types (e.g., `ethik`, `coruja`).
    *   The source subsystem for `event` or `log` types (e.g., `cronos`, `koios`).
    *   Can be hierarchical for more detail (e.g., `cronos.backup`, `ethik.validate`).
*   **`<action_or_event>`**: Specifies the concrete action or event.
    *   For `request`: Verb describing the desired action (e.g., `create`, `get`, `validate`).
    *   For `event`: Past-tense verb describing what happened (e.g., `started`, `completed`, `failed`, `updated`).
    *   For `log`: The log level (e.g., `error`, `warning`, `info`, `debug`).

Subsystems can use NATS wildcards (`*` for single level, `>` for multi-level) in their subscriptions:
*   `request.ethik.validate.*`: Subscribe to all validation requests for ETHIK.
*   `event.cronos.backup.*`: Subscribe to all backup-related events from CRONOS.
*   `log.koios.>`: Subscribe to all logs from KOIOS.

## 4. Initial Core Subjects

This is a non-exhaustive list of initial subjects expected for core functionality. This list will expand as development progresses.

*   **ETHIK:**
    *   `request.ethik.validate.pii`
    *   `request.ethik.validate.content`
    *   `event.ethik.policy.updated`
*   **CORUJA:**
    *   `request.coruja.orchestrate.pdd`
    *   `event.coruja.orchestration.started`
    *   `event.coruja.orchestration.completed`
    *   `event.coruja.orchestration.failed`
*   **CRONOS:**
    *   `request.cronos.backup.create`
    *   `request.cronos.state.get`
    *   `request.cronos.state.set`
    *   `event.cronos.backup.started`
    *   `event.cronos.backup.completed`
    *   `event.cronos.backup.failed`
    *   `event.cronos.state.changed`
*   **KOIOS:**
    *   `log.koios.error`
    *   `log.koios.warning`
    *   `log.koios.info`
    *   `log.koios.debug`
    *   `request.koios.search.docs`
    *   `request.koios.validate.schema`
*   **NEXUS:**
    *   `request.nexus.analyze.dependencies`
    *   `event.nexus.analysis.completed`
*   **ATLAS:**
    *   `request.atlas.visualize.map`
    *   `event.atlas.map.updated`

## 5. Schema Definitions

*(Placeholder: Links to JSON Schemas defining the `payload` structure for specific subjects will be added here or managed within subsystem documentation.)*

---

✧༺❀༻∞ EGOS ∞༺❀༻✧

---
metadata:
  author: "[Your Name/Team or EGOS AI Assistant]"
  backup_required: true
  category: API_DOCUMENTATION
  description: "API contract definitions for the [System/Subsystem Name] [API Type e.g., Mycelium Interface, REST API]."
  documentation_quality: 0.1 # Initial draft quality
  encoding: utf-8
  ethical_validation: false
  last_updated: 'YYYY-MM-DD'
  related_files:
    - subsystems/[SUBSYSTEM_NAME]/README.md # Link to the relevant subsystem README
    - subsystems/MYCELIUM/schemas/[schema_file.py] # Link to Pydantic schemas if applicable
    # Add links to architecture docs, usage examples, etc.
  required: false # Required only when a subsystem exposes a formal API
  review_status: draft # draft | under_review | approved
  security_level: 0.5 # API details can be sensitive
  subsystem: "[SUBSYSTEM_NAME_UPPERCASE]"
  type: documentation
  version: '1.0.0' # API Version
  windows_compatibility: true
---

# API Documentation: [System/Subsystem Name] - [API Type e.g., Mycelium Interface v1]

**Version:** [Version from metadata, e.g., 1.0]
**Status:** [API Status: e.g., Proposed, Defined, Implemented, Deprecated]

## 1. Overview

*   **Purpose:** Describe the overall purpose of this API. What functionality does it expose?
*   **API Style:** Specify the style (e.g., Asynchronous Messaging via Mycelium, RESTful HTTP, GraphQL).
*   **Base URL / Topic Namespace:** Define the base URL for HTTP APIs or the root topic namespace for messaging APIs (e.g., `request.subsystem.`).
*   **Authentication (If applicable):** How are requests authenticated? (e.g., API Keys, JWT, Mycelium security context).
*   **Schema Definitions:** Where are the detailed request/response schemas defined? (e.g., "Pydantic models in `subsystems/MYCELIUM/schemas/schema_file.py`", "OpenAPI specification at `/api/openapi.json`"). Reference `.cursor/rules/api_design_contracts.mdc`.

## 2. [Endpoint/Topic Group 1 Name, e.g., Validation API]

[Group related endpoints or message topics together.]

### 2.1 [Endpoint/Topic 1 Name, e.g., Request Validation]

*   **Endpoint/Topic:** `[Full topic name or URL path, e.g., request.ethik.validate.v1, /api/v1/validate]`
*   **Method (If applicable):** `[HTTP Method, e.g., POST, GET]`
*   **Purpose:** Briefly describe what this specific endpoint/topic does.
*   **Sender(s):** [Which subsystems/clients initiate this request?]
*   **Receiver(s):** [Which subsystem/service handles this request?]
*   **Request Payload:**
    *   **Schema:** `[Reference to Pydantic Model or Schema Definition, e.g., EthikValidationRequestV1]`
    *   **Description:** Briefly describe the payload structure or link to the schema definition.
    *   **Example:**
        ```json
        {
          "request_id": "uuid-...",
          "field1": "value1",
          "field2": { ... }
        }
        ```
*   **Response Payload / Response Topic:**
    *   **Success (e.g., 200 OK / `response.topic.v1.{request_id}`):**
        *   **Schema:** `[Reference to Success Schema, e.g., EthikValidationResponseV1]`
        *   **Description:** Describe the success response.
        *   **Example:**
            ```json
            {
              "request_id": "uuid-...",
              "result_field": "result_value"
            }
            ```
    *   **Error (e.g., 4xx/5xx / Separate Error Topic):**
        *   **Schema:** `[Reference to Error Schema, e.g., ErrorResponseV1]`
        *   **Description:** Describe common error responses.
        *   **Example:**
            ```json
            {
              "error_code": "VALIDATION_ERROR",
              "message": "Invalid input provided."
            }
            ```
*   **Notes (Optional):** Any specific behaviors, rate limits, or considerations.

### 2.2 [Endpoint/Topic 2 Name, e.g., Validation Response]

*   **Endpoint/Topic:** `[e.g., response.ethik.validate.v1.{request_id}]`
*   **Purpose:** ...
*   **Sender(s):** ...
*   **Receiver(s):** ...
*   **Payload Schema:** ...
*   **Example:** ...

## 3. [Endpoint/Topic Group 2 Name, e.g., Sanitization API]

### 3.1 [Endpoint/Topic 3 Name, e.g., Request Sanitization]

*   **Endpoint/Topic:** ...
*   ... (Repeat structure as above)

## 4. Common Data Structures / Schemas (Optional)

[If there are common data structures used across multiple endpoints/topics, define or reference them here.]

*   **`SchemaName`:** [Description or reference to definition]

## 5. Error Handling

[Describe the general approach to error handling. List common error codes or message structures.]

---
✧༺❀༻∞ EGOS ∞༺❀༻✧
# ETHIK Subsystem README

**Version:** 8.0.0
**Status:** Active (Core Logic Standardization in Progress)

## Overview

ETHIK is the ethical framework and validation subsystem for the **EGOS** project. Its purpose is to ensure that all system operations, data handling, and AI interactions adhere to predefined ethical principles and standards.

## Role in Dynamic Roadmap Sync & EGOS Interconnection

ETHIK is responsible for:
- Auditing all roadmap sync actions for security, privacy, and ethical compliance.
- Validating that all inter-subsystem communication and roadmap updates adhere to EGOS ethical standards.
- Collaborating with KOIOS, MYCELIUM, and CRONOS to ensure a verifiable, ethical, and secure sync process.

Cross-reference: See ROADMAP.md sections "Dynamic Roadmap Sync & Mycelium Interconnection" and "Technical Implementation Plan: Dynamic Roadmap Sync (Phase 1)".

## Core Components

* **`EthikValidator` (`core/validator.py`):** Responsible for validating actions, data, or configurations against a set of ethical rules and principles.
  * KOIOS standardization completed ✓
  * Standardized placeholder implementation with comprehensive error handling
  * Loads rules from a configuration file (`config/ethik_rules.json`)
  * Provides `validate_action()` async method to check input against rules
  * Integrates with Mycelium (placeholder handlers) to listen for validation requests (`request.ethik.validate`) and publish results.
* **`EthikSanitizer` (`core/sanitizer.py`):** Responsible for sanitizing content (e.g., text, code) to remove or flag ethically problematic elements based on defined rules.
  * Loads sanitization rules (including regex patterns and replacements) from `config/sanitization_rules.json`.
  * Provides `sanitize_content()` method (and async version).
  * Uses a cache (`content_cache`) and priority queue for performance.
  * Maintains a history of sanitization actions.
  * Integrates with Mycelium to listen for sanitization requests (`request.ethik.sanitize`) and publish results (`response.sanitization.<request_id>`).
* **`EthikService` (`service.py`):** Wraps the Validator and Sanitizer, manages their lifecycle, handles configuration loading, and initializes the Mycelium interface for them.
  * Provides `start()` and `stop()` methods to manage the service and its components.
  * Coordinates the interaction between core logic components and the Mycelium network.
* **`config/`:** Contains configuration files:
  * `ethik_config.json`: Main configuration for the EthikService, including Mycelium topics, component settings, etc.
  * `ethik_rules.json`: Defines the rules used by the `EthikValidator`.
  * `sanitization_rules.json`: Defines the rules used by the `EthikSanitizer`.
* **`tests/`:** Contains unit tests for the validator, sanitizer, and service.

## Key Features

* **Rule-Based Validation:** Allows defining flexible ethical rules in JSON format.
* **Content Sanitization:** Provides automated detection and replacement of content based on configurable rules.
* **Mycelium Integration:** Enables decentralized validation and sanitization requests/responses across the EGOS system.
* **Caching & History:** Optimizes performance for repeated sanitization requests and maintains an auditable history.
* **Configurable:** Rules and service behavior can be adjusted via configuration files.

## Integration

* **Mycelium:** ETHIK heavily relies on Mycelium for communication. Other subsystems can request validation or sanitization by publishing messages to the appropriate topics (defined in `ethik_config.json`).
* **KOIOS:** Uses `KoiosLogger`. ETHIK rules and configurations should adhere to KOIOS standards.
* **Other Subsystems:** Any subsystem performing actions or handling data that requires ethical review should integrate with ETHIK by sending requests via Mycelium.

## Current Status & Next Steps

* KOIOS standardization in progress:
  * `core/validator.py` fully standardized with placeholder implementations ✓
  * Other components pending standardization
* Core validation logic implementation planned for Q3 2025
* Mycelium integration (placeholders prepared in validator)
* Next steps:
  * Continue standardization of remaining ETHIK components
  * Implement actual validation logic (replacing placeholders)
  * Create standard rule templates and evaluation strategies
  * Develop comprehensive test suite for validation rules
  * Refine documentation (docstrings, comments)

## Usage Examples

### Direct Component Usage (Conceptual)

This shows direct interaction with the core components, bypassing the `EthikService` and Mycelium. This might be useful for testing or specific integrated scenarios.

```python
import asyncio
from subsystems.ETHIK.core.sanitizer import EthikSanitizer
from subsystems.ETHIK.core.validator import EthikValidator

# Assume config dictionaries are loaded from json files
sanitizer_config = {...} # Load from sanitization_rules.json conceptually
validator_config = {...} # Load from ethik_rules.json conceptually

# Initialize components directly
sanitizer = EthikSanitizer(config=sanitizer_config)
sanitizer.load_rules() # Ensure rules are loaded

validator = EthikValidator(config=validator_config)
validator.load_rules()

# Example Sanitization
async def run_sanitize():
    original_text = "This is some example text with a potentially problematic word."
    result = await sanitizer.sanitize_content_async(original_text)
    print(f"Original: {original_text}")
    print(f"Sanitized: {result.sanitized_content}")
    print(f"Actions: {result.actions_taken}")

# asyncio.run(run_sanitize())

# Example Validation
async def run_validation():
    action_context = {
        "action_type": "create_resource",
        "level": "high",
        "content": "Creating a sensitive resource",
        "affected_components": ["data_storage"]
    }
    params = {}  # Additional parameters (if needed)
    result = await validator.validate_action(action_context, params)

    print(f"Validation for action: {action_context['action_type']}")
    print(f"Valid: {result.is_valid}")
    print(f"Action taken: {result.action_taken}")
    print(f"Severity: {result.severity}")
    print(f"Score: {result.score}")
    print(f"Details: {result.details}")

# asyncio.run(run_validation())
```

### Mycelium Interaction (Conceptual)

This demonstrates how another subsystem (e.g., `ExampleService`) might request sanitization via Mycelium.

```python
import asyncio
import uuid
from mycelium.client import MyceliumClient # Assuming MyceliumClient exists

async def request_sanitization(client: MyceliumClient, text_to_sanitize: str):
    request_id = str(uuid.uuid4())
    request_topic = "request.ethik.sanitize" # Topic defined in ethik_config.json
    response_topic = f"response.sanitization.{request_id}"

    # Prepare payload
    payload = {
        "request_id": request_id,
        "content": text_to_sanitize,
        "context": {"source": "ExampleService"}
    }

    # Subscribe to the response topic *before* publishing
    # (Implementation detail: Need a mechanism to wait for the specific response)
    print(f"Subscribing to {response_topic}")
    # await client.subscribe(response_topic, handle_sanitization_response)

    print(f"Publishing request {request_id} to {request_topic}")
    await client.publish(request_topic, payload)

    print(f"Waiting for response on {response_topic}...")
    # Add logic here to wait for and process the response message
    # e.g., using a future or callback mechanism provided by MyceliumClient

async def handle_sanitization_response(message):
    # Process the SanitizationResult received in the message payload
    print(f"Received Sanitization Response: {message.payload}")
    # Potentially set a future or trigger further actions
    pass

# Example Usage (Conceptual - Requires running Mycelium and EthikService)
# async def main():
#     mycelium_client = MyceliumClient()
#     await mycelium_client.connect()
#     await request_sanitization(mycelium_client, "Sanitize this sensitive content.")
#     await mycelium_client.disconnect()
#
# asyncio.run(main())
```

## Usage (Conceptual via Mycelium)

1. **Requesting Validation:**
    * Publish a message to the `request.ethik.validate` topic.
    * Payload should contain:
      ```json
      {
        "request_id": "unique-id",
        "action_context": {
          "action_type": "create_resource",
          "level": "high",
          "content": "Description of action",
          "affected_components": ["component1", "component2"]
        },
        "params": {},
        "rule_ids": ["optional-specific-rule-id"]
      }
      ```
    * Listen on `response.validation.<request_id>` for the ValidationResult.

2. **Requesting Sanitization:**
    * Publish a message to the `request.ethik.sanitize` topic.
    * Payload should contain `{"content": "Text to sanitize...", "context": {...}}`.
    * Include a unique request ID.
    * Listen on `response.sanitization.<request_id>` for the `SanitizationResult` (or error).

*(Refer to `EthikService` and core components for specific payload structures)*

## Contributing

Please follow KOIOS standards. Contributions to the ethical rule sets require careful consideration and review.

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧

---
metadata:
  author: EVA & GUARANI
  backup_required: true
  category: STANDARDS
  description: Guidelines for providing feedback (logging, progress) from operational scripts within EGOS.
  documentation_quality: 0.5 # Initial Draft
  encoding: utf-8
  ethical_validation: false # Standard definition
  last_updated: '2025-04-03' # Current date
  related_files:
    - subsystems/KOIOS/docs/STANDARDS.md
    - subsystems/KOIOS/core/logger.py
  required: true # Core standard
  review_status: draft
  security_level: 0.5 # Public standard
  subsystem: KOIOS
  type: documentation
  version: '0.1'
  windows_compatibility: true
---

# KOIOS Standard: Script Feedback and Progress Reporting

**Version:** 0.1
**Status:** Draft
**Last Updated:** 2025-04-03

## 1. Objective

This standard defines how scripts within the EGOS ecosystem (e.g., maintenance scripts, validation tools, batch processors) should provide feedback to the user and log their progress. Consistent feedback mechanisms improve usability, debugging, and monitoring.

## 2. Core Principles

*   **Clarity:** Feedback should be easy to understand.
*   **Appropriate Verbosity:** Provide enough detail without overwhelming the user. Use standard logging levels.
*   **Progress Indication:** For long-running tasks, provide clear progress indicators.
*   **Standardization:** Use consistent tools and formats via KOIOS.

## 3. Guidelines

### 3.1 Logging

*   **Use `KoiosLogger`:** All script output intended for operational logging MUST use the central `KoiosLogger`.
*   **Standard Log Levels:** Adhere to standard Python logging levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) as defined in the main KOIOS Logging Standard.
    *   `INFO`: General progress milestones, start/end of major phases.
    *   `DEBUG`: Detailed information useful for debugging.
    *   `WARNING`: Potential issues or recoverable errors.
    *   `ERROR`: Errors that prevent a specific part of the script from completing but allow the script to continue.
    *   `CRITICAL`: Errors that force the script to terminate prematurely.
*   **Context:** Include relevant context in log messages (e.g., file being processed, item ID).

### 3.2 Progress Reporting (For Long-Running Tasks)

*   **Recommended Tool:** Utilize libraries like `tqdm` or `rich.progress` for displaying progress bars in the console for iterative or multi-step tasks.
*   **Integration with Logging:** Ensure progress reporting does not excessively clutter logs. Log major milestones (e.g., "Processed 1000 / 5000 items") rather than every single increment if using progress bars.
*   **Configuration:** Allow disabling verbose progress reporting via configuration if appropriate.

## 4. Examples

*(Placeholder: Add concrete examples using KoiosLogger and tqdm/rich)*

```python
# Example using KoiosLogger and tqdm (Conceptual)
from koios.logger import KoiosLogger
from tqdm import tqdm
import time

logger = KoiosLogger.get_logger("EXAMPLE_SCRIPT")

def run_long_task(items):
    logger.info(f"Starting task with {len(items)} items.")
    results = []
    # Use tqdm for progress bar in console
    for item in tqdm(items, desc="Processing Items"):
        try:
            # Simulate work
            time.sleep(0.1)
            result = item * 2
            results.append(result)
            # Optional: Log progress milestones less frequently
            if len(results) % 10 == 0:
                 logger.debug(f"Processed {len(results)} items.")
        except Exception as e:
            logger.error(f"Failed to process item {item}: {e}")
            # Decide whether to continue or raise

    logger.info(f"Task completed. Processed {len(results)} items successfully.")
    return results

# run_long_task(list(range(50)))
```

## 5. Compliance

Adherence to this standard is mandatory for scripts intended for operational use within EGOS. KOIOS validation tools may check for appropriate logger usage in the future.

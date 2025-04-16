---
metadata:
  author: "[Your Name/Team or EGOS AI Assistant]"
  backup_required: true # Or false if not critical state
  category: SUBSYSTEM_DOCUMENTATION
  description: "[Concise 1-2 sentence description of the subsystem's purpose and core function]"
  documentation_quality: 0.1 # Initial draft quality
  encoding: utf-8
  ethical_validation: false # Usually false for READMEs
  last_updated: 'YYYY-MM-DD' # Date of last significant update
  related_files:
    - docs/MQP.md
    - ROADMAP.md
    - .cursor/rules/[relevant_rule_1.mdc]
    - subsystems/[dependency_subsystem_1]/README.md
    - subsystems/[dependency_subsystem_2]/README.md
    # Add paths to key internal files/docs if applicable
  required: true # Usually true for core subsystem READMEs
  review_status: draft # draft | under_review | approved
  security_level: 0.5 # Adjust based on content sensitivity (0.0 public -> 1.0 highly sensitive)
  subsystem: "[SUBSYSTEM_NAME_UPPERCASE]" # e.g., NEXUS, CORUJA
  type: documentation
  version: '0.1.0' # Initial version
  windows_compatibility: true # Or false if specific OS dependencies exist
---

# [Subsystem Emoji (Optional)] [SUBSYSTEM_NAME] Subsystem

**Version:** [Version from metadata]
**Status:** [Development Status: e.g., Planning, In Development, Alpha, Beta, Active]

## 1. Overview

[Provide a paragraph elaborating on the subsystem's purpose within the EGOS ecosystem. What problem does it solve? What is its primary role? Reference the MQP if relevant.]

## 2. Core Responsibilities

[Use a bulleted list to detail the key functions and responsibilities of this subsystem.]

*   Responsibility 1: [Description]
*   Responsibility 2: [Description]
*   ...

## 3. Core Components

[Describe the main classes, modules, or services within this subsystem. Briefly explain the purpose of each.]

*   **`ComponentName1` (`path/to/component1.py`):** [Description of its role and function.]
*   **`ComponentName2` (`path/to/component2.py`):** [Description of its role and function.]
*   **`config/` (Optional):** [Describe key configuration files if applicable.]
*   **`docs/` (Optional):** [Mention key internal documentation if applicable.]
*   **`tests/`:** [Briefly state that unit/integration tests reside here.]

## 4. Key Features (Optional)

[Highlight any particularly important or unique features of the subsystem.]

*   Feature 1: [Description]
*   Feature 2: [Description]

## 5. Integration Points

[Describe how this subsystem interacts with other parts of EGOS.]

*   **Consumers:** [Which subsystems or components consume services/data from this subsystem? How?]
    *   Subsystem A: [Via Mycelium topic `topic.name`, via direct API call (if allowed), etc.]
*   **Providers/Dependencies:** [Which subsystems or external services does this subsystem depend on? How?]
    *   **Mycelium:** [Describe reliance on Mycelium for receiving requests or publishing results. Mention key topics.]
    *   **KOIOS:** [Describe reliance on KOIOS for logging, standards, configuration, etc.]
    *   **ETHIK:** [Describe how/when ETHIK is called for validation/sanitization.]
    *   **Subsystem B:** [Describe dependency, e.g., uses data processed by Subsystem B.]
    *   **External APIs/Libraries:** [List key external dependencies.]
*   **Configuration Source:** [Where does it get its configuration (e.g., `config/`, environment variables)?]

## 6. Configuration

[Detail the necessary configuration settings for this subsystem.]

*   **Environment Variables:** [List required environment variables.]
*   **Configuration Files:** [List key configuration files (e.g., `config/subsystem_config.json`) and briefly describe their purpose.]
*   **Secrets Management:** [How are secrets (API keys, passwords) managed? (Should align with security practices)]

## 7. Current Status & Next Steps

*   **Current Status:** [Brief summary of the subsystem's maturity and stability.]
*   **Known Issues/Limitations:** [List any significant known issues or limitations.]
*   **Planned Features/Improvements (Next Steps):** [Bulleted list of items from the ROADMAP or immediate plans.]
    *   [Task ID (Optional)]: [Description]
    *   [Task ID (Optional)]: [Description]

## 8. Usage Examples (Optional)

[Provide brief code snippets or descriptions showing how to interact with the subsystem, either directly (for testing) or via its primary interface (e.g., Mycelium).]

### Example 1: [Scenario Description]

```python
# Code example
```

### Example 2: [Scenario Description]

```bash
# Command line example (if applicable)
```

## 9. Contributing

[Link to `CONTRIBUTING.md`. Add any subsystem-specific contribution guidelines if necessary.]

---
✧༺❀༻∞ EGOS ∞༺❀༻✧
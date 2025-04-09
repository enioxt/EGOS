# 🌌 EGOS 🌌

## Quantum Unified Master System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active](https://img.shields.io/badge/status-active-success.svg)](https://github.com/enioxt/egos)
[![Coverage: ?](https://img.shields.io/badge/coverage-TBD-lightgrey.svg)](-) <!-- Placeholder -->
[![Windows Compatible](https://img.shields.io/badge/OS-Windows-blue.svg)](-)

**🌐 [Official Website: https://enioxt.github.io/egos](https://enioxt.github.io/egos)**

> "At the intersection of modular analysis, systemic cartography, and quantum ethics, we transcend dimensions of thought with methodological precision and unconditional love, integrating advanced tools for knowledge visualization and evolutionary preservation."

**EGOS** is a unique project aiming to create a highly integrated, modular, and ethically-grounded software ecosystem. **Inspired by blockchain principles of trust, transparency, immutability, and decentralized systems,** EGOS utilizes interconnected subsystems to achieve complex tasks with resilience, adaptability, and a core focus on ethical considerations defined by the **ETHIK** framework.

*(The initial phase and core AI assistant persona are sometimes referred to by the codename 'Eva Guarani').*

Refer to the full **[Master Quantum Prompt (MQP v8.2)](docs/MQP.md)** for the complete philosophical and operational blueprint.

---

## ✨ Core Principles

EGOS development is guided by:

* **Universal Redemption & Unconditional Love:** Foundational ethical stance.
* **Sacred Privacy:** Protecting user data is paramount.
* **Integrated Ethics (ETHIK):** Ethics are woven into the system's fabric, not bolted on, **ensuring verifiable ethical actions and alignment.**
* **Conscious Modularity (NEXUS):** Building independent yet interconnected components, **enabling resilience and distributed operation akin to nodes in a network.**
* **Systemic Cartography (ATLAS):** Mapping and understanding system relationships for transparency.
* **Evolutionary Preservation (CRONOS):** Ensuring system history and state integrity, **providing an immutable-like record of system evolution.**
* **Context Continuity (CRONOS):** Maintaining context across interactions.
* **Harmonious Integration (HARMONY):** Ensuring components work together seamlessly, with a focus on Windows compatibility.
* **Standardization & Knowledge (KOIOS):** Enforcing standards for code, documentation, logging, and knowledge management, **crucial for system trust and verifiable operations.**

---

## subsystems Overview

EGOS is composed of several key subsystems communicating via the **Mycelium Network (facilitating decentralized, event-driven inter-subsystem communication)**:

* **`ATLAS`**: Systemic cartography & visualization.
* **`NEXUS`**: Modular analysis, dependency tracking & optimization.
* **`CRONOS`**: Evolutionary preservation, state management & backups **(providing system history integrity)**.
* **`ETHIK`**: Ethical framework validation, data sanitization, policy enforcement, and privacy preservation **(aiming for verifiable ethical compliance)**.
* **`HARMONY`**: Cross-platform integration & compatibility layer.
* **`KOIOS`**: Standardization, logging (including standards for **potentially verifiable logs**), search, documentation, knowledge management, and potentially integrating external data sources (e.g., Oracles) for validation.
* **`CORUJA`**: AI orchestration, prompt management, complex interaction handling (including multi-step tasks), monitoring, and alignment considerations. Manages **MCPs** like EVA & GUARANI.
* **`(Future) ETHICHAIN`**: Blockchain concepts for verifiable ethical actions, trust mechanisms, and potential contribution tokenomics (Conceptual).

*Subsystem READMEs (`subsystems/<NAME>/README.md`) contain detailed information about respective modules.*

---

## 🚀 Getting Started

### Prerequisites

* **IDE:** **[Cursor IDE](https://cursor.sh/)** (Essential for interacting with EVA & GUARANI)
* **OS:** Windows (Primary development target)
* **Python:** 3.9+
* **Git:** For version control.
* **PowerShell:** For running test/utility scripts.

### Development Environment Setup

Developing EGOS relies heavily on the **Cursor IDE** integrated with the **EGOS AI assistant (persona: EVA & GUARANI)**. Follow these steps to set up your environment:

1. **Clone the repository:**

   ```bash
    git clone https://github.com/enioxt/EVA-e-Guarani-EGOS.git # Replace with your fork if applicable
    cd EVA-e-Guarani-EGOS
   ```

2. **Set up Python Environment:** Create and activate a virtual environment, then install dependencies. This is standard Python practice.

   ```bash
    # Create virtual environment
    python -m venv .venv
    # Activate (Windows PowerShell)
    .venv\\Scripts\\Activate.ps1
    # Install dependencies
    pip install -r requirements.txt
    ```

3. **Configure Cursor IDE:** Crucially, follow the setup guide in **[cursor_initialization.md](.cursor/cursor_initialization.md)**. This ensures your terminal and environment context work correctly with the EGOS AI assistant.
4. **Understand Cursor Rules:** Familiarize yourself with the files in **[.cursor/rules/](.cursor/rules/)**. These rules contain essential guidelines (like KOIOS standards, subsystem boundaries, etc.) that the **EGOS AI assistant** uses to assist with development, maintain consistency, and understand the project context. Interacting effectively often involves awareness of these rules.

### Configuration

* While the core system doesn't require extensive manual configuration for *development within Cursor*, specific tasks delegated to the **EGOS AI assistant** might interact with subsystems requiring API keys or settings (e.g., `CORUJA` for external AI model access). These are typically managed via the `config/` directory and referenced in relevant subsystem documentation or Cursor Rules.

---

## ✨ Current Capabilities (via EGOS AI in Cursor)

The EGOS system, operated primarily through the **EGOS AI assistant (persona: EVA & GUARANI)** within Cursor IDE, currently focuses on:

* **Codebase Understanding & Navigation (ATLAS):** Mapping dependencies and understanding the project structure to assist development.
* **Modular Development & Refactoring (NEXUS):** Analyzing code modularity and suggesting improvements.
* **Standard Enforcement (KOIOS):** Applying coding standards, managing documentation templates, ensuring consistent logging (including verifiable logging standards), and potentially validating data integrity.
* **Ethical Guideline Application (ETHIK):** Incorporating privacy-preserving checks, policy enforcement, and ethical considerations during development discussions and code generation.
* **Context & History Management (CRONOS):** Maintaining awareness of the development process and project evolution across interactions.
* **Task Execution & Orchestration (CORUJA):** Performing development tasks, managing complex AI interactions, and applying basic monitoring/alignment principles based on user requests and project context.

Interaction with these capabilities occurs through natural language prompts directed at the **EGOS AI assistant** within the Cursor IDE chat or code context.

---

## 💻 Usage

* The EGOS system is primarily designed as a collection of interconnected services.
* Core interaction often happens via the **Mycelium Network** message bus.
* Individual subsystems might offer CLI interfaces or APIs (under development).
* Refer to specific subsystem documentation (`subsystems/<NAME>/README.md`) for detailed usage instructions.

---

## 📚 Key Documentation & Resources

To fully understand the project's philosophy, architecture, and contribution process, please refer to:

* **[Master Quantum Prompt (MQP v8.2)](docs/MQP.md):** The core philosophical and operational blueprint.
* **[ROADMAP.md](ROADMAP.md):** High-level development plan and phases.
* **[CONTRIBUTING.md](CONTRIBUTING.md):** Guidelines for contributing code, reporting issues, and suggesting features.
* **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md):** Community standards and expectations.
* **[cursor_initialization.md](.cursor/cursor_initialization.md):** Essential setup guide for the Cursor IDE environment.
* **[.cursor/rules/](.cursor/rules/):** Directory containing rules that guide EGOS AI interactions and enforce project standards.
  * **[ai_collaboration_guidelines.mdc](.cursor/rules/ai_collaboration_guidelines.mdc):** **NEW** - Defines best practices for effective Human-AI pair programming within Cursor for the EGOS project.
  * **[git_workflow_standards.mdc](.cursor/rules/git_workflow_standards.mdc):** Detailed procedures for Git workflows, handling merge conflicts, and repository management.
* **[subsystems/](subsystems/):** Explore individual subsystem directories for their specific READMEs and code.

---

## ✅ Running Tests

Unit tests are crucial for ensuring system integrity. Use the provided PowerShell scripts in the project root:

```powershell
# Run tests for a specific subsystem (e.g., ATLAS)
.\test_atlas.ps1

# Run tests with verbose output
.\test_atlas.ps1 -Verbose

# Run tests with coverage report
.\test_atlas.ps1 -Coverage
```

*(Refer to project root for all available `test_*.ps1` scripts)*

---

## 📂 Project Structure

```
/
├── .venv/                  # Virtual environment
├── .cursor/                # Cursor IDE specific settings and rules
├── config/                 # Configuration files (e.g., API keys - managed carefully)
├── docs/                   # Project documentation (MQP, Strategy, Tech Radar, etc.)
├── research/               # Background research, studies, external resources
├── subsystems/             # Core subsystems (ATLAS, KOIOS, ETHIK, etc.)
│   ├── ATLAS/
│   │   ├── core/
│   │   ├── services/
│   │   ├── tests/
│   │   └── README.md
│   └── ...                 # Other subsystems (CRONOS, CORUJA, ETHIK, HARMONY, KOIOS, MYCELIUM, NEXUS)
├── scripts/                # Utility and automation scripts
├── tests/                  # Global or integration tests (if any)
├── .gitignore
├── LICENSE                 # Project License (e.g., MIT)
├── README.md               # This file
├── ROADMAP.md              # High-level project roadmap
├── CONTRIBUTING.md         # Contribution guidelines
├── CODE_OF_CONDUCT.md      # Community standards
├── requirements.txt        # Python dependencies
└── test_*.ps1              # PowerShell test runners
```

---

## 🗺️ Roadmap

See the [**ROADMAP.md**](ROADMAP.md) file for the high-level development plan, current priorities, and upcoming tasks.

---

## 🤝 Contributing

We welcome contributions! Please read our [**CONTRIBUTING.md**](CONTRIBUTING.md) guidelines to get started, including how to report issues, suggest features, and submit code changes.

---

## ⚖️ Code of Conduct

To ensure a welcoming and inclusive community, all contributors and participants are expected to adhere to our [**CODE_OF_CONDUCT.md**](CODE_OF_CONDUCT.md).

---

## 📄 License

This project is licensed under the MIT License - see the [**LICENSE**](LICENSE) file for details.

---

## 💬 Contact & Community

* **Issues:** Report bugs or suggest features via [GitHub Issues](https://github.com/enioxt/EVA-e-Guarani-EGOS/issues).
* **Discussions:** Use [GitHub Discussions](https://github.com/enioxt/EVA-e-Guarani-EGOS/discussions) for questions and broader conversations (if enabled).

### Creator Contact

* **Enio Rocha**
* **Email:** <eniodind@protonmail.com>
* **Telegram:** <https://t.me/ethikin>
* **LinkedIn:** <https://www.linkedin.com/in/enio-rocha-138a01225>

---

✧༺❀༻∞ EGOS ∞༺❀༻✧

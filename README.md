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

Refer to the full **[Master Quantum Prompt (MQP v9.0 "Full Moon Blueprint")](docs/MQP.md)** for the complete philosophical and operational blueprint.

**Development Approach Note:** This project utilizes a multi-agent AI collaboration model within the Cursor IDE, coordinated by an Orchestrator (Gemini 2.5 Pro) and supported by Task Executors (e.g., Quasar-Alpha). Key project documents (`ROADMAP.md`, `docs/website/DEVELOPMENT_PLAN.md`, `docs/website/DESIGN_GUIDE.md`) and rules (`.cursor/rules/`) guide this process. See `docs/ai_collaboration/MULTI_AGENT_WORKFLOW.md` for details.

The technical approach for the primary public-facing website involves a **Modern JavaScript Framework (Next.js/SvelteKit)** and a **Headless CMS**.

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

## ✨ Website & Dashboard Integration

The EGOS website (see `website/` directory) is built with Next.js and features:
- **Integrated Monitoring Dashboard:** Accessible at `/dashboard`, this page embeds the live EGOS Monitoring Dashboard via iframe, using the Streamlit Cloud deployment ([https://egosos.streamlit.app/](https://egosos.streamlit.app/)).
- **Interactive Roadmap:** The main page displays a modular, interactive roadmap. Contributors can click on tasks to open a detailed modal with contribution instructions, acceptance criteria, and direct links to relevant GitHub issues or code.
- **Contribution Flow:** Contributors are encouraged to use the website’s roadmap/modal as the primary way to discover, understand, and contribute to project tasks. Each modal provides links to GitHub for further discussion or code review.

Refer to the [CONTRIBUTING.md](CONTRIBUTING.md) for more details on the contribution workflow.

---

## ✨ Features

*   **Subsystem Architecture:** Modular design based on EGOS principles (ETHIK, KOIOS, NEXUS, etc.).
*   **AI Collaboration:** Designed for human-AI pair programming and agentic workflows.
*   **Dynamic Development:** Emphasizes continuous improvement, feedback loops, and systemic propagation.
*   **Automated Quality Gates:** CI/CD workflows for linting, security scanning, type checking, protocol adherence, and test coverage.
*   **Interactive Dashboard (`dashboard/streamlit_app.py`)**:
    *   Visualizes SPARC task flow (supports simulated & **live** data via Mycelium/NATS).
    *   Displays LLM interaction logs (supports simulated & **live** data via Mycelium/NATS).
    *   Provides a feedback submission form.
    *   Shows automated feedback reports (summary, word cloud, top feedback).
    *   Includes a meta-panel for system transparency (context usage, batch info, heartbeat).
    *   Supports filtering SPARC tasks by type and status.
    *   Includes a toggle for switching between simulated and live data streams.
    *   Displays a Systemic Propagation Log (supports simulated & **live** data via Mycelium/NATS).
    *   Modular UI structure for maintainability.
*   **Website (`website/`)**: Public-facing interface (under development).
*   **Automated Workflows**: CI/CD pipeline for linting, security scanning, type checking, and protocol adherence.
*   **Comprehensive Documentation:** Following KOIOS standards for processes, architecture, and onboarding.

---

## ✨ Current Capabilities (via EGOS AI in Cursor)

The EGOS system, operated primarily through the **EGOS AI assistant (persona: EVA & GUARANI)** within Cursor IDE, currently focuses on:

*   **Codebase Understanding & Navigation (ATLAS):** Mapping dependencies and understanding the project structure to assist development.
*   **Modular Development & Refactoring (NEXUS):** Analyzing code modularity and suggesting improvements.
*   **Standard Enforcement (KOIOS):** Applying coding standards, managing documentation templates, ensuring consistent logging (including verifiable logging standards), and potentially validating data integrity.
*   **Ethical Guideline Application (ETHIK):** Incorporating privacy-preserving checks, policy enforcement, and ethical considerations during development discussions and code generation.
*   **Context & History Management (CRONOS):** Maintaining awareness of the development process and project evolution across interactions.
*   **Task Execution & Orchestration (CORUJA):** Performing development tasks, managing complex AI interactions, and applying basic monitoring/alignment principles based on user requests and project context.

Interaction with these capabilities occurs through natural language prompts directed at the **EGOS AI assistant** within the Cursor IDE chat or code context.

---

## 🚀 Getting Started

### Prerequisites

*   **IDE:** **[Cursor IDE](https://cursor.sh/)** (Essential for interacting with EVA & GUARANI)
*   **OS:** Windows (Primary development target)
*   **Python:** 3.9+
*   **Git:** For version control.
*   **PowerShell:** For running test/utility scripts.

### Development Environment Setup

Developing EGOS relies heavily on the **Cursor IDE** integrated with the **EGOS AI assistant (persona: EVA & GUARANI)**. Follow these steps to set up your environment:

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/enioxt/EVA-e-Guarani-EGOS.git # Replace with your fork if applicable
    cd EVA-e-Guarani-EGOS
    ```

2.  **Set up Python Environment:** Create and activate a virtual environment, then install dependencies. This is standard Python practice.

    ```bash
    # Create virtual environment
    python -m venv .venv
    # Activate (Windows PowerShell)
    .venv\\Scripts\\Activate.ps1
    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Configure Cursor IDE:** Crucially, follow the setup guide in **[cursor_initialization.md](.cursor/cursor_initialization.md)**. This ensures your terminal and environment context work correctly with the EGOS AI assistant.
4.  **Understand Cursor Rules:** Familiarize yourself with the files in **[.cursor/rules/](.cursor/rules/)**. These rules contain essential guidelines (like KOIOS standards, subsystem boundaries, etc.) that the **EGOS AI assistant** uses to assist with development, maintain consistency, and understand the project context. Interacting effectively often involves awareness of these rules.

### Configuration

*   While the core system doesn't require extensive manual configuration for *development within Cursor*, specific tasks delegated to the **EGOS AI assistant** might interact with subsystems requiring API keys or settings (e.g., `CORUJA` for external AI model access). These are typically managed via the `config/` directory and referenced in relevant subsystem documentation or Cursor Rules.

---

## 🚀 Running the Dashboard

Navigate to the project root directory and run:

```bash
streamlit run dashboard/streamlit_app.py
```

Ensure you have the necessary dependencies installed (`streamlit`, `pandas`, `wordcloud`).

---

## 🗺️ Roadmap

See the [**ROADMAP.md**](ROADMAP.md) file for the high-level development plan, current priorities, and upcoming tasks.

---

## 🤝 Contributing

We welcome contributions! Please read our [**CONTRIBUTING.md**](CONTRIBUTING.md) guidelines to get started, including how to report issues, suggest features, submit code changes, and follow the essential [**Human-AI Collaboration Best Practices**](docs/process/human_ai_collaboration_guidelines.md).

---

## ⚖️ Code of Conduct

To ensure a welcoming and inclusive community, all contributors and participants are expected to adhere to our [**CODE_OF_CONDUCT.md**](CODE_OF_CONDUCT.md).

---

## 📄 License

This project is licensed under the MIT License - see the [**LICENSE**](LICENSE) file for details.

---

## 💬 Contact & Community

*   **Issues:** Report bugs or suggest features via [GitHub Issues](https://github.com/enioxt/EVA-e-Guarani-EGOS/issues).
*   **Discussions:** Use [GitHub Discussions](https://github.com/enioxt/EVA-e-Guarani-EGOS/discussions) for questions and broader conversations (if enabled).

### Creator Contact

*   **Enio Rocha**
*   **Email:** <eniodind@protonmail.com>
*   **Telegram:** <https://t.me/ethikin>
*   **LinkedIn:** <https://www.linkedin.com/in/enio-rocha-138a01225>

---

✧༺❀༻∞ EGOS ∞༺❀༻✧

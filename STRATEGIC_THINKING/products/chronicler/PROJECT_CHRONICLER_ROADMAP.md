# Project Roadmap: EGOS Chronicler Module

**Version:** 0.1.1 (Updated post-setup refinement)
**Date:** 2025-04-16

This roadmap outlines the planned development phases for the **EGOS Chronicler Module**. Implementation details can be found in `subsystems/KOIOS/chronicler_module`.

## Phase 1: MVP - Basic Project Overview (Short-Term: ~1-2 Sprints)

**Goal:** Deliver a functional prototype capable of generating a basic project summary from a local directory.

*   **[Epic] Initial Setup & Refinement:**
    *   **[Task] Define Vision & High-Level Roadmap.**
    *   **[Task] Establish Initial Code Structure & Naming:** Renamed from 'Scribe' to 'Chronicler', corrected directory placement to `subsystems/KOIOS/chronicler_module` following EGOS standards.
    *   **[Task] Create Placeholder Files:** `analyzer.py`, `generator.py`, `renderer.py`, `main.py`, `templates/basic_summary_template.html`.
*   **[Epic] Core Analysis Engine:**
    *   **[Story] Directory Scanner:** Implement function to recursively scan a user-provided directory path (`subsystems/KOIOS/chronicler_module/analyzer.py`).
    *   **[Story] `.gitignore` Parser:** Implement logic to read and apply `.gitignore` rules to exclude files/folders (`subsystems/KOIOS/chronicler_module/analyzer.py`).
    *   **[Story] Basic File Filtering:** Implement default exclusions and identify potential key files (`subsystems/KOIOS/chronicler_module/analyzer.py`).
    *   **[Story] Language Detection:** Implement basic language detection (`subsystems/KOIOS/chronicler_module/analyzer.py`).
*   **[Epic] AI Integration (Placeholder/Basic):**
    *   **[Story] Content Extraction:** Extract content from identified key files (`subsystems/KOIOS/chronicler_module/analyzer.py`).
    *   **[Story] Placeholder AI Summary:** Implement a placeholder function in `subsystems/KOIOS/chronicler_module/generator.py` that simulates generating a summary.
*   **[Epic] Output Generation:**
    *   **[Story] Basic HTML Template:** Create `subsystems/KOIOS/chronicler_module/templates/basic_summary_template.html`.
    *   **[Story] Simple Renderer:** Implement basic logic in `subsystems/KOIOS/chronicler_module/renderer.py` to populate the HTML template.
*   **[Epic] CLI/Entry Point:**
    *   **[Story] Basic `main.py`:** Create a simple command-line interface in `subsystems/KOIOS/chronicler_module/main.py`.
    *   **[Task] Initial Test Run & Verification:** Execute the basic CLI command and verify output generation.

**Deliverable:** A command-line tool (`chronicler`) that takes a directory path and outputs a single HTML file with a basic project overview.

## Phase 2: Core AI & Usability Enhancements (Medium-Term: ~3-4 Sprints)

**Goal:** Integrate real AI capabilities via OpenRouter, refine output, and improve usability.

*   **[Epic] Full AI Integration (via CORUJA):**
    *   **[Story] CORUJA Client Integration:** Implement calls to the CORUJA subsystem (or a dedicated OpenRouter client within Chronicler if CORUJA is not ready) to handle communication with LLMs (`subsystems/KOIOS/chronicler_module/generator.py`).
        *   **[Task] Define API/Interaction Contract:** Specify how Chronicler will request summaries/analysis from CORUJA.
        *   **[Task] Implement API Client Logic:** Write the code to make requests and handle responses (including errors).
    *   **[Story] Model Selection Logic:** Implement basic logic for selecting appropriate models based on task (e.g., context-aware model for analysis, writing model for summary) (`subsystems/KOIOS/chronicler_module/generator.py`).
        *   **[Task] Identify Suitable Models:** Research and list candidate models available via OpenRouter.
        *   **[Task] Implement Selection Function:** Code the logic based on task type or configuration.
    *   **[Story] Sophisticated Prompt Engineering:** Develop and iterate on prompts for generating high-quality project summaries (`subsystems/KOIOS/chronicler_module/generator.py`).
        *   **[Task] Draft Initial Summary Prompt:** Create the first version of the prompt incorporating analysis data.
        *   **[Task] Test and Refine Prompt:** Experiment with different prompts, analyze output quality, and iterate.
*   **[Epic] Analysis Improvements:**
    *   **[Story] Enhanced Language/Framework Detection:** Improve accuracy beyond basic extensions (`subsystems/KOIOS/chronicler_module/analyzer.py`).
        *   **[Task] Research Libraries:** Investigate libraries like `linguist` or file content analysis techniques.
        *   **[Task] Implement Enhanced Detection:** Integrate a more robust detection method.
    *   **[Story] Deeper Code Analysis (Optional POC):** Explore feasibility of summarizing key functions/classes (`subsystems/KOIOS/chronicler_module/analyzer.py`, `generator.py`).
        *   **[Task] Identify Key Code Files:** Heuristics to find central code files beyond just README.
        *   **[Task] POC Code Chunk Summarization:** Experiment with prompts to summarize small code snippets.
*   **[Epic] Output & UI:**
    *   **[Story] Improved HTML Styling:** Enhance the visual presentation using CSS (`subsystems/KOIOS/chronicler_module/templates/basic_summary_template.html`).
        *   **[Task] Define Style Guide:** Choose a simple theme or framework (e.g., basic Bootstrap, custom CSS).
        *   **[Task] Implement CSS:** Write or integrate the CSS rules.
    *   **[Story] Basic Navigation (If Needed):** Add simple internal links if the report becomes multi-section (`subsystems/KOIOS/chronicler_module/renderer.py`).
*   **[Epic] Configuration & Billing Foundation:**
    *   **[Story] Basic Configuration File:** Allow users to specify custom exclusion patterns or preferred models via a config file (e.g., `chronicler_config.yaml`).
        *   **[Task] Design Config Format:** Define the structure of the config file.
        *   **[Task] Implement Config Loading:** Add code to read and apply the configuration.
    *   **[Story] Token Usage Tracking:** Implement internal tracking of estimated token usage for AI calls.
        *   **[Task] Estimate Tokens:** Add logic to estimate tokens based on prompts/responses.
        *   **[Task] Log Usage:** Store or display usage information.
    *   **[Story] Crypto Payment Research/PoC:** Investigate potential libraries or services for integrating crypto payments (Low priority for initial Phase 2).

**Deliverable:** A more robust tool with actual AI-generated summaries, improved output, basic configuration, and foundational billing/payment mechanisms.

## Phase 3: Feature Expansion & Polish (Long-Term: Ongoing)

**Goal:** Expand documentation types, enhance user experience, and explore further integrations.

*   **[Epic] Advanced Documentation Types:**
    *   **[Story] API Documentation Generation.**
    *   **[Story] PRD/Architecture Doc Generation.**
    *   **[Story] Code Comment Generation/Enhancement.**
*   **[Epic] User Experience:**
    *   **[Story] GUI (Web UI or Desktop App).**
    *   **[Story] Advanced Configuration UI.**
    *   **[Story] Output Formats (Markdown).**
*   **[Epic] Ecosystem Integration:**
    *   **[Story] IDE Plugin (VS Code/Cursor).**
    *   **[Story] Git Integration.**
*   **[Epic] Platform Features:**
    *   **[Story] User Accounts & History.**
    *   **[Story] Collaboration Features.**
    *   **[Story] Template Marketplace.**

**Deliverable:** A mature, feature-rich documentation tool competitive in the market.

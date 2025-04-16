# Project Roadmap: EGOS Scribe Module

**Version:** 0.1
**Date:** 2025-04-16

This roadmap outlines the planned development phases for the EGOS Scribe Module.

## Phase 1: MVP - Basic Project Overview (Short-Term: ~1-2 Sprints)

**Goal:** Deliver a functional prototype capable of generating a basic project summary from a local directory.

*   **[Epic] Core Analysis Engine:**
    *   **[Story] Directory Scanner:** Implement function to recursively scan a user-provided directory path.
    *   **[Story] `.gitignore` Parser:** Implement logic to read and apply `.gitignore` rules to exclude files/folders.
    *   **[Story] Basic File Filtering:** Implement default exclusions (e.g., `node_modules`, `.git`, common build outputs) and identify potential key files (README, main config files).
    *   **[Story] Language Detection:** Implement basic language detection (e.g., based on file extensions).
*   **[Epic] AI Integration (Placeholder/Basic):**
    *   **[Story] Content Extraction:** Extract content from identified key files (e.g., README.md).
    *   **[Story] Placeholder AI Summary:** Implement a placeholder function in `generator.py` that simulates generating a summary (or uses a very simple, hardcoded prompt if API access is readily available).
*   **[Epic] Output Generation:**
    *   **[Story] Basic HTML Template:** Create `basic_summary_template.html` with placeholders for MVP data.
    *   **[Story] Simple Renderer:** Implement basic logic in `renderer.py` to populate the HTML template with collected data (project name, languages, file list, AI summary).
*   **[Epic] CLI/Entry Point:**
    *   **[Story] Basic `main.py`:** Create a simple command-line interface (using `argparse` perhaps) to accept a directory path and trigger the analysis/generation process.

**Deliverable:** A command-line tool that takes a directory path and outputs a single HTML file with a basic project overview.

## Phase 2: Core AI & Usability Enhancements (Medium-Term: ~3-4 Sprints)

**Goal:** Integrate real AI capabilities via OpenRouter, refine output, and improve usability.

*   **[Epic] Full AI Integration:**
    *   **[Story] CORUJA/OpenRouter Client:** Implement robust integration with OpenRouter via the CORUJA subsystem (or a dedicated client within Scribe).
    *   **[Story] Model Selection Logic:** Implement logic for selecting appropriate models (high-context for analysis, text generator for summaries) - automatic and potentially manual modes.
    *   **[Story] Sophisticated Prompt Engineering:** Develop and refine prompts for generating high-quality, context-aware summaries.
*   **[Epic] Analysis Improvements:**
    *   **[Story] Enhanced Language/Framework Detection:** Improve accuracy and detail of language/framework detection.
    *   **[Story] Deeper Code Analysis (Optional):** Explore summarizing key functions/classes (might move to Phase 3).
*   **[Epic] Output & UI:**
    *   **[Story] Improved HTML Styling:** Apply CSS for better visual presentation of the output HTML.
    *   **[Story] Basic Navigation (if needed):** Add simple navigation if the output becomes multi-section.
*   **[Epic] Configuration & Billing:**
    *   **[Story] Basic Configuration:** Allow users to specify custom exclusion patterns.
    *   **[Story] Token Usage Tracking:** Implement tracking of token usage for AI calls.
    *   **[Story] Crypto Payment PoC:** Integrate a proof-of-concept for crypto payment (e.g., display wallet address and required amount).

**Deliverable:** A more robust tool with actual AI-generated summaries, improved output, basic configuration, and initial billing/payment mechanisms.

## Phase 3: Feature Expansion & Polish (Long-Term: Ongoing)

**Goal:** Expand documentation types, enhance user experience, and explore further integrations.

*   **[Epic] Advanced Documentation Types:**
    *   **[Story] API Documentation Generation:** Analyze code (docstrings, signatures) to generate API docs.
    *   **[Story] PRD/Architecture Doc Generation:** Explore generating higher-level planning documents based on codebase analysis.
    *   **[Story] Code Comment Generation/Enhancement:** Option to add/improve docstrings in the source code.
*   **[Epic] User Experience:**
    *   **[Story] GUI:** Develop a graphical user interface (Web UI or Desktop App) for easier interaction.
    *   **[Story] Advanced Configuration UI:** User-friendly interface for managing settings, exclusions, model preferences.
    *   **[Story] Output Formats:** Support for Markdown output.
*   **[Epic] Ecosystem Integration:**
    *   **[Story] IDE Plugin (VS Code/Cursor):** Develop an extension for direct use within the IDE.
    *   **[Story] Git Integration:** Potentially trigger documentation updates on commits.
*   **[Epic] Platform Features:**
    *   **[Story] User Accounts & History:** Manage user projects and past generations.
    *   **[Story] Collaboration Features:** Allow teams to share configurations or results (requires careful design).
    *   **[Story] Template Marketplace:** Allow users to share/use custom output templates.

**Deliverable:** A mature, feature-rich documentation tool competitive in the market.

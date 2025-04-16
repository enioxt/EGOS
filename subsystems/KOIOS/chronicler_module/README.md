# KOIOS: Chronicler Module

**Part of the KOIOS Subsystem**

**Strategic Context:** See Vision [[../../../STRATEGIC_THINKING/products/chronicler/PROJECT_CHRONICLER_VISION.md]] and Roadmap [[../../../STRATEGIC_THINKING/products/chronicler/PROJECT_CHRONICLER_ROADMAP.md]]

## Overview

The Chronicler Module is responsible for AI-powered analysis and generation of documentation from local codebases.

It aims to provide developers with an easy-to-use tool to quickly understand projects and maintain up-to-date documentation by leveraging Large Language Models for code analysis and text generation.

## Purpose within EGOS

*   **Knowledge Organization:** Structures information extracted from codebases.
*   **Standardized Output:** Generates documentation in a consistent (and eventually customizable) format.
*   **Integration:** Leverages CORUJA for AI model interaction and potentially integrates with other EGOS components or external tools (IDEs, Git).
*   **Automated Documentation:** Reduce manual effort in creating initial project documentation.
*   **Codebase Understanding:** Provide quick summaries for developers onboarding to new modules.
*   **Maintainability:** Assist in keeping documentation somewhat aligned with code evolution (future goal).

## Current Status (As of April 16, 2025)

*   **Phase 1 (MVP) Complete:** Basic CLI tool analyzes a directory and generates an HTML summary.
*   **Phase 2 (AI Integration) Complete:** Integrated with OpenRouter for AI summary generation.
*   **Phase 3 (Refinement/Observability) In Progress:**
    *   Implemented comprehensive logging across all modules ([main.py](cci:7://file:///c:/Eva%20Guarani%20EGOS/subsystems/KOIOS/chronicler_module/main.py:0:0-0:0), [analyzer.py](cci:7://file:///c:/Eva%20Guarani%20EGOS/subsystems/KOIOS/chronicler_module/analyzer.py:0:0-0:0), [generator.py](cci:7://file:///c:/Eva%20Guarani%20EGOS/subsystems/KOIOS/chronicler_module/generator.py:0:0-0:0), [renderer.py](cci:7://file:///c:/Eva%20Guarani%20EGOS/subsystems/KOIOS/chronicler_module/renderer.py:0:0-0:0)).
    *   Configured logging output to a dedicated `chronicler.log` file within the specified output directory.
    *   Standardized HTML report naming convention.
*   **Dependencies:** Managed in `requirements.txt`.

## Key Components

*   `analyzer.py`: Directory scanning, file filtering (`.gitignore`), language detection.
*   `generator.py`: AI model interaction (OpenRouter), prompt engineering.
*   `renderer.py`: HTML report generation.
*   `main.py`: CLI entry point, orchestrates module execution.
*   `chronicler_config.yaml`: Configuration file for model, exclusions, etc.
*   `chronicler.log`: Output log file (generated in the output directory).

## Getting Started (MVP)

1.  Ensure Python environment is set up.
2.  Navigate to this directory (`subsystems/KOIOS/chronicler_module`) in your terminal.
3.  Run the analysis: `python main.py "<path_to_your_project_directory>"`
4.  The output HTML file will be saved in the current directory by default (or specify with `-o <output_dir>`).

## Roadmap & Upcoming Tasks

Refer to the main strategic [Project Roadmap](../../../STRATEGIC_THINKING/products/chronicler/PROJECT_CHRONICLER_ROADMAP.md) for high-level goals.

### Short-Term (Next ~1-3 Sessions)

1.  **(Refinement)** Enhance Error Handling: Implement more specific exception handling (API limits, file errors) in all modules.
2.  **(Refinement/KOIOS)** Improve Configuration: Add more options to `chronicler_config.yaml` (log level, report date format, more exclusion patterns).
3.  **(HARMONY)** Basic Unit Tests: Create initial tests for helper functions (e.g., language detection).
4.  **(Internal)** Time/Cost Tracking: Begin manually logging development time per task; investigate automatic token logging for `generator.py`.

### Medium-Term

5.  **(Refinement/HARMONY)** Advanced Analysis: Enhance `analyzer` to detect frameworks, dependencies (read `requirements.txt`, `package.json`).
6.  **(CORUJA/Refinement)** Improve AI Prompt: Refine `generator.py` prompt based on feedback and new analysis data (dependencies/frameworks); add config for summary style/length.
7.  **(HARMONY)** Integration Tests: Create tests for the full [main.py](cci:7://file:///c:/Eva%20Guarani%20EGOS/subsystems/KOIOS/chronicler_module/main.py:0:0-0:0) workflow.
8.  **(KOIOS/Refinement)** Externalize CSS: Move CSS from `renderer.py` to a separate file.

### Long-Term

9.  **(Spec/Arch/CORUJA)** Interactive Mode/UI: Explore options for a simple web UI (Flask/Streamlit?) or enhanced CLI.
10. **(Spec/Arch/CORUJA)** Caching Mechanism: Implement caching for analysis results to speed up runs on unchanged projects.
11. **(Refinement/HARMONY)** Token Usage Reporting: Integrate token usage reporting from OpenRouter API into logs if feasible.
12. **(Spec/Arch/CORUJA)** Multi-File Analysis for Summary: Allow `generator` to use content from multiple key files for summary generation.
13. **(Spec/Arch/KOIOS)** EGOS Website Integration: Make Chronicler functionality executable/viewable via the main EGOS website interface (`docs/`).
14. **(KOIOS)** Website Documentation: Add comprehensive documentation for Chronicler usage and API (if applicable) to the EGOS website.
15. **(HARMONY/KOIOS)** File Timing Dashboard: (Related Idea) Develop a system/dashboard to visualize development time based on file creation/modification dates across EGOS.

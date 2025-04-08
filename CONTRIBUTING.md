# Contributing to EGOS

First off, thank you for considering contributing to **EGOS**! Your involvement helps us build a more robust, ethical, and unified system.

This document provides guidelines for contributing to the project. Please read it carefully to ensure a smooth collaboration process.

## Code of Conduct

By participating in this project, you agree to abide by our [**Code of Conduct**](CODE_OF_CONDUCT.md). Please read it to understand the standards of behavior we expect within our community.

## How Can I Contribute?

There are many ways to contribute:

*   **Reporting Bugs:** If you find a bug, please create a detailed issue in our GitHub repository.
*   **Suggesting Enhancements:** Have an idea for a new feature or an improvement? Open an issue to discuss it.
*   **Writing Code:** Help implement new features, fix bugs, or improve existing code.
*   **Improving Documentation:** Enhance READMEs, add docstrings, write tutorials, or correct typos.
*   **Submitting Feedback:** Share your experience using EGOS and suggest improvements.

## Reporting Bugs

Before creating a bug report, please check existing issues to see if someone has already reported it. If not, create a new issue and include:

*   A clear and descriptive title.
*   A detailed description of the steps to reproduce the bug.
*   What you expected to happen.
*   What actually happened (include error messages and stack traces if applicable).
*   Your environment details (OS, Python version, etc.).

## Suggesting Enhancements

Use GitHub Issues to suggest enhancements. Provide:

*   A clear title summarizing the suggestion.
*   A detailed description of the proposed feature or improvement.
*   The motivation behind the suggestion (what problem does it solve?).
*   Any potential implementation ideas (optional).

## Development Workflow

1.  **Fork the Repository:** Create your own copy of the EGOS repository on GitHub.
2.  **Clone Your Fork:**
    ```bash
    git clone <your-fork-url>
    cd Eva-Guarani-EGOS
    ```
3.  **Set Up Environment:** Follow the [Installation steps in the README](README.md#installation).
4.  **Create a Branch:** Create a new branch for your feature or bugfix:
    ```bash
    git checkout -b <branch-name>
    # Examples: feature/add-atlas-mermaid-export, fix/koios-logger-bug
    ```
5.  **Make Changes:** Implement your code or documentation changes.
6.  **Follow Standards:** Adhere to the KOIOS standards for code style, naming, logging, and error handling. Refer to relevant `.mdc` rules or documentation in `docs/STANDARDS_*.md`. **When creating or modifying core AI prompts, document them using the [PDD Template](docs/templates/PDD_Template.md).**
7.  **Write/Update Tests:** Ensure your changes are covered by unit tests. Aim to maintain or increase test coverage. Run tests using the provided PowerShell scripts (e.g., `.\test_<subsystem>.ps1 -Coverage`).
8.  **Commit Changes:** Use clear and descriptive commit messages following the Conventional Commits format (see `commit_messages.mdc` rule). Reference related issues (e.g., `feat: Add Mermaid export to ATLASCore (closes #42)`).
    ```bash
    git add .
    git commit -m "type(scope): description"
    ```
9.  **Push to Your Fork:**
    ```bash
    git push origin <branch-name>
    ```
10. **Submit a Pull Request (PR):** Open a PR from your branch to the `main` branch of the upstream EGOS repository.
    *   Provide a clear title and description for your PR.
    *   Link any related issues.
    *   Explain the changes and the reasoning behind them.
    *   Ensure all automated checks (CI/CD, linters - if configured) pass.
11. **Code Review:** Project maintainers will review your PR. Be responsive to feedback and make necessary adjustments.

## Standard Commit & Push Workflow (Main Branch)

To ensure your local changes are correctly synchronized with the `main` branch on GitHub, follow these steps **in order**. For standard commits of completed work, refer specifically to procedure **EGOS-GIT-COMMIT-01** in the [Git Workflow Standards](.cursor/rules/git_workflow_standards.mdc).

1.  **Check Status (Optional, but recommended):**
    *   Confirm which branch you are on and check for unsaved changes.
    *   Command: `git status`

2.  **Synchronize with Remote (`git pull`):**
    *   **Purpose:** Download the latest updates from the `main` branch on GitHub to your local repository. This prevents your push from being rejected because the remote repository is ahead of yours.
    *   Command: `git pull origin main`
    *   **Attention:** If merge conflicts occur after the pull, resolve them by editing the marked files, save them, use `git add <resolved_file>` for each, and finalize the merge with `git commit` before proceeding.
    *   **Important:** For detailed procedures on handling merge conflicts and other Git challenges, refer to the [Git Workflow Standards](.cursor/rules/git_workflow_standards.mdc) (Procedures EGOS-GIT-MERGE-01 and EGOS-GIT-PRECOMMIT-01).

3.  **Stage Changes (`git add`):**
    *   **Purpose:** Tell Git which modified or created files you want to include in the *next* commit.
    *   Command for specific files: `git add <filename_1> <filename_2>`
    *   Command to add *all* changes in the current directory (use with caution): `git add .`

4.  **Commit Locally (`git commit`):**
    *   **Purpose:** Save the staged changes to the history of *your* local repository.
    *   Command: `git commit -m "type(scope): Your descriptive message here"`
    *   **Important:** Use clear commit messages following the [Conventional Commits](https://www.conventionalcommits.org/) standard (e.g., `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`). Refer to the `commit_messages.mdc` rule and **EGOS-GIT-COMMIT-01**.

5.  **Push to GitHub (`git push`):**
    *   **Purpose:** Send your local commits (which now include the updates from step 2) to the remote repository on GitHub.
    *   Command: `git push origin main`

Following this sequence ensures a smoother workflow and reduces common Git errors.

## Documentation Contributions

Improvements to documentation are always welcome! Follow the development workflow above, making changes to `.md` files or adding docstrings within the code. Ensure your writing is clear, concise, and follows existing style where applicable.

Thank you again for your interest in contributing!

---

✧༺❀༻∞ EGOS ∞༺❀༻✧

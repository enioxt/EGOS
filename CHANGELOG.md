# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Standard project documentation files: `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
- Cursor IDE configuration files: `.cursor/cursor_initialization.md` and rules in `.cursor/rules/` added to version control.
- Standard commit/push workflow documentation to `CONTRIBUTING.md`.
- Sections on development setup, current capabilities, and key resources to `README.md`.
- Comprehensive Git workflow standards in `.cursor/rules/git_workflow_standards.mdc` with detailed procedures for merge conflicts, pre-commit hook failures, and repository migrations.
- Enhanced Smart Tips protocol with subsystem-specific recommendations and tip categories.
- New KOIOS standards documentation in `docs/standards/KOIOS_Interaction_Standards.md`.
- Local-first development rule to ensure proper workflow with Git repositories.
- Initial project structure based on Quantum Unified System principles.
- Core subsystems directories created (ATLAS, BIOS-Q, etc.).
- Basic README and documentation placeholders.

### Changed
- Standardized the structure of `.cursor/rules/*.mdc` files to comply with `MDC_RULES_STANDARD.md` (added frontmatter description, standard H1, standard H2 sections: Rule, Rationale, Examples).
- **`README.md`:** Overhauled to reflect current project state, focus on Cursor IDE development workflow, remove inaccurate installation/usage sections, and add links to key resources.
- **`.gitignore`:**
    - Removed ignore rules for `.cursor/` directory to track essential setup files.
    - Removed ignore rules for `package-lock.json`, `yarn.lock` to ensure dependency consistency.
    - Removed obsolete ignore rule for `Researchs/`.
    - Removed generic ignore rule for `*.ps1` scripts.
    - Added rule to ignore large lock files in example directories.
- Refactored `subsystems/ETHIK/core/sanitizer.py` to remove redundant module-level logger and rely on injected `KoiosLogger`.
- Refactored `subsystems/ETHIK/core/validator.py` to remove redundant module-level logger and rely on injected `KoiosLogger`.
- Updated `subsystems/CRONOS/service.py` to use `KoiosLogger` for the service itself and correctly handle the logger instantiation for `BackupManager`.
- **Branding:** Applied "EGOS" branding consistently across core documentation (`README.md`, `ROADMAP.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `docs/MQP.md`, `docs/STRATEGY.md`) and rule files (`.cursor/rules/quantum_prompt_core.mdc`). Updated version references to MQP v8.2.
- Updated `package.json` with standard fields and "egos" name.
- Updated subsystem documentation introductions (`ETHIK/README.md`, `CRONOS/docs/procedures.md`) with EGOS branding.
- Updated `ROADMAP.md` to reflect completion of Git workflow standards and Smart Tips enhancements.
- Added categories to Smart Tips protocol for better organization.
- Refined subsystem responsibilities based on MQP v7.4.

### Deprecated
-

### Removed
- Inaccurate "Installation" and "Usage" sections from `README.md`.
- Obsolete/incorrect ignore rules from `.gitignore`.
- Redundant module-level logger setup in `subsystems/ETHIK/core/sanitizer.py`.
- Redundant module-level logger setup in `subsystems/ETHIK/core/validator.py`.
- Redundant module-level logger setup in `subsystems/NEXUS/core/nexus_core.py`.

### Fixed
- Broken Markdown links in `README.md` for Cursor setup files and directories.
- Updated hardcoded paths in `.cursor` config files and `CRONOS/service.py` to use "EGOS" project name (Note: still requires refactoring to relative paths).
- Resolved indentation errors and cleaned up unused code/imports in `subsystems/ETHIK/core/validator.py`.

### Security
- Removed hardcoded API key from `.cursor/test_openrouter_direct.bat`.

## [0.1.0] - YYYY-MM-DD

### Added
- Initial project structure setup.
- Basic configuration for subsystems.

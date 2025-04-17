# Process: PROC-VALIDATE-01 - Roadmap Task Validation

**Version:** 1.0
**Date:** 2025-04-17
**Status:** Active
**Owner:** KOIOS Subsystem

## 1. Purpose

This document describes the usage of the `scripts/validation/validate_roadmap_tasks.py` script. The script ensures that all task entries in the main `ROADMAP.md` file adhere to the KOIOS standard format. Consistent formatting is crucial for automated processing, reporting, and clarity.

## 2. Scope

This process applies to the `ROADMAP.md` file located in the project root. It validates the structure of individual task lines.

## 3. Procedure

### 3.1. Running the Script

The script is designed to be run from the project's root directory.

```powershell
python scripts/validation/validate_roadmap_tasks.py
```

Or, if executable permissions are set:

```powershell
./scripts/validation/validate_roadmap_tasks.py
```

### 3.2. Script Functionality

- Reads the content of `ROADMAP.md`.
- Iterates through each line identified as a task entry (typically lines starting with `- [ ]`, `- [x]`, or similar markdown task list syntax followed by standard fields).
- Applies regular expressions and structural checks to validate against the expected KOIOS format: `[Status] [Subsystem(s)] [Task ID] [Priority] Description (Dependencies: ...) (Principles: ...)`
- Reports any lines that do not conform to the standard format, indicating the line number and the specific deviation found.
- (Optional/Future Enhancement): May include auto-correction capabilities for common formatting errors.

## 4. Expected Format

Tasks should generally follow this pattern:

```markdown
- [ ] [To Do] [KOIOS, NEXUS] [KOIOS-TASK-001] [P1] Implement automated documentation generation (Dependencies: NEXUS-TASK-005) (Principles: Conscious Modularity, Systemic Cartography)
- [x] [Done] [CRONOS] [CRONOS-TASK-002] [P0] Setup initial project backup strategy (Principles: Evolutionary Preservation)
```

Key elements checked include:
- Presence and format of Status (`[Status]`)
- Presence and format of Subsystem(s) (`[Subsystem]` or `[Subsystem1, Subsystem2]`)
- Presence and format of Task ID (`[ID-PREFIX-NNN]`)
- Presence and format of Priority (`[P0-P4]`)
- Parentheses for Dependencies and Principles sections (if present).

## 5. Examples & Common Corrections

*   **Error:** Missing Priority
    *   *Incorrect:* `- [ ] [To Do] [ATLAS] [ATLAS-TASK-010] Create visualization module`
    *   *Correct:* `- [ ] [To Do] [ATLAS] [ATLAS-TASK-010] [P2] Create visualization module`
*   **Error:** Incorrect Task ID format
    *   *Incorrect:* `- [ ] [In Progress] [MYCELIUM] [MYC_TASK_1] [P1] Define core message schema`
    *   *Correct:* `- [ ] [In Progress] [MYCELIUM] [MYCELIUM-TASK-001] [P1] Define core message schema`
*   **Error:** Missing Subsystem brackets
    *   *Incorrect:* `- [ ] [To Do] HARMONY [HARMONY-TASK-005] [P3] Test Windows compatibility`
    *   *Correct:* `- [ ] [To Do] [HARMONY] [HARMONY-TASK-005] [P3] Test Windows compatibility`

## 6. Related Standards

- `ROADMAP.md` structure and content guidelines.
- KOIOS Task Identification and Formatting standards.
- Conventional Commits (`commit_messages.mdc` - for commits related to roadmap updates).

## 7. Troubleshooting

- **Script not found:** Ensure you are running the command from the project root directory (`c:\Eva Guarani EGOS`).
- **Permission denied:** You may need to grant execute permissions (`chmod +x scripts/validation/validate_roadmap_tasks.py` on Git Bash/WSL, or check PowerShell execution policy).
- **Incorrect validation:** If the script incorrectly flags valid lines or misses invalid ones, please open an issue to refine the validation logic.

---
✧༺❀༻∞ EGOS ∞༺❀༻✧

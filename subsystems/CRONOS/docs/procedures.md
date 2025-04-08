# CRONOS Backup & Restore Procedures

**Version:** 1.0
**Last Updated:** April 3, 2025

## Overview

This document outlines the standard operating procedures (SOPs) for using the CRONOS subsystem, specifically its `BackupManager`, to manage project backups for the **EGOS** system. Adhering to these procedures ensures data integrity and facilitates system state recovery.

**Target Audience:** Developers, System Administrators

## Core Component: BackupManager

The primary tool for managing backups is the `BackupManager` class located in `subsystems/CRONOS/core/backup_manager.py`. It provides functionalities for creating, listing, restoring, and cleaning backups.

## Prerequisites

-   Python environment with necessary dependencies installed (refer to `requirements.txt`).
-   Access to the project's root directory.
-   (Optional) Running Mycelium network if using message-based interaction via `CronosService`.

## Procedures

These procedures assume interaction with the `BackupManager` class, typically via a script or the `CronosService`.

### 1. Creating a Manual Backup

**Purpose:** To create a point-in-time snapshot of the project state.

**Method:** Use the `create_backup` method.

**Parameters:**

*   `name` (str): A descriptive name for the backup (e.g., `"pre_refactor"`, `"feature_x_release"`).
*   `backup_type` (str, optional): The type of backup, defaults to `"manual"`. Other types like `"auto"` or `"restore_point"` might be used internally.
*   `include_patterns` (List[str], optional): List of glob patterns for files/directories to *explicitly include*. If `None`, defaults to `["**/*"]`.
*   `exclude_patterns` (List[str], optional): List of glob patterns for files/directories to *exclude*. If `None`, uses default excludes defined in `BackupManager` (e.g., `.venv`, `__pycache__`, `.git`, `backups`, `logs`, `data`).
*   `metadata` (Dict[str, Any], optional): Additional metadata to store within the backup (e.g., `{"commit_hash": "abcdef1"}`).

**Example (Conceptual Python):**

```python
import asyncio
from pathlib import Path
from subsystems.CRONOS.core.backup_manager import BackupManager

async def main():
    project_root = Path(".").resolve() # Adjust as needed
    # Assuming BackupManager is initialized correctly (potentially needs Mycelium mock/client)
    manager = BackupManager(project_root=project_root)

    backup_path = await manager.create_backup(
        name="deployment_candidate",
        backup_type="manual",
        metadata={"reason": "Preparing for deployment test"}
    )

    if backup_path:
        print(f"Manual backup created successfully: {backup_path}")
    else:
        print("Failed to create manual backup.")

# asyncio.run(main())
```

**Result:** A compressed `.zip` file is created in the configured backup directory (default: `./backups/`) following the naming convention `egos_backup_<type>_<name>_<timestamp>.zip`.

### 2. Listing Available Backups

**Purpose:** To view the existing backups and their details.

**Method:** Use the `list_backups` method.

**Parameters:** None.

**Example (Conceptual Python):**

```python
import asyncio
from pathlib import Path
from subsystems.CRONOS.core.backup_manager import BackupManager

async def main():
    project_root = Path(".").resolve()
    manager = BackupManager(project_root=project_root)

    backups = manager.list_backups() # This method is currently sync

    print("Available Backups:")
    if not backups:
        print("- None")
    else:
        for backup in backups:
            print(f"- File: {backup['filename']}")
            print(f"  Size: {backup['size_bytes'] / 1024:.2f} KB")
            print(f"  Created: {backup['created_at']}")

# asyncio.run(main()) # Adjust if list_backups becomes async
```

**Result:** Prints a list of available backup files found in the backup directory, sorted by creation time (newest first), including filename, size, and creation timestamp.

### 3. Restoring from a Backup

**Purpose:** To revert the project state to a previously saved backup.

**Method:** Use the `restore_backup` method.

**Parameters:**

*   `backup_identifier` (str): A way to identify the backup to restore. This can be:
    *   The **full filename** of the backup zip file (e.g., `"egos_backup_manual_..._timestamp.zip"`).
    *   The **timestamp** part of the filename (e.g., `"YYYYMMDD_HHMMSS"`).
    *   The backup **name and timestamp** part (`<name>_<timestamp>`).
    *   *Note: If multiple backups match a partial identifier (like timestamp), the **latest** matching backup will be used.* Use the full filename for certainty.
*   `restore_target_path` (str, optional): The directory where the backup content should be extracted. Behavior depends on the `strategy`.
*   `strategy` (str, optional): The restore strategy. Options:
    *   `"new_location"` (Default): Restores the backup content into a *new, separate directory*.
        *   If `restore_target_path` is provided, it uses that path (which **must not exist or be empty**).
        *   If `restore_target_path` is `None`, it creates a new directory inside `./backups/restores/` named `restore_<backup_name>_<timestamp>`.
    *   `"overwrite"`: Restores the backup content directly into the **project root directory**, potentially overwriting existing files.
        *   **Use with extreme caution!**
        *   If configured (`restore.create_restore_point: true`), it automatically creates a `restore_point` backup before overwriting.
        *   `restore_target_path` is ignored for this strategy.

**Example (Conceptual Python - Restore to New Location):**

```python
import asyncio
from pathlib import Path
from subsystems.CRONOS.core.backup_manager import BackupManager

async def main():
    project_root = Path(".").resolve()
    manager = BackupManager(project_root=project_root)

    # Find a backup identifier (e.g., from list_backups or know the filename/timestamp)
    backup_id_to_restore = "egos_backup_manual_deployment_candidate_20250403_100000.zip" # Replace with actual ID

    # Restore to a new location (default strategy)
    success, message = await manager.restore_backup(backup_identifier=backup_id_to_restore)

    if success:
        print(f"Restore successful: {message}") # Message will contain the new restore path
    else:
        print(f"Restore failed: {message}")

# asyncio.run(main())
```

**Example (Conceptual Python - Overwrite):**

```python
import asyncio
from pathlib import Path
from subsystems.CRONOS.core.backup_manager import BackupManager

async def main():
    project_root = Path(".").resolve()
    manager = BackupManager(project_root=project_root)

    backup_id_to_restore = "egos_backup_manual_deployment_candidate_20250403_100000.zip" # Replace with actual ID

    # Restore by overwriting project root (USE WITH CAUTION)
    print("WARNING: Attempting overwrite restore. Ensure you have backups!")
    success, message = await manager.restore_backup(
        backup_identifier=backup_id_to_restore,
        strategy="overwrite"
    )

    if success:
        print(f"Overwrite restore successful: {message}")
    else:
        print(f"Overwrite restore failed: {message}")

# asyncio.run(main())
```

**Result:** The content of the selected backup archive is extracted according to the chosen strategy. Success status and relevant messages are returned.

### 4. Cleaning Old Backups

**Purpose:** To automatically remove old backups based on retention policies defined in the configuration.

**Method:** Use the `clean_old_backups` method.

**Parameters:** None.

**Policies (from config):**

*   `backup.retention_days`: Backups older than this number of days are deleted.
*   `backup.max_backups`: If the total number of backups exceeds this, the oldest ones are deleted until the limit is met.
*   *(Cleanup runs automatically after `create_backup`)*.

**Example (Conceptual Python - Manual Trigger):**

```python
import asyncio
from pathlib import Path
from subsystems.CRONOS.core.backup_manager import BackupManager

async def main():
    project_root = Path(".").resolve()
    manager = BackupManager(project_root=project_root)

    print("Manually cleaning old backups...")
    await manager.clean_old_backups()
    print("Cleanup complete based on retention policy.")

# asyncio.run(main())
```

**Result:** Old backup files are deleted from the backup directory according to the configured retention days and maximum backup count.

## Configuration

The `BackupManager` loads its configuration during initialization. This configuration typically originates from a central project configuration file (e.g., `config.json` or similar) and is passed to the `BackupManager`, often via the `CronosService`.

Key configuration options influencing these procedures:

*   `backup.directory`: Location where backups are stored (Default: `./backups`).
*   `backup.retention_days`: Days to keep backups (Default: 30).
*   `backup.max_backups`: Max number of backups to keep (Default: 100).
*   `backup.compression_level`: ZIP compression level (Default: 9).
*   `backup.exclude_patterns`: Default list of patterns to exclude.
*   `restore.default_strategy`: Default strategy if not specified (`new_location` or `overwrite`).
*   `restore.create_restore_point`: Whether to create a backup before an `overwrite` restore (Default: `true`).
*   `restore.verify_integrity`: Whether to run a zip integrity test before extraction (Default: `true`).

## Backup Verification (Best Practice)

While CRONOS offers an optional integrity check during restore (`restore.verify_integrity`), it is **highly recommended** to periodically test your backups:

1.  **List available backups:** Use `list_backups`.
2.  **Choose a recent backup.**
3.  **Restore to a new location:** Use `restore_backup` with the default `new_location` strategy.
4.  **Inspect the restored files:** Manually check critical files, configurations, or run basic checks within the restored directory to ensure the backup is valid and complete.
5.  **Delete the test restore directory** once verification is complete.

Regular verification ensures backups are viable when needed.

## Error Handling

If any backup or restore operation fails:

*   The method will typically return `None` (for `create_backup`) or `(False, error_message)` (for `restore_backup`).
*   Detailed error information, including stack traces for unexpected exceptions, will be logged using the `KoiosLogger` (check console output and the configured log file, typically `logs/egos_system.log`). Consult these logs for troubleshooting.

## Important Notes

*   **Overwrite Strategy:** Use the `overwrite` restore strategy with extreme caution as it modifies the live project directory.
*   **Backup Integrity:** While the restore process includes an optional integrity check (`restore.verify_integrity`), regularly verify backups manually or through automated checks.
*   **Storage:** Ensure sufficient disk space is available for storing backups.
*   **Mycelium:** If using `CronosService`, backup and restore operations can be triggered via Mycelium messages (Topics: `request.cronos.backup`, `request.cronos.restore`). Status updates are published to corresponding status topics.

## Review & Finalization (Roadmap Item)

*(Placeholder: This section notes the need to review and finalize these procedures according to Roadmap Step 1 [Next 10 Steps - 2025-04-02]. Ensure all procedures are accurate, examples are clear, and integration with KoiosLogger and Mycelium is properly documented or handled.)*

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧

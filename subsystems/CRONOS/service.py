"""Core service implementation for the CRONOS subsystem."""

import asyncio
from dataclasses import asdict, dataclass, field
from datetime import datetime
import hashlib  # Added hashlib
import json
import logging
import os  # Added os
from pathlib import Path
import re
import shutil
import subprocess  # Added subprocess
from typing import Any, Dict, List, Optional, Tuple

# Import Koios Logger
from koios.logger import KoiosLogger

# Assuming Mycelium Interface is available for injection
from subsystems.MYCELIUM.core.interface import MyceliumInterface
from subsystems.MYCELIUM.core.network import MyceliumNetwork

# Import functions from migrated scripts (or refactor them into this class)
# Need to adjust imports based on final location/structure
try:
    # If scripts remain separate and are importable:
    from .scripts.backup_manager import CRONOSBackup as BackupManager  # Assuming class name
    from .scripts.verify_cleanup import (
        verify_backup_integrity as verify_integrity_script,
    )  # Assuming function name

    # Need to refactor verify_cleanup.py into functions first
except ImportError:
    # Fallback if refactoring into this file or structure changes
    logging.warning(
        "Could not import backup/verification scripts directly. Functionality needs integration."
    )
    BackupManager = None
    verify_integrity_script = None

# Remove old standard logger setup
# logger = logging.getLogger(__name__)

# Get a logger for the module level, used by the initializer function
module_logger = KoiosLogger.get_logger("CRONOS.ServiceModule")


# --- Data Classes (from cronos_core.py) --- #
@dataclass
class SystemState:
    """Represents a captured system state (metadata focus)."""

    id: str
    name: str
    timestamp: datetime = field(default_factory=datetime.now)
    state_type: str = "snapshot"
    related_backup_id: Optional[str] = None
    # Core state data:
    git_commit_hash: Optional[str] = None
    config_hashes: Dict[str, str] = field(
        default_factory=dict
    )  # e.g., {"config/backup_config.json": "hash..."}
    subsystem_versions: Dict[str, str] = field(
        default_factory=dict
    )  # e.g., {"CRONOS": "0.1", "KOIOS": "0.2"} (Placeholder for now)
    # Other potential data:
    data: Dict[str, Any] = field(default_factory=dict)  # Generic placeholder
    metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemBackupInfo:
    """Represents metadata about a system backup artifact."""

    id: str  # Backup ID (e.g., directory name timestamp)
    name: str
    timestamp: datetime
    backup_type: str = "system"
    state_id: Optional[str] = None
    location: Path = Path(".")
    size_bytes: int = 0
    file_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Add retention info? (daily, weekly, monthly)
    retention_category: Optional[str] = None


# --- Core Service Class --- #


class CronosService:
    """Core service for CRONOS subsystem functionalities."""

    def __init__(
        self, config: Dict[str, Any], mycelium_interface: MyceliumInterface, project_root: Path
    ):
        """Initialize the CRONOS service."""
        self.config = config
        self.interface = mycelium_interface
        self.node_id = "CRONOS_SERVICE"  # More specific node ID
        self.system_root = project_root
        self.backup_base_path = self.system_root / Path(
            self.config.get("backup_location", "backups/CRONOS")
        )
        self.version_history_file = self.backup_base_path / "version_history.json"

        # --- Setup Loggers using Koios --- #
        log_config = self.config.get("logging", {})
        # Service logger
        self.logger = KoiosLogger.get_logger(f"EGOS.{self.node_id}", config=log_config)
        # --------------------------------- #

        self.states: Dict[str, SystemState] = {}
        self.backups: Dict[str, SystemBackupInfo] = {}

        self._backup_task: Optional[asyncio.Task] = None
        self._running = False

        # Instantiate BackupManager
        self.backup_manager = BackupManager(
            # Assuming BackupManager's __init__ takes project_root, config_path,
            # and mycelium_client
            # And its internal logger uses the passed name or defaults.
            # We don't pass logger directly.
            project_root=self.system_root,
            config_path=self.config.get(
                "backup_manager_config", self.system_root / "config" / "cronos_config.yaml"
            ),
            mycelium_client=self.interface,  # Pass the initialized Mycelium client
        )
        # Ensure BackupManager uses the correct KoiosLogger internally - Removed
        # This relies on BackupManager.__init__ calling
        # KoiosLogger.get_logger("CRONOS.BackupManager")
        # Or accepting a logger instance (less ideal if it has its own name)
        # Re-checking backup_manager.py: It DOES create its own logger.

        self.logger.info(f"CRONOS Service initialized. Backup location: {self.backup_base_path}")

        self.backup_tasks: Dict[str, asyncio.Task] = {}
        self.lock = asyncio.Lock()
        self.stop_event = asyncio.Event()
        self.running = False

        # Update the config with the determined root
        self.config["system_root"] = "/c/Eva Guarani EGOS/"
        self.logger.info(f"Updated system_root in config: {self.config['system_root']}")

    async def start(self):
        """Start the CRONOS service and connect to Mycelium."""
        if self._running:
            self.logger.warning("CRONOS service already running.")
            return

        self.logger.info("Starting CRONOS service...")
        self.backup_base_path.mkdir(parents=True, exist_ok=True)
        self._load_version_history()  # Load history first

        # --- Check if initial/periodic backup is needed (from preservation.py) --- #
        try:
            await self._check_and_perform_backup()
        except Exception as e:
            self.logger.error(f"Error during initial backup check: {e}", exc_info=True)
            # Continue starting service even if initial backup check fails?
            # Or should this be a fatal error preventing start?
            # For now, log and continue.
        # --------------------------------------------------------------------- #

        # Connect to Mycelium
        connected = await self.interface.connect(
            node_type="PRESERVATION",
            version="0.1",  # TODO: Make version dynamic
            capabilities=["backup", "restore", "state_mgmt", "history"],
        )
        if not connected:
            self.logger.error("CRONOS failed to connect to Mycelium Network!")
            return

        # Register message handlers
        # await self.interface.subscribe(
        #     "request.cronos.create_backup",
        #     self.handle_create_backup_request
        # )
        # await self.interface.subscribe(
        #     "request.cronos.get_status",
        #     self.handle_get_status_request
        # )

        # Start background tasks (e.g., scheduled backups - if implementing scheduler)
        # self._start_scheduler()

        # Add subscriptions for restore requests?
        try:
            await self.interface.subscribe(
                f"request.{self.node_id}.list_backups", self.handle_list_backups_request
            )
            await self.interface.subscribe(
                f"request.{self.node_id}.restore_backup", self.handle_restore_backup_request
            )
            self.logger.info("Subscribed to backup list/restore request topics.")
        except Exception as e:
            self.logger.error(f"Failed to subscribe to CRONOS request topics: {e}", exc_info=True)

        self._running = True
        self.logger.info("CRONOS service started successfully.")
        await self.interface.report_health("active")

    async def stop(self):
        """Stop the CRONOS service gracefully."""
        if not self._running:
            self.logger.warning("CRONOS service not running.")
            return

        self.logger.info("Stopping CRONOS service...")
        self._running = False
        # Cancel background tasks
        if self._backup_task and not self._backup_task.done():
            self._backup_task.cancel()
            try:
                await self._backup_task
            except asyncio.CancelledError:
                pass

        # Save state before disconnecting
        self._save_version_history()

        # Disconnect from Mycelium
        await self.interface.disconnect()
        self.logger.info("CRONOS service stopped.")

    # --- Core Functionality Methods --- #

    async def create_backup(
        self, name: str, backup_type: str = "manual", metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """Creates a new system backup using the configured logic."""
        self.logger.info(f"Initiating backup: Name='{name}', Type='{backup_type}'")
        start_time = datetime.now()
        backup_id = f"system_backup_{start_time.strftime('%Y%m%d_%H%M%S')}"
        backup_location = self.backup_base_path / backup_id
        metadata = metadata or {}
        metadata["trigger"] = backup_type

        try:
            backup_location.mkdir(parents=True, exist_ok=True)

            # Integrate file copy logic from backup_manager.py (CRONOSBackup class)
            # This needs refactoring of backup_manager.py or reimplementation here.
            # For now, conceptual call:
            (
                copied_files_count,
                skipped_files_count,
                skipped_dirs_count,
                bytes_copied,
            ) = await self._execute_backup_file_copy(backup_location)

            if copied_files_count is None:  # Indicate failure from helper
                raise Exception("File copy process failed.")

            # Capture state (placeholder)
            state_id = self._capture_current_state(backup_id)

            # Create and store backup metadata
            backup_info = SystemBackupInfo(
                id=backup_id,
                name=name,
                timestamp=start_time,
                backup_type=backup_type,
                state_id=state_id,
                location=backup_location,
                size_bytes=bytes_copied,
                file_count=copied_files_count,
                metadata=metadata,
            )
            self.backups[backup_id] = backup_info
            self._add_version_to_history(backup_info)
            self._save_version_history()

            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"Backup '{name}' ({backup_id}) completed successfully in {duration:.2f}s."
            )
            self.logger.info(
                f"Stats: {copied_files_count} files copied, {bytes_copied / (1024 * 1024):.2f} MB"
            )

            # Clean old backups based on retention policy
            await self.clean_old_backups()

            # Publish event
            await self.interface.publish_event(
                topic="event.cronos.backup_completed", payload=asdict(backup_info)
            )
            return backup_id

        except Exception as e:
            self.logger.error(f"Backup creation failed for '{name}': {e}", exc_info=True)
            # Attempt cleanup of partial backup directory
            if backup_location.exists():
                try:
                    shutil.rmtree(backup_location)
                except Exception as clean_e:
                    self.logger.error(
                        f"Failed to clean up partial backup {backup_location}: {clean_e}"
                    )
            await self.interface.publish_event(
                topic="event.cronos.backup_failed", payload={"name": name, "error": str(e)}
            )
            return None

    async def _execute_backup_file_copy(
        self, backup_location: Path
    ) -> Tuple[Optional[int], Optional[int], Optional[int], Optional[int]]:
        """Executes the file copying part of the backup.

        Integrates logic from the recovered backup_manager.py script.
        Walks the system_root, applies exclusions from config, and copies
        files to the target backup_location using shutil.copy2.

        Returns:
            Tuple (
                files_copied, files_skipped, dirs_skipped, bytes_copied
            ) or (None, None, None, None) on failure.
        """
        self.logger.info(f"Starting file copy process to {backup_location}...")
        files_copied = 0
        files_skipped = 0
        dirs_skipped = 0
        bytes_copied = 0
        # Get exclusions from loaded config
        excluded_dirs = set(self.config.get("excluded_directories", []))
        excluded_exts = set(self.config.get("excluded_extensions", []))
        # Get backup base path string relative to system root for exclusion check
        try:
            backup_base_rel_path = self.backup_base_path.relative_to(self.system_root).as_posix()
        except ValueError:
            # If backup path is not within system root (unlikely but possible)
            # We won't exclude it based on path prefix below
            self.logger.warning(
                f"Backup base path {self.backup_base_path} is outside system root "
                f"{self.system_root}. Cannot exclude based on prefix."
            )
            backup_base_rel_path = None

        try:
            # Use topdown=True to allow modifying dirs list
            for root, dirs, files in os.walk(self.system_root, topdown=True):
                current_root_path = Path(root)

                # --- Exclusion Logic --- #
                # 1. Exclude the entire backup destination base path
                if backup_base_rel_path and os.path.relpath(root, self.system_root).startswith(
                    backup_base_rel_path
                ):
                    self.logger.debug(f"Skipping backup directory itself: {root}")
                    dirs[:] = []  # Don't recurse further
                    continue

                # 2. Exclude specific directory names (anywhere in the path)
                original_dirs = list(dirs)  # Copy for iteration
                dirs[:] = []  # Clear dirs, we will re-add allowed ones
                skipped_in_level = 0
                for d in original_dirs:
                    is_excluded = False
                    # Check simple name exclusion
                    if d in excluded_dirs:
                        is_excluded = True
                    # Check if full path contains an excluded dir component
                    # (More robust check than just checking parent parts in should_exclude)
                    # This requires joining path segments carefully
                    # For simplicity, stick to name check here and potentially refine if needed

                    if is_excluded:
                        self.logger.debug(f"Excluding directory: {Path(root) / d}")
                        skipped_in_level += 1
                    else:
                        dirs.append(d)
                dirs_skipped += skipped_in_level
                # ----------------------- #

                # Process files in allowed directories
                for file in files:
                    src_path = current_root_path / file

                    # 3. Check extension exclusion
                    if src_path.suffix in excluded_exts:
                        self.logger.debug(f"Skipping file by extension: {src_path}")
                        files_skipped += 1
                        continue

                    # --- File Copying --- #
                    try:
                        # Create destination path
                        rel_file_path = src_path.relative_to(self.system_root)
                        dst_path = backup_location / rel_file_path

                        # Create parent directory for file if it doesn't exist
                        dst_path.parent.mkdir(parents=True, exist_ok=True)

                        # Copy file using copy2 to preserve metadata
                        shutil.copy2(src_path, dst_path)
                        files_copied += 1
                        try:
                            bytes_copied += src_path.stat().st_size
                        except FileNotFoundError:
                            self.logger.warning(
                                f"Source file disappeared during backup: {src_path}"
                            )
                            pass  # File might be gone, ignore size error but count as copied
                        except OSError as stat_e:
                            self.logger.warning(f"Could not get size of {src_path}: {stat_e}")
                            pass  # Ignore size if stat fails

                    except Exception as copy_e:
                        self.logger.error(f"Failed to copy {src_path} to {dst_path}: {copy_e}")
                        # Optionally: Increment an error count? Continue backup?
                        # For now, continue processing other files.
                        files_skipped += 1  # Count as skipped due to error
                    # ------------------- #

            self.logger.info("File copy process finished.")
            return files_copied, files_skipped, dirs_skipped, bytes_copied
        except Exception as e:
            self.logger.error(f"Error during file copy process: {e}", exc_info=True)
            return None, None, None, None

    async def clean_old_backups(self):
        """Cleans old backups based on retention policy."""
        # Integrate logic from backup_manager.py::CRONOSBackup.clean_old_backups
        self.logger.info("Running backup cleanup...")
        retention_policy = self.config.get("retention_policy", {})
        daily = retention_policy.get("daily", 7)
        weekly = retention_policy.get("weekly", 4)
        monthly = retention_policy.get("monthly", 12)
        keep_paths = set()
        weekly_kept = set()  # Store week numbers
        monthly_kept = set()  # Store month numbers
        today = datetime.now()

        for backup_path, timestamp in self.backups.items():
            days_diff = (today - timestamp.timestamp).days
            week_num = timestamp.timestamp.isocalendar()[1]
            month_num = timestamp.timestamp.month

            keep = False
            retention_cat = None

            # Keep dailies for the last N days
            if days_diff < daily:
                keep = True
                retention_cat = "daily"
            # Keep first backup of the week for N weeks
            elif days_diff < weekly * 7 and week_num not in weekly_kept:
                keep = True
                weekly_kept.add(week_num)
                retention_cat = "weekly"
            # Keep first backup of the month for N months
            elif days_diff < monthly * 31 and month_num not in monthly_kept:
                keep = True
                monthly_kept.add(month_num)
                retention_cat = "monthly"

            # Always keep the very latest backup regardless of policy for safety
            if backup_path == list(self.backups.keys())[-1]:
                keep = True
                retention_cat = retention_cat or "latest"

            if keep:
                keep_paths.add(backup_path)
                # Update metadata in self.backups if loaded
                backup_id = backup_path
                if backup_id in self.backups:
                    self.backups[backup_id].retention_category = retention_cat

        # Delete backups not in the keep set
        deleted_count = 0
        for backup_path, timestamp in self.backups.items():
            if backup_path not in keep_paths:
                self.logger.info(f"Deleting old backup (Reason: Retention Policy): {backup_path}")
                try:
                    shutil.rmtree(backup_path)
                    # Remove from in-memory dict as well
                    self.backups.pop(backup_path, None)
                    deleted_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to delete {backup_path}: {e}")

        self.logger.info(
            f"Backup cleanup completed. Kept {len(keep_paths)} backups, deleted {deleted_count}."
        )
        # Resave history after potential deletions
        self._save_version_history()

    def _capture_current_state(self, backup_id: str) -> str:
        """Captures current system state metadata, including git hash and config hashes."""
        state_id = f"state_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        state_name = f"State captured at {datetime.now().isoformat()}"
        self.logger.debug(f"Capturing system state {state_id} for backup {backup_id}")

        # --- Gather State Data --- #
        git_hash = self._get_git_commit_hash()
        config_hashes = self._get_config_hashes()

        # Placeholder: Gather OS/Environment Info
        os_info = {}
        try:
            import platform

            os_info = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "python_version": platform.python_version(),
            }
        except Exception as e:
            self.logger.warning(f"Could not capture OS info: {e}")

        # Placeholder: Gather Dependency Info (Example: parse requirements.txt)
        dependency_info = {}
        try:
            req_path = self.system_root / "requirements.txt"
            if req_path.exists():
                with open(req_path, "r", encoding="utf-8") as f:
                    # Simple parsing - might need more robust parsing for complex reqs
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            parts = re.split(r"==|>=|<=|>|<|~", line, maxsplit=1)  # Basic split
                            package = parts[0].strip()
                            version = parts[1].strip() if len(parts) > 1 else "any"
                            dependency_info[package] = version
        except Exception as e:
            self.logger.warning(f"Could not parse requirements.txt: {e}")

        # Placeholder: Gather Mycelium Status (Requires access to network instance)
        mycelium_status = {}
        # if self.interface and hasattr(self.interface, 'get_network_status'):
        #     try:
        #         mycelium_status = await self.interface.get_network_status() # Needs async?
        #     except Exception as e:
        #         logger.warning(f"Could not get Mycelium status: {e}")
        # --- End Gather State Data --- #

        state = SystemState(
            id=state_id,
            name=state_name,
            related_backup_id=backup_id,
            git_commit_hash=git_hash,
            config_hashes=config_hashes,
            subsystem_versions={},  # TODO: Populate via Mycelium later
            data={  # Store gathered non-core data here
                "os_info": os_info,
                "dependencies": dependency_info,
                "mycelium_snapshot": mycelium_status,  # Store snapshot
            },
            # metrics = {} # TODO: Capture key system metrics?
        )
        self.states[state_id] = state
        self.logger.info(f"Captured system state {state_id}")
        return state_id

    def _get_git_commit_hash(self) -> Optional[str]:
        """Attempts to get the current git commit hash."""
        if not shutil.which("git"):  # Check if git command exists
            self.logger.warning("Git command not found, cannot capture commit hash.")
            return None
        try:
            # Ensure running from the correct directory (project root)
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.system_root,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",  # Added encoding
            )
            return result.stdout.strip()
        except FileNotFoundError:  # Handle case where .git dir is missing
            self.logger.warning("Not a git repository, cannot capture commit hash.")
            return None
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error getting git commit hash: {e.stderr}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error getting git commit hash: {e}", exc_info=True)
            return None

    def _get_config_hashes(self) -> Dict[str, str]:
        """Calculates MD5 hashes for key configuration files."""
        config_files_to_hash = [
            "pyproject.toml",
            "requirements.txt",
            "subsystems/CRONOS/config/backup_config.json",
            # Add other critical config files, e.g.:
            # "BIOS-Q/config/bios_config.json",
            # ".cursorrules",
            # ".flake8",
            # "config/mcp_config.json" # If it exists at root
        ]
        hashes = {}
        for rel_path_str in config_files_to_hash:
            file_path = self.system_root / rel_path_str
            if file_path.exists() and file_path.is_file():
                try:
                    content = file_path.read_bytes()
                    file_hash = hashlib.md5(content).hexdigest()
                    hashes[rel_path_str] = file_hash
                except Exception as e:
                    self.logger.error(f"Error hashing config file {rel_path_str}: {e}")
                    hashes[rel_path_str] = "Error"
            else:
                self.logger.warning(f"Config file not found for hashing: {rel_path_str}")
                hashes[rel_path_str] = "NotFound"
        return hashes

    # --- History Management (from preservation.py) --- #
    def _load_version_history(self):
        """Loads the backup/version history from JSON file."""
        self.backups = {}
        self.states = {}
        if not self.version_history_file.exists():
            self.logger.warning(f"Version history file not found: {self.version_history_file}")
            self._save_version_history()  # Create an empty one
            return

        try:
            with open(self.version_history_file, "r", encoding="utf-8") as f:
                history = json.load(f)

            # Reconstruct backup objects
            for b_data in history.get("backups", []):
                try:
                    # Convert timestamp back to datetime
                    b_data["timestamp"] = datetime.fromisoformat(b_data["timestamp"])
                    # Convert location back to Path
                    b_data["location"] = self.backup_base_path / b_data["id"]  # Reconstruct path
                    backup = SystemBackupInfo(**b_data)
                    # Check if backup dir still exists
                    if backup.location.exists() and backup.location.is_dir():
                        self.backups[backup.id] = backup
                    else:
                        self.logger.warning(
                            f"Backup directory missing for history entry {backup.id}. Ignoring."
                        )
                except Exception as e:
                    self.logger.error(f"Error loading backup entry {b_data.get('id')}: {e}")

            # Reconstruct state objects (less critical for now)
            for s_data in history.get("states", []):
                try:
                    s_data["timestamp"] = datetime.fromisoformat(s_data["timestamp"])
                    state = SystemState(**s_data)
                    self.states[state.id] = state
                except Exception as e:
                    self.logger.error(f"Error loading state entry {s_data.get('id')}: {e}")

            self.logger.info(
                f"Version history loaded: {len(self.backups)} backups, {len(self.states)} states."
            )

        except Exception as e:
            self.logger.error(
                f"Failed to load or parse version history {self.version_history_file}: {e}",
                exc_info=True,
            )
            # Reset to empty if loading fails badly
            self.backups = {}
            self.states = {}

    def _add_version_to_history(self, backup_info: SystemBackupInfo):
        """Adds a new backup entry to the in-memory history."""
        # This method assumes history is saved separately by _save_version_history
        self.backups[backup_info.id] = backup_info
        if backup_info.state_id and backup_info.state_id in self.states:
            # Ensure state knows its related backup
            self.states[backup_info.state_id].related_backup_id = backup_info.id

    def _save_version_history(self):
        """Saves the current backup/state history to JSON file."""
        self.logger.debug("Saving version history...")
        history = {"last_updated": datetime.now().isoformat(), "backups": [], "states": []}
        try:
            # Sort backups newest first for saving
            sorted_backups = sorted(self.backups.values(), key=lambda b: b.timestamp, reverse=True)
            for backup in sorted_backups:
                b_dict = asdict(backup)
                # Convert Path back to string relative to base for saving
                b_dict["location"] = backup.id  # Store only ID, reconstruct path on load
                b_dict["timestamp"] = backup.timestamp.isoformat()
                history["backups"].append(b_dict)

            # Sort states newest first
            sorted_states = sorted(self.states.values(), key=lambda s: s.timestamp, reverse=True)
            for state in sorted_states:
                s_dict = asdict(state)
                s_dict["timestamp"] = state.timestamp.isoformat()
                history["states"].append(s_dict)

            with open(self.version_history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, default=str)
            self.logger.info(f"Version history saved to {self.version_history_file}")
        except Exception as e:
            self.logger.error(f"Failed to save version history: {e}", exc_info=True)

    # --- Placeholder methods from cronos_core.py/preservation.py --- #
    # These need proper implementation based on chosen strategy

    async def verify_backup_integrity(self, backup_info: SystemBackupInfo) -> bool:
        """Verify the integrity of a specific backup.

        Checks if the backup directory exists and if it contains any
        directories that should have been excluded based on config.
        (Future: Could add checksum verification)
        """
        self.logger.info(f"Verifying integrity of backup: {backup_info.id}...")
        backup_path = backup_info.location

        # 1. Basic check: Does the directory exist?
        if not backup_path.exists() or not backup_path.is_dir():
            self.logger.error(
                f"Integrity check failed: Backup directory not found at {backup_path}"
            )
            return False

        # 2. Check for included problematic directories (from verify_cleanup.py)
        problems_found = []
        problematic_dirs = set(self.config.get("excluded_directories", []))
        try:
            for root, dirs, files in os.walk(backup_path):
                # Check only immediate subdirectories within the walk for simplicity?
                # Or check all nested dirs?
                # Checking all nested dirs is more thorough:
                for d in dirs:
                    # Check based on name
                    if d in problematic_dirs:
                        rel_path = Path(root) / d
                        problems_found.append(str(rel_path.relative_to(backup_path)))
                        self.logger.warning(
                            f"Integrity issue: Problematic directory '{d}' found "
                            f"within backup at {rel_path.relative_to(backup_path)}"
                        )

            if problems_found:
                self.logger.error(
                    f"Integrity check failed: Found {len(problems_found)} "
                    f"problematic directories inside backup {backup_info.id}."
                )
                # Optionally, list problems here or return them?
                return False
            else:
                self.logger.info(
                    f"Integrity check passed for {backup_info.id} (Excluded directory check)."
                )
                return True

        except Exception as e:
            self.logger.error(
                f"Error during integrity check for {backup_info.id}: {e}", exc_info=True
            )
            return False

    def check_for_stray_backups(self) -> List[str]:
        """Scans the project root for potential old/stray backup directories
        that are not managed by the current CRONOS instance.

        Returns:
            List of relative paths to potential stray backup directories.
        """
        self.logger.info("Scanning for potential stray backup directories...")
        stray_backups = []
        # Define patterns that might indicate a backup folder
        backup_patterns = set(
            self.config.get("stray_backup_patterns", ["backup", "bkp", "_backup", "_bkp"])
        )  # Add more patterns if needed

        current_backup_ids = set(self.backups.keys())
        latest_backup_path = self.backup_base_path  # Use the base path for comparison

        try:
            for item in self.system_root.rglob("*"):  # Use rglob for recursive search
                if item.is_dir():
                    # Check if dir name contains any backup pattern
                    if any(pattern in item.name.lower() for pattern in backup_patterns):
                        # Check if it's inside the main backup location AND is managed
                        is_managed = False
                        try:
                            if (
                                item.relative_to(latest_backup_path)
                                and item.name in current_backup_ids
                            ):
                                is_managed = True
                        except ValueError:  # Not relative to the main backup path
                            pass

                        # Check if it *is* the main backup path itself
                        if item == latest_backup_path:
                            is_managed = True

                        if not is_managed:
                            rel_path = str(item.relative_to(self.system_root))
                            self.logger.warning(
                                f"Potential stray backup directory found: {rel_path}"
                            )
                            stray_backups.append(rel_path)
        except Exception as e:
            self.logger.error(f"Error scanning for stray backups: {e}", exc_info=True)

        if not stray_backups:
            self.logger.info("No potential stray backup directories found.")
        return stray_backups

    def _restore_system_state(self, state_id: str) -> bool:
        """(Placeholder) Restore system files/config from a state/backup."""
        # This is the most complex part - needs a strategy.
        # Overwrite existing files? Restore to different location?
        self.logger.error(f"System state restore for {state_id} not implemented.")
        return False

    def _calculate_directory_size(self, path: Path) -> int:
        """Calculates the total size of a directory."""
        total_size = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file():
                    total_size += entry.stat().st_size
                elif entry.is_dir():
                    total_size += self._calculate_directory_size(Path(entry.path))
        except FileNotFoundError:
            self.logger.warning(f"Directory not found for size calculation: {path}")
        except Exception as e:
            self.logger.error(f"Error calculating size for {path}: {e}")
        return total_size

    # --- New Helper for Initial/Periodic Backup Check --- #
    async def _check_and_perform_backup(self):
        """Checks history and performs backup if needed based on interval."""
        backup_needed = False
        reason = ""
        last_backup_timestamp = None

        # Sort existing backups (loaded in self.backups during _load_version_history)
        sorted_backups = sorted(self.backups.values(), key=lambda b: b.timestamp, reverse=True)

        if not sorted_backups:
            backup_needed = True
            reason = "Initial system backup (no previous history)"
        else:
            try:
                last_backup_timestamp = sorted_backups[0].timestamp
                # Ensure it's offset-aware for comparison if needed, assume UTC for now
                # last_backup_timestamp = last_backup_timestamp.replace(
                #     tzinfo=datetime.timezone.utc
                # )
                now = datetime.now()  # Or datetime.now(datetime.timezone.utc)
                hours_since_last = (now - last_backup_timestamp).total_seconds() / 3600
                interval_hours = self.config.get("backup_interval_hours", 12)

                self.logger.info(f"Time since last backup: {hours_since_last:.1f} hours.")
                if hours_since_last > interval_hours:
                    backup_needed = True
                    reason = (
                        f"Automatic backup (interval: {interval_hours}h, "
                        f"last: {hours_since_last:.1f}h ago)"
                    )
                else:
                    self.logger.info(
                        f"Recent backup found ({hours_since_last:.1f}h ago). "
                        f"No automatic backup needed now."
                    )

            except Exception as e:
                self.logger.warning(
                    f"Could not reliably determine time since last backup: {e}. "
                    f"Performing backup as precaution."
                )
                backup_needed = True
                reason = "Precautionary backup (error determining last backup time)"

        if backup_needed:
            self.logger.info(f"Performing backup. Reason: {reason}")
            await self.create_backup(name=reason.split("(")[0].strip(), backup_type="automatic")

    # --- Mycelium Request Handlers (New/Updated) --- #

    async def handle_create_backup_request(self, message: Dict[str, Any]):
        # ... (existing backup handler) ...
        pass

    async def handle_list_backups_request(self, message: Dict[str, Any]):
        """Handles requests to list available backups."""
        request_id = message.get("id", "unknown")
        self.logger.info(f"Received list_backups request: {request_id}")
        response_topic = f"response.{self.node_id}.{request_id}"
        try:
            # Call the BackupManager method (to be implemented)
            backup_list = self.backup_manager.list_backups()
            response_payload = {"success": True, "backups": backup_list}
            await self.interface.publish(
                response_topic, {"type": "list_backups_response", "payload": response_payload}
            )
            self.logger.info(
                f"Processed list_backups request {request_id}. Found {len(backup_list)} backups."
            )
        except Exception as e:
            self.logger.error(
                f"Error handling list_backups request {request_id}: {e}", exc_info=True
            )
            await self.interface.publish(
                response_topic, {"type": "error", "payload": {"message": str(e)}}
            )

    async def handle_restore_backup_request(self, message: Dict[str, Any]):
        """Handles requests to restore a specific backup."""
        request_id = message.get("id", "unknown")
        self.logger.info(f"Received restore_backup request: {request_id}")
        response_topic = f"response.{self.node_id}.{request_id}"
        try:
            payload = message.get("payload", {})
            backup_identifier = payload.get("backup_identifier")  # e.g., filename or timestamp
            restore_target_path = payload.get("restore_target_path")  # Where to restore
            strategy = payload.get("strategy", "new_location")  # e.g., "new_location", "overwrite"

            if not backup_identifier:
                raise ValueError("Missing 'backup_identifier' in payload.")
            # Target path validation might be needed depending on strategy
            if strategy != "new_location" and not restore_target_path:
                raise ValueError(
                    "'restore_target_path' is required for non-'new_location' strategies."
                )

            self.logger.warning(
                f"Initiating restore for backup '{backup_identifier}' with strategy '{strategy}'."
            )
            # *** Execute the restore via BackupManager ***
            success, details = await self.backup_manager.restore_backup(
                backup_identifier=backup_identifier,
                restore_target_path=restore_target_path,
                strategy=strategy,
            )

            response_payload = {"success": success, "details": details}
            await self.interface.publish(
                response_topic, {"type": "restore_backup_response", "payload": response_payload}
            )
            self.logger.info(f"Processed restore_backup request {request_id}. Success: {success}")

        except Exception as e:
            self.logger.error(
                f"Error handling restore_backup request {request_id}: {e}", exc_info=True
            )
            await self.interface.publish(
                response_topic, {"type": "error", "payload": {"message": str(e)}}
            )


# --- Standard Subsystem Initializer --- #
def initialize_cronos(mycelium_network_instance: MyceliumNetwork) -> Optional[CronosService]:
    """Standard async initializer for the CRONOS subsystem."""
    module_logger.info("Attempting to initialize CRONOS...")
    try:
        # Load CRONOS specific config (adjust path as needed)
        config_path = Path("subsystems/CRONOS/config/backup_config.json")
        config = {}
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            module_logger.warning(f"CRONOS config file not found at {config_path}. Using defaults.")
            # Provide default config if file missing?

        # Add system root if not in config (needed by service)
        config["system_root"] = "/c/EGOS/"

        interface = MyceliumInterface(mycelium_network_instance, "CRONOS")
        service = CronosService(config, interface, Path(config["system_root"]))
        # Don't start automatically, let BIOS-Q manage lifecycle via start()
        # await service.start()
        module_logger.info("CRONOS initialized, awaiting start command.")
        return service
    except Exception as e:
        module_logger.error(f"CRONOS initialization failed: {e}", exc_info=True)
        return None

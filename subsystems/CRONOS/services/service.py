"""Core service implementation for the CRONOS subsystem."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import json
import logging
import os
from pathlib import Path
import platform
import subprocess
from typing import Any, Dict, List, Optional

# Correct Koios Logger import path assuming standard structure
try:
    from ..KOIOS.core.logger import KoiosLogger
except ImportError:
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger(__name__).warning(
        "Could not import KoiosLogger from relative path. Check structure.", exc_info=True
    )
    raise

# Assuming Mycelium Interface is available for injection
from ..MYCELIUM.core.interface import MyceliumInterface
from ..MYCELIUM.core.network import MyceliumNetwork

# Import the new BackupManager
from .core.backup_manager import BackupManager

# Import the new PidManager
from .core.pid_manager import PidManager

# Import functions from migrated scripts (or refactor them into this class)
try:
    from .scripts.backup_manager import CRONOSBackup as BackupManager
except ImportError:
    module_logger = KoiosLogger.get_logger("CRONOS.ServiceModule")
    module_logger.warning(
        "Could not import backup/verification scripts directly. Functionality needs integration."
    )
    BackupManager = None

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
        self.node_id = "CRONOS_SERVICE"
        self.system_root = project_root
        self.backup_base_path = self.system_root / Path(
            self.config.get("backup_location", "backups/CRONOS")
        )
        self.version_history_file = self.backup_base_path / "version_history.json"
        # PID file path is now managed by PidManager, but base path needed here?
        # self.pid_file_path = self.backup_base_path / f"{self.node_id}.pid" # Moved to PidManager

        # --- Setup Loggers using Koios --- #
        log_config = self.config.get("logging", {})
        self.logger = KoiosLogger.get_logger(f"EGOS.{self.node_id}", config=log_config)
        # --------------------------------- #

        # --- Initialize PID Manager --- #
        pid_file_path = self.backup_base_path / f"{self.node_id}.pid"
        self.pid_manager = PidManager(pid_file_path=pid_file_path, logger=self.logger)
        # ----------------------------- #

        self.states: Dict[str, SystemState] = {}
        # self.backups: Dict[str, SystemBackupInfo] = {} # History now managed by BackupManager

        self._backup_task: Optional[asyncio.Task] = None
        self._running = False
        self.lock = asyncio.Lock()
        self.stop_event = asyncio.Event()

        # Instantiate BackupManager if available
        self.backup_manager = BackupManager(
            backup_base_path=self.backup_base_path,
            history_file_path=self.version_history_file,
            config=self.config,
            logger=self.logger,
        )
        # ------------------------------ #

        self.logger.info(f"CRONOS Service initialized. Backup location: {self.backup_base_path}")

        # Update the config with the determined root (ensure it's string for JSON later)
        resolved_root_path = str(self.system_root.resolve())
        self.config["system_root"] = resolved_root_path
        self.logger.info(f"Resolved system_root in config: {self.config['system_root']}")

    async def start(self):
        """Start the CRONOS service and connect to Mycelium."""
        if self._running:
            self.logger.warning("CRONOS service already running.")
            return

        self.logger.info("Starting CRONOS service...")
        try:
            self.backup_base_path.mkdir(parents=True, exist_ok=True)
            # Use PidManager to check/create PID file
            self.pid_manager.check_and_create_pid()
        except (OSError, PermissionError) as e:
            error_msg = (
                f"Failed to create backup directory or PID file {self.backup_base_path}: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            return  # Cannot operate without backup dir or PID file
        except RuntimeError as e:  # Catch PID file specific runtime error
            self.logger.critical(f"PID file check failed: {e}. Aborting start.")
            return

        # self._load_version_history() # Moved to BackupManager init

        try:
            await self._check_and_perform_backup()
        except (OSError, PermissionError, asyncio.TimeoutError) as e:
            # More specific errors during backup check
            self.logger.error(f"Error during initial backup check: {e}", exc_info=True)
            # Log and continue startup
        except Exception as e:  # Catch any other unexpected error during backup check
            self.logger.error(f"Unexpected error during initial backup check: {e}", exc_info=True)

        connected = await self.interface.connect(
            node_type="PRESERVATION",
            # TODO: Make version dynamic from config/source
            version=self.config.get("version", "0.1.0"),
            capabilities=["backup", "restore", "state_mgmt", "history", "cleanup"],
        )
        if not connected:
            self.logger.error("CRONOS failed to connect to Mycelium Network!")
            # Use PidManager to remove PID file
            self.pid_manager.remove_pid_file()
            return

        try:
            await self.interface.subscribe(
                f"request.{self.node_id}.list_backups", self.handle_list_backups_request
            )
            await self.interface.subscribe(
                f"request.{self.node_id}.restore_backup", self.handle_restore_backup_request
            )
            await self.interface.subscribe(
                f"request.{self.node_id}.create_backup", self.handle_create_backup_request
            )
            await self.interface.subscribe(
                f"request.{self.node_id}.cleanup_backups", self.handle_cleanup_request
            )

            self.logger.info("Subscribed to CRONOS request topics.")
        except Exception as e:  # Catch potential Mycelium subscription errors
            self.logger.error(f"Failed to subscribe to CRONOS request topics: {e}", exc_info=True)
            # Attempt graceful disconnect only if interface likely exists
            if self.interface:
                try:
                    await self.interface.disconnect()
                except Exception as disc_e:
                    disc_error = f"Error during disconnect after subscription failure: {disc_e}"
                    self.logger.error(disc_error)
            # Use PidManager to remove PID file
            self.pid_manager.remove_pid_file()
            return

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
        self.stop_event.set()  # Signal tasks relying on self._running to stop

        # Cancel background tasks (e.g., ongoing backup)
        if self._backup_task and not self._backup_task.done():
            self._backup_task.cancel()
            try:
                await self._backup_task
            except asyncio.CancelledError:
                self.logger.info("Ongoing backup task cancelled.")
            except Exception as e:  # Catch other potential errors during task await
                self.logger.error(f"Error waiting for backup task cancellation: {e}", exc_info=True)

        # Save state before disconnecting
        # self._save_version_history() # Moved to BackupManager

        # Disconnect from Mycelium
        try:
            if self.interface:  # Check if interface exists
                await self.interface.disconnect()
        except Exception as e:  # Catch potential disconnect errors
            self.logger.error(f"Error disconnecting from Mycelium: {e}", exc_info=True)

        # Use PidManager to remove PID file
        self.pid_manager.remove_pid_file()
        self.logger.info("CRONOS service stopped.")

    # --- Backup Creation --- #

    async def create_backup(
        self, name: str, backup_type: str = "manual", metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """Creates a new system backup using the configured logic."""
        # Delegate to BackupManager
        return await self.backup_manager.create_backup(name, backup_type, metadata)

    # --- Backup Cleanup --- #

    async def clean_old_backups(self):
        """Cleans up old backups based on the configured retention policy."""
        # Delegate to BackupManager
        await self.backup_manager.clean_old_backups()

    # --- State Capture --- #

    def _capture_current_state(self, backup_id: Optional[str] = None) -> str:
        """Captures essential system state metadata."""
        self.logger.debug("Capturing current system state...")
        now = datetime.now()
        state_id = f"state_{now.strftime('%Y%m%d_%H%M%S')}"
        name = f"System State Snapshot {now.strftime('%Y-%m-%d %H:%M:%S')}"

        # Gather state information using helper methods
        git_hash = self._get_git_commit_hash()
        config_hashes = self._get_config_hashes()
        system_info = self._get_system_info()
        # subsystem_versions = self._get_subsystem_versions() # Placeholder

        state = SystemState(
            id=state_id,
            name=name,
            timestamp=now,
            related_backup_id=backup_id,
            git_commit_hash=git_hash,
            config_hashes=config_hashes,
            # subsystem_versions=subsystem_versions,
            metadata={"system_info": system_info},  # Store system info in metadata
            metrics={},  # TODO: Populate via Mycelium later?
        )

        self.states[state_id] = state
        self.logger.info(f"Captured system state: ID='{state_id}'")

        # Optionally save state immediately or rely on backup history save
        # self._save_state(state) # If storing states separately

        return state_id

    def _get_system_info(self) -> Dict[str, str]:
        """Gets basic OS and Python info."""
        try:
            info = {
                "os": platform.system(),
                "os_release": platform.release(),
                "os_version": platform.version(),
                "architecture": platform.machine(),
                "python_version": platform.python_version(),
            }
            return info
        except (AttributeError, RuntimeError) as e:
            error_msg = f"Could not retrieve system info due to platform interface error: {e}"
            self.logger.warning(error_msg)
            return {"error": str(e)}
        except Exception as e:
            error_msg = f"Unexpected critical error retrieving system info: {e}"
            self.logger.error(error_msg, exc_info=True)
            return {"error": f"Critical error: {str(e)}"}

    def _get_git_commit_hash(self) -> Optional[str]:
        """Retrieves the current Git commit hash of the project root."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.system_root,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,  # Add timeout
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            self.logger.warning(f"Could not retrieve Git commit hash: {e}")
            return None
        except (PermissionError, OSError) as e:
            self.logger.error(f"File system error accessing Git repository: {e}", exc_info=True)
            return None
        except ValueError as e:
            self.logger.error(f"Invalid argument in Git command: {e}", exc_info=True)
            return None

    def _get_config_hashes(self) -> Dict[str, str]:
        """Calculates hashes for key configuration files."""
        hashes = {}
        config_paths_to_track = self.config.get("config_files_to_track", [])
        # Example: ["config/main_config.json", "subsystems/CRONOS/config/cronos_config.yaml"]

        for relative_path_str in config_paths_to_track:
            try:
                # Ensure paths are relative to system_root
                if os.path.isabs(relative_path_str):
                    skip_msg = (
                        f"Skipping absolute path in config_files_to_track: {relative_path_str}"
                    )
                    self.logger.warning(skip_msg)
                    continue

                full_path = self.system_root / Path(relative_path_str)
                if full_path.is_file():
                    with open(full_path, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                        # Store relative path as key for consistency
                        hashes[relative_path_str] = file_hash
                else:
                    self.logger.warning(f"Config file to track not found: {full_path}")
            except (IOError, OSError) as e:
                self.logger.error(f"Error hashing config file {relative_path_str}: {e}")
            except (TypeError, ValueError) as e:
                error_msg = f"Data format error for config file {relative_path_str}: {e}"
                self.logger.error(error_msg, exc_info=True)
            except PermissionError as e:
                error_msg = f"Permission error accessing config file {relative_path_str}: {e}"
                self.logger.error(error_msg, exc_info=True)

        return hashes

    # --- History Management (MOVED TO BackupManager) --- #
    # def _load_version_history(self): ...
    # def _add_version_to_history(self, backup_info: SystemBackupInfo): ...
    # def _save_version_history(self): ...

    # --- Backup Verification --- #

    async def verify_backup_integrity(self, backup_info: SystemBackupInfo) -> bool:
        """Verifies the integrity of a backup (file count and hashes)."""
        self.logger.info(f"Verifying integrity of backup: {backup_info.id}")
        hash_file_path = backup_info.location / "manifest.sha256"

        file_count_correct = await self._verify_file_count(backup_info)
        hashes_match = await self._verify_file_hashes(backup_info.location, hash_file_path)

        is_valid = file_count_correct and hashes_match

        if is_valid:
            self.logger.info(f"Integrity verification successful for backup: {backup_info.id}")
            backup_info.metadata["last_verified"] = datetime.now().isoformat()
            backup_info.metadata["integrity_status"] = "valid"
        else:
            self.logger.warning(f"Integrity verification FAILED for backup: {backup_info.id}")
            backup_info.metadata["integrity_status"] = "failed"
            await self.interface.publish(
                f"alert.{self.node_id}.backup_integrity_failed",
                {"backup_id": backup_info.id, "reason": "Mismatch in file count or hashes"},
            )
        return is_valid

    async def _verify_file_count(self, backup_info: SystemBackupInfo) -> bool:
        """Verifies if the actual file count matches the recorded count."""
        try:
            actual_file_count = sum(1 for item in backup_info.location.rglob("*") if item.is_file())
            if actual_file_count == backup_info.file_count:
                self.logger.debug(f"File count matches for {backup_info.id}: {actual_file_count}")
                return True

            count_error = (
                f"File count mismatch for {backup_info.id}: "
                f"Expected={backup_info.file_count}, Found={actual_file_count}"
            )
            self.logger.warning(count_error)
            return False
        except (OSError, PermissionError) as e:
            self.logger.error(f"Error counting files in {backup_info.location}: {e}")
            return False
        except FileNotFoundError as e:
            self.logger.error(f"Backup directory not found for {backup_info.id}: {e}")
            return False
        except (RuntimeError, RecursionError) as e:
            error_msg = f"Runtime error during file counting for {backup_info.id}: {e}"
            self.logger.error(error_msg, exc_info=True)
            return False

    async def _verify_file_hashes(self, backup_location: Path, hash_file_path: Path) -> bool:
        """Verifies file hashes against a manifest file."""
        if not hash_file_path.is_file():
            file_error = f"Hash manifest file not found: {hash_file_path}. Cannot verify hashes."
            self.logger.warning(file_error)
            return False

        try:
            with open(hash_file_path, "r", encoding="utf-8") as f:
                manifest_lines = f.readlines()

            all_hashes_match = True
            for line in manifest_lines:
                line = line.strip()
                if not line or " " not in line:
                    continue
                try:
                    expected_hash, relative_path_str = line.split(" ", 1)
                except ValueError:
                    self.logger.warning(f"Skipping malformed manifest line: {line}")
                    continue

                # Convert path separators for current OS
                relative_path_str = (
                    relative_path_str.strip().replace("/", os.sep).replace("\\", os.sep)
                )

                file_path = backup_location / relative_path_str
                if not file_path.is_file():
                    self.logger.warning(f"File listed in manifest not found: {file_path}")
                    all_hashes_match = False
                    continue
                try:
                    with open(file_path, "rb") as item_f:
                        actual_hash = hashlib.sha256(item_f.read()).hexdigest()
                    if actual_hash != expected_hash:
                        hash_error = (
                            f"Hash mismatch for {relative_path_str}: "
                            f"Expected={expected_hash}, Found={actual_hash}"
                        )
                        self.logger.warning(hash_error)
                        all_hashes_match = False
                except (IOError, OSError) as e:
                    self.logger.error(f"Error reading file {file_path} for hash verification: {e}")
                    all_hashes_match = False
            return all_hashes_match

        except (IOError, OSError) as e:
            self.logger.error(f"Error reading manifest file {hash_file_path}: {e}")
            return False
        except (ValueError, TypeError) as e:
            error_msg = f"Data format error in manifest file {hash_file_path}: {e}"
            self.logger.error(error_msg, exc_info=True)
            return False
        except FileNotFoundError as e:
            error_msg = f"File or directory not found during hash verification: {e}"
            self.logger.error(error_msg, exc_info=True)
            return False

    # --- Utility Methods --- #

    def check_for_stray_backups(self) -> List[str]:
        """Identifies backup directories present on disk but not in the history."""
        stray_dirs = []
        try:
            if not self.backup_base_path.is_dir():
                return []  # No backup location, no strays

            # Ensure history is loaded
            # self._load_version_history() # Consider if this should be forced or rely on state

            for item in self.backup_base_path.iterdir():
                if item.is_dir() and item.name not in self.backup_manager.list_backups():
                    # Basic check: does it look like a backup ID?
                    if item.name.startswith("system_backup_") or item.name.startswith(
                        tuple(self.config.get("known_backup_prefixes", []))
                    ):
                        stray_dirs.append(item.name)
            if stray_dirs:
                self.logger.warning(f"Found {len(stray_dirs)} potential stray backup directories.")
        except (OSError, PermissionError) as e:
            self.logger.error(f"Error checking for stray backups in {self.backup_base_path}: {e}")
        except Exception as e:  # Catch other unexpected errors
            self.logger.error(f"Unexpected error checking for stray backups: {e}", exc_info=True)

        return stray_dirs

    def _restore_system_state(self, state_id: str) -> bool:
        """Restores system state from captured data (Placeholder)."""
        # This would involve potentially checking out a git commit,
        # restoring config files, etc. Complex and needs careful design.
        state = self.states.get(state_id)
        if not state:
            self.logger.error(f"Cannot restore: System state '{state_id}' not found.")
            return False
        self.logger.warning(f"System state restore for '{state_id}' is not fully implemented.")
        # Placeholder: Log what would be done
        if state.git_commit_hash:
            self.logger.info(f"Would attempt to check out git commit: {state.git_commit_hash}")
        # Restore config files based on hashes? Risky.
        return False  # Return False as it's not implemented

    def _calculate_directory_size(self, path: Path) -> int:
        """Calculates the total size of a directory."""
        total_size = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    try:
                        total_size += item.stat().st_size
                    except (OSError, FileNotFoundError, PermissionError) as stat_err:
                        # More specific stat errors
                        stat_msg = f"Could not get size for file {item}: {stat_err}"
                        self.logger.warning(stat_msg)
        except (OSError, PermissionError) as e:
            self.logger.error(f"Error calculating size for directory {path}: {e}")
        except Exception as e:  # Catch other unexpected errors during iteration
            error_msg = f"Unexpected error calculating directory size {path}: {e}"
            self.logger.error(error_msg, exc_info=True)
        return total_size

    async def _check_and_perform_backup(self):
        """Checks if a backup is needed based on policy and performs it."""
        # Example policy: backup if last backup is older than 'min_backup_interval_hours'
        interval_hours = self.config.get("backup_interval_hours", 24)
        # self._load_version_history() # Ensure history is fresh

        last_backup_time: Optional[datetime] = None
        if self.backup_manager.list_backups():
            last_backup = max(self.backup_manager.list_backups(), key=lambda b: b.timestamp)
            last_backup_time = last_backup.timestamp

        needs_backup = False
        if not last_backup_time:
            self.logger.info("No previous backup found. Performing initial backup.")
            needs_backup = True
        else:
            time_since_last = datetime.now() - last_backup_time
            if time_since_last > timedelta(hours=interval_hours):
                scheduled_msg = (
                    f"Last backup is older than {interval_hours} hours. "
                    "Performing scheduled backup."
                )
                self.logger.info(scheduled_msg)
                needs_backup = True
            else:
                skip_msg = f"Last backup was recent ({time_since_last}). Skipping scheduled backup."
                self.logger.info(skip_msg)

        if needs_backup:
            # Use a descriptive name for scheduled backups
            backup_name = f"scheduled_backup_{datetime.now().strftime('%Y%m%d')}"
            # Use 'scheduled' type
            await self.create_backup(name=backup_name, backup_type="scheduled")

    # --- Request Handlers --- #

    async def handle_create_backup_request(self, message: Dict[str, Any]):
        """Handles requests to manually create a backup."""
        request_id = message["header"]["message_id"]
        payload = message["payload"]
        response_topic = f"response.{self.node_id}.{request_id}"

        # Create default backup name with timestamp if not provided
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"manual_backup_{timestamp_str}"
        backup_name = payload.get("name", default_name)

        # Allow passing custom metadata
        metadata = payload.get("metadata")
        self.logger.info(f"Received manual backup request '{request_id}': Name='{backup_name}'")

        try:
            # Delegate backup creation to the manager
            backup_id = await self.backup_manager.create_backup(
                name=backup_name, backup_type="manual", metadata=metadata
            )

            if backup_id:
                success_response = {"status": "success", "backup_id": backup_id}
                await self.interface.publish(response_topic, success_response)
            else:
                error_response = {"status": "error", "message": "Backup creation failed."}
                await self.interface.publish(response_topic, error_response)

        except Exception as e:  # Catch unexpected errors during backup call or publish
            self.logger.error(
                f"Error handling create backup request '{request_id}': {e}", exc_info=True
            )
            try:
                error_msg = f"Internal server error: {e}"
                await self.interface.publish(
                    response_topic, {"status": "error", "message": error_msg}
                )
            except Exception as pub_e:
                pub_error = f"Failed to publish error response for request '{request_id}': {pub_e}"
                self.logger.error(pub_error)

    async def handle_list_backups_request(self, message: Dict[str, Any]):
        """Handles requests to list available backups."""
        request_id = message["header"]["message_id"]
        response_topic = f"response.{self.node_id}.{request_id}"
        self.logger.info(f"Received list backups request '{request_id}'")

        try:
            # Delegate listing to the manager
            backup_list = self.backup_manager.list_backups()
            # History is already loaded by manager, sorting is internal if needed
            # Sorting might happen in list_backups if desired
            # backup_list.sort(key=lambda b: b.get("timestamp", ""), reverse=True)

            success_response = {"status": "success", "backups": backup_list}
            await self.interface.publish(response_topic, success_response)

        except (IOError, json.JSONDecodeError) as e:
            # Specific load errors (less likely now?) - Keep for safety?
            error_msg = f"Error loading history for list backups request '{request_id}': {e}"
            self.logger.error(error_msg, exc_info=True)

            response = {"status": "error", "message": f"Internal error loading history: {e}"}
            await self.interface.publish(response_topic, response)

        except Exception as e:  # Catch other errors during processing/publish
            error_msg = f"Error handling list backups request '{request_id}': {e}"
            self.logger.error(error_msg, exc_info=True)

            try:
                response = {"status": "error", "message": f"Internal error listing backups: {e}"}
                await self.interface.publish(response_topic, response)
            except Exception as pub_e:
                pub_error = f"Failed to publish error response for request '{request_id}': {pub_e}"
                self.logger.error(pub_error)

    async def handle_restore_backup_request(self, message: Dict[str, Any]):
        """Handles requests to restore a specific backup (Placeholder)."""
        payload = message.get("payload", {})
        request_id = message.get("id", "unknown_request")
        response_topic = f"response.{self.node_id}.{request_id}"
        backup_id = payload.get("backup_id")

        request_info = (
            f"Received restore request for backup ID: '{backup_id}', Request ID='{request_id}'"
        )
        self.logger.info(request_info)

        if not backup_id:
            missing_id_msg = "Missing 'backup_id' in payload."
            await self.interface.publish(
                response_topic, {"status": "error", "message": missing_id_msg}
            )
            return

        self.logger.warning(f"Restore functionality for backup '{backup_id}' is not implemented.")

        not_implemented_msg = "Restore functionality not implemented."
        await self.interface.publish(
            response_topic, {"status": "error", "message": not_implemented_msg}
        )

    async def handle_cleanup_request(self, message: Dict[str, Any]):
        """Handles requests to manually trigger backup cleanup."""
        request_id = message.get("id", "unknown_request")
        response_topic = f"response.{self.node_id}.{request_id}"
        self.logger.info(f"Received cleanup request '{request_id}'")

        try:
            # Delegate cleanup to the manager
            await self.backup_manager.clean_old_backups()

            success_msg = "Cleanup process completed."
            await self.interface.publish(
                response_topic, {"status": "success", "message": success_msg}
            )

        except (OSError, PermissionError) as e:
            error_msg = f"Error during manual cleanup request '{request_id}': {e}"
            self.logger.error(error_msg, exc_info=True)

            fs_error_msg = f"Cleanup failed due to filesystem error: {e}"
            await self.interface.publish(
                response_topic, {"status": "error", "message": fs_error_msg}
            )

        except Exception as e:  # Catch potential errors during cleanup or publish
            error_msg = f"Error handling cleanup request '{request_id}': {e}"
            self.logger.error(error_msg, exc_info=True)

            try:
                simple_error_msg = f"Cleanup failed: {e}"
                await self.interface.publish(
                    response_topic, {"status": "error", "message": simple_error_msg}
                )
            except Exception as pub_e:
                pub_error = f"Failed to publish error response for request '{request_id}': {pub_e}"
                self.logger.error(pub_error)


# --- Service Initializer --- #


def initialize_cronos(mycelium_network_instance: MyceliumNetwork) -> Optional[CronosService]:
    """Initializes and configures the CRONOS service."""
    module_logger.info("Initializing CRONOS subsystem...")
    if not mycelium_network_instance:
        module_logger.critical("Mycelium network instance is required but not provided.")
        return None

    try:
        # --- Configuration Loading ---
        # Determine project root robustly (adjust if needed)
        try:
            project_root = Path(__file__).parent.parent.parent.resolve()
            module_logger.info(f"Determined project root: {project_root}")
        except NameError:  # __file__ might not be defined in some contexts (e.g. interactive)
            project_root = Path(".").resolve()  # Fallback to current working directory
            root_msg = f"Could not determine project root via __file__, using cwd: {project_root}"
            module_logger.warning(root_msg)

        # Load main config - requires a central config loading mechanism
        # For now, assume a simple path relative to this file or project root
        config_path = project_root / "config" / "main_config.json"  # Or other central config
        if not config_path.exists():
            # Try specific cronos config as fallback for standalone testing
            cronos_config_file = "subsystems/CRONOS/config/cronos_config.yaml"
            config_path = project_root / cronos_config_file  # Adjust extension if yaml
            if not config_path.exists():
                module_logger.error("CRONOS configuration not found at expected paths.")
                # Try loading default from backup_manager if exists? Less ideal.
                return None

        # Load the specific config file (adapt loader for yaml/json)
        config = {}
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                if config_path.suffix in [".yaml", ".yml"]:
                    # Use safe_load for YAML
                    import yaml  # Import yaml only when needed

                    config = yaml.safe_load(f)
                elif config_path.suffix == ".json":
                    config = json.load(f)
                else:
                    module_logger.error(f"Unsupported config file format: {config_path.suffix}")
                    return None
            module_logger.info(f"Loaded configuration from: {config_path}")
        except (IOError, yaml.YAMLError, json.JSONDecodeError) as e:
            error_msg = f"Error loading configuration from {config_path}: {e}"
            module_logger.error(error_msg, exc_info=True)
            return None
        except ModuleNotFoundError:
            yaml_error = "PyYAML is required to load .yaml config files. Please install it."
            module_logger.error(yaml_error)
            return None
        except Exception as e:  # Catch other unexpected errors
            error_msg = f"Unexpected error loading config {config_path}: {e}"
            module_logger.error(error_msg, exc_info=True)
            return None

        # Extract CRONOS specific config if nested
        # Use top-level config if not nested under CRONOS key
        cronos_config = config.get("CRONOS", config)

        # --- Get Mycelium Interface ---
        # Assume the network instance provides a way to get the interface
        mycelium_interface = mycelium_network_instance.get_interface()
        if not mycelium_interface:
            module_logger.critical("Failed to get Mycelium interface from network instance.")
            return None

        # --- Instantiate Service ---
        service = CronosService(cronos_config, mycelium_interface, project_root)
        module_logger.info("CRONOS service instance created.")
        return service

    except Exception as e:
        module_logger.critical(f"CRITICAL ERROR during CRONOS initialization: {e}", exc_info=True)
        return None

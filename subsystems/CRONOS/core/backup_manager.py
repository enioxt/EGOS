#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Manages the creation, loading, and cleanup of system backups for CRONOS."""

import asyncio
from dataclasses import asdict
import datetime
from datetime import timedelta
import fnmatch
import json
import logging
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional, Tuple
import zipfile

from koios.logger import KoiosLogger
from mycelium import Message, MyceliumClient

# Import dataclasses from service or a shared location
# Assuming they might be moved to a shared location or stay in service for now
from ..services.service import SystemBackupInfo


class BackupManager:
    """Handles backup creation, retention policy application, and history."""

    def __init__(
        self,
        project_root: Path,
        config_path: Optional[Path] = None,
        mycelium_client: Optional[MyceliumClient] = None,
    ):
        """Initialize BackupManager with configuration.

        Args:
            project_root (Path): Root directory of the project
            config_path (Optional[Path]): Path to configuration file. If None, uses default config.
            mycelium_client (Optional[MyceliumClient]): Mycelium client for pub/sub.
                                                       If None, messaging is disabled.
        """
        self.project_root = Path(project_root)
        self.logger = KoiosLogger.get_logger("CRONOS.BackupManager")
        self.mycelium = mycelium_client

        # Load configuration
        self.config = self._load_config(config_path)

        # Initialize paths
        self.backup_dir = Path(self.config["backup"]["directory"])
        if not self.backup_dir.is_absolute():
            self.backup_dir = self.project_root / self.backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Initialize performance settings
        self.buffer_size = self.config["performance"]["buffer_size_mb"] * 1024 * 1024
        self.max_concurrent = self.config["performance"]["max_concurrent_operations"]

        # Initialize Mycelium topics if client provided
        if self.mycelium:
            self.topics = self.config["mycelium"]["topics"]
            self._setup_mycelium_handlers()

        self.logger.info(
            f"BackupManager initialized with root: {project_root}, backup dir: {self.backup_dir}"
        )

        self.system_root = Path(self.config.get("system_root", ".")).resolve()
        self.backups: Dict[str, SystemBackupInfo] = {}

        self._load_version_history()  # Load history on init

    def _setup_mycelium_handlers(self):
        """Setup Mycelium message handlers."""
        if not self.mycelium:
            return

        @self.mycelium.subscribe(self.topics["backup_request"])
        async def handle_backup_request(message: Message):
            """Handle backup requests from Mycelium."""
            try:
                data = message.data
                backup_path = await self.create_backup(
                    name=data["name"],
                    backup_type=data.get("type", "manual"),
                    include_patterns=data.get("include_patterns"),
                    exclude_patterns=data.get("exclude_patterns"),
                    metadata=data.get("metadata"),
                )

                if backup_path:
                    await self.mycelium.publish(
                        self.topics["backup_status"],
                        {
                            "status": "success",
                            "backup_path": str(backup_path),
                            "request_id": message.id,
                        },
                    )
                else:
                    await self.mycelium.publish(
                        self.topics["backup_status"],
                        {
                            "status": "error",
                            "error": "Backup creation failed",
                            "request_id": message.id,
                        },
                    )
            except Exception as e:
                self.logger.error(f"Error handling backup request: {e}", exc_info=True)
                await self.mycelium.publish(
                    self.topics["backup_status"],
                    {"status": "error", "error": str(e), "request_id": message.id},
                )

        @self.mycelium.subscribe(self.topics["restore_request"])
        async def handle_restore_request(message: Message):
            """Handle restore requests from Mycelium."""
            try:
                data = message.data
                success, result_msg = await self.restore_backup(
                    backup_identifier=data["backup_identifier"],
                    restore_target_path=data.get("target_path"),
                    strategy=data.get("strategy", "new_location"),
                )

                await self.mycelium.publish(
                    self.topics["restore_status"],
                    {
                        "status": "success" if success else "error",
                        "message": result_msg,
                        "request_id": message.id,
                    },
                )
            except Exception as e:
                self.logger.error(f"Error handling restore request: {e}", exc_info=True)
                await self.mycelium.publish(
                    self.topics["restore_status"],
                    {"status": "error", "error": str(e), "request_id": message.id},
                )

    async def _publish_alert(
        self, level: str, message: str, details: Optional[Dict[str, Any]] = None
    ):
        """Publish an alert through Mycelium."""
        if not self.mycelium:
            return

        try:
            await self.mycelium.publish(
                self.topics["alert"],
                {
                    "level": level,
                    "message": message,
                    "details": details or {},
                    "timestamp": datetime.datetime.now().isoformat(),
                },
            )
        except Exception as e:
            self.logger.error(f"Failed to publish alert: {e}")

    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "backup": {
                "directory": "./backups",
                "retention_days": 30,
                "max_backups": 100,
                "compression_level": 9,
                "auto_backup": {"enabled": True, "interval_hours": 24, "min_changes": 10},
            },
            "restore": {
                "default_strategy": "merge",
                "verify_integrity": True,
                "create_restore_point": True,
                "max_retries": 3,
                "timeout_seconds": 300,
            },
            "performance": {
                "max_concurrent_operations": 5,
                "buffer_size_mb": 64,
                "temp_dir": "./temp",
            },
        }

        if config_path:
            try:
                with open(config_path) as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    self._deep_merge(default_config, loaded_config)
            except Exception as e:
                self.logger.error(f"Error loading config from {config_path}: {e}. Using defaults.")

        return default_config

    def _deep_merge(self, base: Dict, update: Dict) -> None:
        """Recursively merge update dict into base dict."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    async def create_backup(
        self,
        name: str,
        backup_type: str = "manual",
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Path]:
        """Create a new backup with enhanced configuration support and Mycelium integration."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"egos_backup_{backup_type}_{name.lower().replace(' ', '_')}_{timestamp}.zip"
        backup_path = self.backup_dir / backup_name

        # Use config values if patterns not provided
        if include_patterns is None:
            include_patterns = ["**/*"]
        if exclude_patterns is None:
            exclude_patterns = [
                ".venv/*",
                "__pycache__/*",
                "*.pyc",
                ".git/*",
                "node_modules/*",
                "backups/*",
                "logs/*",
                "data/*",
            ]

        self.logger.info(f"Starting {backup_type} backup '{name}' to {backup_path}")

        try:
            with zipfile.ZipFile(
                backup_path,
                "w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=self.config["backup"]["compression_level"],
            ) as zipf:
                # Add metadata if provided
                if metadata:
                    metadata.update(
                        {"created_at": timestamp, "backup_type": backup_type, "name": name}
                    )
                    zipf.writestr("backup_metadata.json", json.dumps(metadata, indent=2))

                files_added = 0
                for item_path in self.project_root.rglob("*"):
                    try:
                        relative_path = item_path.relative_to(self.project_root)
                        if self._should_exclude(relative_path, exclude_patterns):
                            continue

                        if item_path.is_file() and self._should_include(
                            relative_path, include_patterns
                        ):
                            zipf.write(item_path, arcname=str(relative_path))
                            files_added += 1

                            if files_added % 100 == 0:
                                self.logger.debug(f"Added {files_added} files to backup...")
                                await self._publish_alert(
                                    "info",
                                    f"Backup progress: {files_added} files added",
                                    {"backup_name": name, "files_processed": files_added},
                                )

                    except Exception as item_e:
                        self.logger.warning(f"Error processing {item_path}: {item_e}")
                        await self._publish_alert(
                            "warning",
                            "Error processing file during backup",
                            {"file": str(item_path), "error": str(item_e)},
                        )
                        continue

                self.logger.info(f"Backup completed successfully. Added {files_added} files.")
                await self._publish_alert(
                    "success",
                    "Backup completed successfully",
                    {
                        "backup_name": name,
                        "files_added": files_added,
                        "backup_path": str(backup_path),
                    },
                )

                # Clean old backups if needed
                await self.clean_old_backups()
                return backup_path

        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}", exc_info=True)
            await self._publish_alert(
                "error", "Backup creation failed", {"error": str(e), "backup_name": name}
            )
            if backup_path.exists():
                try:
                    backup_path.unlink()
                except Exception as del_e:
                    self.logger.error(f"Failed to cleanup failed backup {backup_path}: {del_e}")
            return None

    def _should_exclude(self, path: Path, patterns: List[str]) -> bool:
        """Check if path should be excluded based on patterns."""
        path_str = str(path.as_posix())
        return any(fnmatch.fnmatch(path_str, pattern) for pattern in patterns)

    def _should_include(self, path: Path, patterns: List[str]) -> bool:
        """Check if path should be included based on patterns."""
        path_str = str(path.as_posix())
        return any(fnmatch.fnmatch(path_str, pattern) for pattern in patterns)

    def _get_backup_config(self) -> Dict[str, Any]:
        """Helper to get the specific backup configuration."""
        # Assuming backup config is nested, e.g., config['backup_settings']
        return self.config.get("backup_settings", self.config)  # Fallback to main config

    def should_exclude(self, path):
        """Check if a path should be excluded based on config rules"""
        path_obj = Path(path)

        # Check if any parent directory should be excluded
        for part in path_obj.parts:
            if part in self.config["excluded_directories"]:
                return True

        # Check file extension
        if path_obj.is_file() and path_obj.suffix in self.config["excluded_extensions"]:
            return True

        return False

    def _find_backup_path(self, backup_identifier: str) -> Optional[Path]:
        """Finds the full path to a backup zip file based on an identifier.

        The identifier can be a full filename or a timestamp (YYYYMMDD_HHMMSS).
        Returns the latest match if multiple backups match a timestamp prefix.
        """
        latest_match = None
        latest_timestamp = None

        for item in self.backup_dir.iterdir():
            if item.is_file() and item.name.endswith(".zip"):
                if item.name == backup_identifier:
                    self.logger.info(f"Found exact backup match: {item.name}")
                    return item  # Exact filename match

                # Check for timestamp match in standard backup name format
                # egos_backup_<type>_<name>_<timestamp>.zip
                try:
                    base_name = item.stem  # filename without .zip
                    timestamp_str = base_name.split("_")[-1]  # Get last part
                    if timestamp_str == backup_identifier or base_name.endswith(backup_identifier):
                        # Allow matching by timestamp or full stem identifier
                        current_timestamp = datetime.datetime.strptime(
                            timestamp_str, "%Y%m%d_%H%M%S"
                        )
                        if latest_timestamp is None or current_timestamp > latest_timestamp:
                            latest_timestamp = current_timestamp
                            latest_match = item
                except (ValueError, IndexError):
                    continue  # Ignore files not matching the expected name format or timestamp

        if latest_match:
            self.logger.info(
                f"Found latest backup matching identifier '{backup_identifier}': "
                f"{latest_match.name}"
            )
            return latest_match
        else:
            self.logger.error(
                f"No backup found matching identifier: '{backup_identifier}' in {self.backup_dir}"
            )
            return None

    async def restore_backup(
        self,
        backup_identifier: str,
        restore_target_path: Optional[str] = None,
        strategy: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Restores a project state from a specified backup archive.

        Args:
            backup_identifier (str): The filename or a unique part
                                     (like timestamp YYYYMMDD_HHMMSS)
                                     of the backup zip file.
            restore_target_path (Optional[str]): The directory where the backup
                                                 should be restored. Required for
                                                 'overwrite' strategy. If None for
                                                 'new_location', a new timestamped
                                                 directory is created relative to
                                                 the project root.
            strategy (str): The restore strategy ('new_location', 'overwrite').
                            Defaults to config or 'new_location'.

        Returns:
            Tuple[bool, str]: (Success status, Message)
        """

        # Determine strategy and log start
        resolved_strategy = strategy or self.config.get("restore", {}).get(
            "default_strategy", "new_location"
        )
        self.logger.info(
            f"Initiating restore: Identifier='{backup_identifier}', "
            f"Strategy='{resolved_strategy}', "
            f"Target='{restore_target_path or 'Default New Location'}'"
        )

        # --- 1. Find the Backup File ---
        backup_path = self._find_backup_path(backup_identifier)
        if not backup_path:
            err_msg = f"Backup '{backup_identifier}' not found."
            await self._publish_alert(
                "error", err_msg, {"backup_id": backup_identifier}
            )  # Publish error
            return False, err_msg

        # --- 2. Determine and Prepare Target Path ---
        target_path: Path
        try:
            if resolved_strategy == "new_location":
                if restore_target_path:
                    target_path = Path(restore_target_path).resolve()
                    if target_path.exists() and any(target_path.iterdir()):
                        err_msg = (
                            f"Target path '{target_path}' for 'new_location' strategy "
                            f"must not exist or be empty."
                        )
                        self.logger.error(err_msg)
                        await self._publish_alert(
                            "error",
                            err_msg,
                            {"backup_id": backup_identifier, "target": str(target_path)},
                        )  # Publish error
                        return False, err_msg
                else:
                    # Default: Create backups/restores/restore_<timestamp>
                    restore_base = self.backup_dir / "restores"
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    target_path = restore_base / f"restore_{backup_path.stem}_{timestamp}"
                    self.logger.info(
                        f"No target path provided for 'new_location', using default: {target_path}"
                    )

                target_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Restore target (new location): {target_path}")

            elif resolved_strategy == "overwrite":
                # Overwrite strategy restores to the project root
                target_path = self.project_root
                self.logger.warning(
                    f"Restore target (overwrite): {target_path}. Existing files may be overwritten!"
                )

                # Create pre-restore backup (restore point) if configured
                if self.config.get("restore", {}).get("create_restore_point", False):
                    self.logger.info("Creating pre-restore backup (restore point)...")
                    restore_point_name = f"restore_point_before_{backup_path.stem}"
                    # Exclude backups dir itself from the restore point
                    exclude_patterns_rp = self.config.get("backup", {}).get("exclude_patterns") + [
                        self.backup_dir.name + "/*"
                    ]
                    rp_backup_path = await self.create_backup(
                        name=restore_point_name,
                        backup_type="restore_point",
                        exclude_patterns=list(set(exclude_patterns_rp)),  # Ensure unique excludes
                    )
                    if not rp_backup_path:
                        err_msg = "Failed to create pre-restore backup. Aborting restore."
                        self.logger.error(err_msg)
                        await self._publish_alert(
                            "error", err_msg, {"backup_id": backup_identifier}
                        )  # Publish error
                        return False, err_msg
                    self.logger.info(f"Restore point created: {rp_backup_path.name}")
            else:
                err_msg = (
                    f"Unsupported restore strategy: '{resolved_strategy}'. "
                    f"Use 'new_location' or 'overwrite'."
                )
                self.logger.error(err_msg)
                await self._publish_alert(
                    "error", err_msg, {"backup_id": backup_identifier}
                )  # Publish error
                return False, err_msg
        except Exception as path_e:
            err_msg = f"Error preparing restore target path: {path_e}"
            self.logger.error(err_msg, exc_info=True)
            await self._publish_alert(
                "error", err_msg, {"backup_id": backup_identifier}
            )  # Publish error
            return False, err_msg

        # --- 3. Extract Backup ---
        self.logger.info(f"Starting extraction from '{backup_path.name}' to '{target_path}'...")
        extracted_count = 0
        try:
            with zipfile.ZipFile(backup_path, "r") as zipf:
                # Verify integrity if configured
                if self.config.get("restore", {}).get("verify_integrity", False):
                    self.logger.info("Verifying backup integrity...")
                    test_result = zipf.testzip()
                    if test_result is not None:
                        err_msg = f"Backup integrity check failed for file: {test_result}"
                        self.logger.error(err_msg)
                        await self._publish_alert(
                            "error", err_msg, {"backup_id": backup_identifier}
                        )  # Publish error
                        return False, err_msg
                    self.logger.info("Backup integrity verified.")

                # Extract all members
                member_list = zipf.namelist()
                total_files = len(member_list)
                self.logger.info(
                    f"Found {total_files} items in backup (including potential metadata file)."
                )

                for member in member_list:
                    # Skip metadata file extraction
                    if member == "backup_metadata.json":
                        self.logger.debug("Skipping metadata file extraction.")
                        continue

                    zipf.extract(member, path=target_path)
                    extracted_count += 1
                    # Add progress logging/alerting if desired
                    if extracted_count % 100 == 0:
                        self.logger.debug(f"Extracted {extracted_count}/{total_files} items...")

            msg = (
                f"Successfully restored backup '{backup_identifier}' to '{target_path}'. "
                f"Extracted {extracted_count} items."
            )
            self.logger.info(msg)
            await self._publish_alert(
                "info", msg, {"backup_id": backup_identifier, "target": str(target_path)}
            )  # Publish success alert
            return True, msg

        except zipfile.BadZipFile:
            err_msg = (
                f"Error: Backup file '{backup_path.name}' is corrupted or not a valid zip file."
            )
            self.logger.error(err_msg)
            await self._publish_alert(
                "error", err_msg, {"backup_id": backup_identifier}
            )  # Publish error alert
            return False, err_msg
        except Exception as extract_e:
            err_msg = f"An unexpected error occurred during restore extraction: {extract_e}"
            self.logger.error(err_msg, exc_info=True)
            await self._publish_alert(
                "error", err_msg, {"backup_id": backup_identifier}
            )  # Publish error alert
            return False, err_msg

    # --- Helper Methods --- #
    def _matches_any(self, path: Path, patterns: List[str]) -> bool:
        """Check if the path matches any of the glob patterns."""
        # Convert path to string for matching
        path_str = str(path.as_posix())  # Use POSIX paths for glob matching consistency
        for pattern in patterns:
            if path.match(pattern):
                return True
            # Also check string match for patterns like dir/*
            if fnmatch.fnmatch(path_str, pattern):
                return True
        return False

    async def clean_old_backups(self):
        """Cleans up old backups based on the configured retention policy."""
        retention_config = self.config.get("retention", {})
        enabled = retention_config.get("enabled", False)
        retention_days = retention_config.get("days", {"daily": 7, "weekly": 4, "monthly": 3})

        if not enabled:
            self.logger.info("Backup retention policy is disabled. Skipping cleanup.")
            return

        self.logger.info("Starting backup cleanup process...")

        # Ensure history is loaded
        self._load_version_history()

        if not self.backups:
            self.logger.info("No backups found in history. Nothing to clean.")
            return

        now = datetime.datetime.now()
        sorted_backups = sorted(self.backups.values(), key=lambda b: b.timestamp)

        kept_backups = self._apply_retention_policy(sorted_backups, retention_days, now)

        # Identify backups to delete
        backups_to_delete = {b.id: b for b in sorted_backups if b.id not in kept_backups}

        if not backups_to_delete:
            self.logger.info("No backups identified for deletion based on retention policy.")
            return

        self.logger.info(f"Identified {len(backups_to_delete)} backups for deletion.")

        deleted_count = 0
        failed_count = 0
        original_backup_dict = self.backups.copy()  # Work on copy

        for backup_id, backup_info in backups_to_delete.items():
            self.logger.debug(
                f"Attempting to delete backup: {backup_id} ({backup_info.name}) "
                f"at {backup_info.location}"
            )
            try:
                if backup_info.location.exists():
                    if backup_info.location.is_dir():
                        shutil.rmtree(backup_info.location)
                        self.logger.info(f"Deleted backup directory: {backup_info.location}")
                    else:
                        # Handle case where location might be a file (unexpected?)
                        backup_info.location.unlink()
                        self.logger.warning(
                            f"Deleted backup file (expected directory): {backup_info.location}"
                        )
                    deleted_count += 1
                    # Remove from our working copy of the history
                    del original_backup_dict[backup_id]
                else:
                    warn_msg = (
                        f"Backup location not found for deletion: "
                        f"{backup_info.location}. Removing from history."
                    )
                    self.logger.warning(warn_msg)
                    # Remove from history even if location not found
                    del original_backup_dict[backup_id]
            except (OSError, PermissionError, shutil.Error) as e:
                error_msg = f"Failed to delete backup {backup_id} at {backup_info.location}: {e}"
                self.logger.error(error_msg)
                failed_count += 1
            except Exception as e:  # Catch unexpected errors during deletion
                self.logger.exception(f"Unexpected error deleting backup {backup_id}: {e}")
                failed_count += 1

        # Update the main backup history with the modified one
        self.backups = original_backup_dict

        self._save_version_history()

        completion_msg = (
            f"Backup cleanup finished. Deleted: {deleted_count}, Failed: {failed_count}. "
            f"Remaining: {len(self.backups)}"
        )
        self.logger.info(completion_msg)

    def _apply_retention_policy(
        self, sorted_backups: List[SystemBackupInfo], retention_days: Dict[str, int], now: datetime
    ) -> Dict[str, SystemBackupInfo]:
        """Applies the retention policy to a sorted list of backups.

        Returns a dictionary of backup IDs that should be kept.
        """
        kept_backups: Dict[str, SystemBackupInfo] = {}

        # Keep N daily backups
        daily_limit = retention_days.get("daily", 7)
        daily_cutoff = now.date() - timedelta(days=daily_limit)
        daily_kept_dates = set()
        for backup in reversed(sorted_backups):
            backup_date = backup.timestamp.date()
            if backup_date >= daily_cutoff and backup_date not in daily_kept_dates:
                if len(daily_kept_dates) < daily_limit:
                    kept_backups[backup.id] = backup
                    daily_kept_dates.add(backup_date)
            # Stop checking dailies once we have enough or go past the cutoff conceptually
            # Though the date check handles the cutoff
            if len(daily_kept_dates) >= daily_limit:
                break
        self.logger.debug(f"Kept {len(daily_kept_dates)} daily backups.")

        # Keep N weekly backups (keep the first backup of each week)
        weekly_limit = retention_days.get("weekly", 4)
        weekly_cutoff = now.date() - timedelta(weeks=weekly_limit)
        weekly_kept_weeks = set()  # Store (year, week_number)
        for backup in reversed(sorted_backups):
            backup_date = backup.timestamp.date()
            year, week_num, _ = backup_date.isocalendar()
            week_id = (year, week_num)
            # Only consider backups older than the daily cutoff for weekly retention
            if backup_date < daily_cutoff and backup_date >= weekly_cutoff:
                if week_id not in weekly_kept_weeks:
                    if len(weekly_kept_weeks) < weekly_limit:
                        kept_backups[backup.id] = backup  # Keep this one (first of the week)
                        weekly_kept_weeks.add(week_id)
            if len(weekly_kept_weeks) >= weekly_limit:
                break
        self.logger.debug(f"Kept {len(weekly_kept_weeks)} additional weekly backups.")

        # Keep N monthly backups (keep the first backup of each month)
        monthly_limit = retention_days.get("monthly", 3)
        monthly_cutoff = now.date() - timedelta(days=monthly_limit * 30)  # Approximate
        monthly_kept_months = set()  # Store (year, month)
        for backup in reversed(sorted_backups):
            backup_date = backup.timestamp.date()
            month_id = (backup_date.year, backup_date.month)
            # Only consider backups older than the weekly cutoff for monthly retention
            if backup_date < weekly_cutoff and backup_date >= monthly_cutoff:
                if month_id not in monthly_kept_months:
                    if len(monthly_kept_months) < monthly_limit:
                        kept_backups[backup.id] = backup
                        monthly_kept_months.add(month_id)
            if len(monthly_kept_months) >= monthly_limit:
                break
        self.logger.debug(f"Kept {len(monthly_kept_months)} additional monthly backups.")

        # Always keep the absolute latest backup if not already included
        if sorted_backups and sorted_backups[-1].id not in kept_backups:
            latest_backup = sorted_backups[-1]
            self.logger.debug(f"Ensuring the latest backup {latest_backup.id} is kept.")
            kept_backups[latest_backup.id] = latest_backup

        return kept_backups

    def _calculate_directory_size(self, path: Path) -> int:
        """Calculates the total size of a directory."""
        total_size = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
        except (OSError, FileNotFoundError) as e:
            self.logger.error(f"Error calculating size for {path}: {e}")
        return total_size

    def _prepare_for_json(self, data: Dict) -> Dict:
        """Converts Path objects and datetimes to strings for JSON serialization."""
        prepared_data = {}
        for key, value in data.items():
            if isinstance(value, Path):
                prepared_data[key] = str(value.resolve())  # Store absolute path string
            elif isinstance(value, datetime):
                prepared_data[key] = value.isoformat()
            elif isinstance(value, dict):
                prepared_data[key] = self._prepare_for_json(value)  # Recurse
            elif isinstance(value, list):
                # Ensure nested items are also prepared
                prepared_data[key] = [
                    self._prepare_for_json(item)
                    if isinstance(item, (dict, SystemBackupInfo))
                    else item
                    for item in value
                ]
            else:
                prepared_data[key] = value
        return prepared_data

    def get_backup_info(self, backup_id: str) -> Optional[SystemBackupInfo]:
        """Retrieves information about a specific backup from history."""
        return self.backups.get(backup_id)

    def list_backups(self) -> List[Dict]:
        """Lists all backups currently in the history."""
        # Return serializable list
        return [self._prepare_for_json(asdict(b)) for b in self.backups.values()]

    def _load_version_history(self):
        """Loads the backup version history from the JSON file."""
        if self.version_history_file.exists():
            try:
                with open(self.version_history_file, "r") as f:
                    history_data = json.load(f)
                self.backups = {}
                for backup_id, data in history_data.items():
                    try:
                        # Convert relevant fields back from JSON representation
                        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                        data["location"] = Path(data["location"])  # Convert back to Path
                        self.backups[backup_id] = SystemBackupInfo(**data)
                    except (TypeError, KeyError, ValueError) as e:
                        error_msg = f"Error parsing backup entry '{backup_id}' from history: {e}"
                        self.logger.error(error_msg, exc_info=True)
                self.logger.info(f"Loaded {len(self.backups)} backups from history file.")
            except (IOError, json.JSONDecodeError) as e:
                error_msg = f"Error loading version history from {self.version_history_file}: {e}"
                self.logger.error(error_msg, exc_info=True)
                self.backups = {}  # Reset on load error
        else:
            self.logger.info("Version history file not found. Starting fresh.")
            self.backups = {}

    def _save_version_history(self):
        """Saves the current backup version history to the JSON file."""
        try:
            # Convert data to JSON serializable format before saving
            serializable_history = {
                bid: self._prepare_for_json(asdict(binfo)) for bid, binfo in self.backups.items()
            }
            self.version_history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.version_history_file, "w") as f:
                json.dump(serializable_history, f, indent=4)
            self.logger.info(f"Saved {len(self.backups)} backups to history file.")
        except (IOError, TypeError) as e:
            error_msg = f"Error saving version history to {self.version_history_file}: {e}"
            self.logger.error(error_msg, exc_info=True)

    def _add_history_entry(self, backup_info: SystemBackupInfo):
        """Adds a new entry to the version history (in memory)."""
        self.backups[backup_info.id] = backup_info
        # Saving happens separately or on shutdown


if __name__ == "__main__":
    # Example usage needs updating for async and proper initialization
    # This block is likely outdated
    async def run_example():
        try:
            # Proper initialization example (assuming project root can be found)
            project_root = Path(__file__).parent.parent.parent.resolve()

            # Mock Mycelium for example run
            class MockMycelium:
                async def publish(self, *args, **kwargs):
                    pass

                def subscribe(self, *args, **kwargs):
                    return lambda func: func

            # Get a logger instance for the example run
            example_logger = KoiosLogger.get_logger("CRONOS.BackupManager.Example")

            manager = BackupManager(project_root=project_root, mycelium_client=MockMycelium())
            # Explicitly set the manager's logger for the example if needed,
            # though its __init__ handles it.
            # manager.logger = example_logger

            print("Listing existing backups:")
            existing = manager.list_backups()
            for b in existing:
                print(f"- {b['filename']} ({b['size_bytes']} bytes, {b['created_at']})\n")

            print("Creating a new test backup...")
            backup_path = await manager.create_backup(name="main_test", backup_type="manual")
            if backup_path:
                print(f"✅ Backup completed successfully: {backup_path}")
                print("Listing backups again:")
                updated_list = manager.list_backups()
                for b in updated_list:
                    print(f"- {b['filename']} ({b['size_bytes']} bytes, {b['created_at']})\n")

                # Example Restore (to new location by default)
                print("\nAttempting restore to new location...")
                success, msg = await manager.restore_backup(
                    backup_identifier=backup_path.stem
                )  # Use stem as identifier
                print(f"Restore Result: {success} - {msg}")

            else:
                print("❌ Backup creation failed.")

            print("\nCleaning old backups...")
            await manager.clean_old_backups()
            print("✅ Old backup cleanup completed according to retention policy.")
        except Exception as e:
            # Use the example logger if available, otherwise a default logger might be needed
            try:
                example_logger.error(f"Example run failed: {e}", exc_info=True)
            except NameError:  # If example_logger wasn't defined due to earlier error
                logging.error(f"Example run failed critically: {e}", exc_info=True)
            print(f"❌ Example run failed: {e}")

    asyncio.run(run_example())

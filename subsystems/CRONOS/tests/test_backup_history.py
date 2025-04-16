import pytest
from pathlib import Path
import time
import asyncio
import json
from unittest.mock import patch, mock_open

from ..core.backup_manager import BackupManager, SystemBackupInfo
from datetime import datetime, timezone, timedelta

# Uses fixtures from conftest.py

@pytest.mark.asyncio
async def test_load_version_history_file_not_found(backup_manager_fixture: BackupManager, mock_logger):
    """Test loading history when the file doesn't exist."""
    manager = backup_manager_fixture
    manager.version_history_file = manager.backup_dir / "nonexistent_history.json"
    assert not manager.version_history_file.exists()

    manager._load_version_history()

    assert manager.backups == {}
    assert manager.states == {}
    mock_logger.warning.assert_called_with(f"Version history file not found: {manager.version_history_file}")
    # Check if save was called to create an empty file
    mock_logger.info.assert_any_call(f"Version history saved to {manager.version_history_file}")

@pytest.mark.asyncio
async def test_load_version_history_invalid_json(backup_manager_fixture: BackupManager, mock_logger):
    """Test loading history from a file with invalid JSON."""
    manager = backup_manager_fixture
    manager.version_history_file.write_text("this is not json")

    manager._load_version_history()

    assert manager.backups == {}
    assert manager.states == {}
    mock_logger.error.assert_called_with(
        f"Failed to load rules from {manager.version_history_file}: Expecting value: line 1 column 1 (char 0)",
        exc_info=True
    )

@pytest.mark.asyncio
async def test_load_version_history_valid_data(backup_manager_fixture: BackupManager):
    """Test loading valid backup and state entries from history."""
    manager = backup_manager_fixture
    ts1 = datetime.now(timezone.utc)
    ts2 = ts1 - timedelta(days=1)
    valid_history_data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "backups": [
            {
                "id": "backup_id_1", "name": "backup1", "timestamp": ts1.isoformat(),
                "backup_type": "manual", "state_id": "state_1",
                "location": "backup_id_1", # Store only ID
                "size_bytes": 1024, "file_count": 10, "metadata": {}
            },
             {
                "id": "backup_id_2", "name": "backup2", "timestamp": ts2.isoformat(),
                "backup_type": "auto", "state_id": None,
                "location": "backup_id_2",
                "size_bytes": 512, "file_count": 5, "metadata": {"reason": "auto"}
            }
        ],
        "states": [
             {
                "id": "state_1", "name": "state1", "timestamp": ts1.isoformat(),
                "related_backup_id": "backup_id_1", "git_commit_hash": "abc",
                "config_hashes": {}, "subsystem_versions": {}, "data": {}, "metrics": {},
                 "metadata": {}
             }
        ]
    }
    manager.version_history_file.write_text(json.dumps(valid_history_data))

    # Mock Path.exists to return True for the backup locations during load
    with patch.object(Path, 'exists', return_value=True):
        with patch.object(Path, 'is_dir', return_value=True): # Assume they are dirs
             manager._load_version_history()

    assert len(manager.backups) == 2
    assert len(manager.states) == 1
    assert "backup_id_1" in manager.backups
    assert "state_1" in manager.states
    assert manager.backups["backup_id_1"].timestamp == ts1
    assert manager.backups["backup_id_1"].location == manager.backup_dir / "backup_id_1"
    assert manager.states["state_1"].related_backup_id == "backup_id_1"

@pytest.mark.asyncio
async def test_load_version_history_missing_backup_dir(backup_manager_fixture: BackupManager, mock_logger):
    """Test loading history when a backup dir listed in history is missing."""
    manager = backup_manager_fixture
    ts1 = datetime.now(timezone.utc)
    valid_history_data = {
        "backups": [
            {
                "id": "backup_id_missing", "name": "backup_missing", "timestamp": ts1.isoformat(),
                "backup_type": "manual", "state_id": None,
                "location": "backup_id_missing",
                "size_bytes": 100, "file_count": 1, "metadata": {}
            }
        ],
        "states": []
    }
    manager.version_history_file.write_text(json.dumps(valid_history_data))

    # Ensure the directory does NOT exist
    missing_path = manager.backup_dir / "backup_id_missing"
    if missing_path.exists(): missing_path.rmdir() # Ensure it's gone

    manager._load_version_history()

    assert len(manager.backups) == 0 # Backup should be ignored
    mock_logger.warning.assert_called_with(
        f"Backup directory missing for history entry backup_id_missing. Ignoring."
    )

@pytest.mark.asyncio
async def test_save_version_history(backup_manager_fixture: BackupManager):
    """Test saving the current history to the file."""
    manager = backup_manager_fixture
    ts = datetime.now(timezone.utc)
    backup_info = SystemBackupInfo(
        id="test_save_id", name="test_save", timestamp=ts,
        location=manager.backup_dir / "test_save_id",
        size_bytes=123, file_count=1
    )
    manager._add_history_entry(backup_info)

    manager._save_version_history()

    assert manager.version_history_file.exists()
    with open(manager.version_history_file, "r") as f:
        saved_data = json.load(f)

    assert "last_updated" in saved_data
    assert len(saved_data["backups"]) == 1
    assert saved_data["backups"][0]["id"] == "test_save_id"
    assert saved_data["backups"][0]["name"] == "test_save"
    assert saved_data["backups"][0]["timestamp"] == ts.isoformat()
    assert saved_data["backups"][0]["location"] == "test_save_id" # Check only ID is saved

# TODO: Add tests for _add_history_entry if it becomes more complex

@pytest.mark.asyncio
async def test_remove_history_entry(backup_manager_fixture: BackupManager):
    """Test removing a backup and its associated state from history."""
    manager = backup_manager_fixture
    ts = datetime.now(timezone.utc)

    # Add a state entry first
    state_info = SystemStateInfo(
        id="state_remove_test", name="state_to_remove", timestamp=ts,
        related_backup_id="backup_remove_test"
    )
    manager._add_history_entry(state_info)
    assert "state_remove_test" in manager.states

    # Add a backup entry linked to the state
    backup_info = SystemBackupInfo(
        id="backup_remove_test", name="backup_to_remove", timestamp=ts,
        location=manager.backup_dir / "backup_remove_test",
        state_id="state_remove_test", # Link to the state
        size_bytes=123, file_count=1
    )
    manager._add_history_entry(backup_info)
    assert "backup_remove_test" in manager.backups
    assert manager.states["state_remove_test"].related_backup_id == "backup_remove_test" # Check link

    # --- Act ---
    manager._remove_history_entry("backup_remove_test")

    # --- Assert ---
    assert "backup_remove_test" not in manager.backups
    # Crucially, check that the associated state was also removed
    assert "state_remove_test" not in manager.states

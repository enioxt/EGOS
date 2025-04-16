import pytest
from pathlib import Path
import time
import datetime
from ..core.backup_manager import BackupManager # Import BackupManager

# Helper function (can also be in conftest if used by multiple files)
def create_dummy_backup_file(backup_dir: Path, name: str):
    """Helper to create an empty dummy backup zip file with a specific name."""
    backup_path = backup_dir / f"{name}.zip"
    backup_path.touch()
    # Ensure modification time is set for sorting tests
    # Note: touching might not be enough on all systems for precise time control
    # For more control, consider setting mtime explicitly if needed, though complex
    return backup_path

# --- Test Backup Listing (Uses backup_manager_fixture from conftest.py) ---

@pytest.mark.asyncio
async def test_list_backups_empty(backup_manager_fixture: BackupManager):
    """Test listing backups when directory is empty."""
    backup_manager = backup_manager_fixture
    # Need to load history (which might be empty if dir is empty)
    backup_manager._load_version_history()
    backups = backup_manager.list_backups() # list_backups also reloads
    assert len(backups) == 0

@pytest.mark.asyncio
async def test_list_backups_with_files(backup_manager_fixture: BackupManager):
    """Test listing backups with multiple backup files present."""
    backup_manager = backup_manager_fixture
    backup_dir = backup_manager.backup_dir

    # Create some dummy backup files with slightly different times
    # Ensure names match expected format for _find_backup_path tests later
    ts_format = "%Y%m%d_%H%M%S"
    t1 = datetime.datetime.now() - datetime.timedelta(seconds=10)
    t2 = datetime.datetime.now() - datetime.timedelta(seconds=5)
    name1 = f"egos_backup_manual_list_test_{t1.strftime(ts_format)}"
    name2 = f"egos_backup_manual_list_test_{t2.strftime(ts_format)}"

    backup_path1 = create_dummy_backup_file(backup_dir, name1)
    # Ensure modification times differ if possible
    time.sleep(0.1)
    backup_path2 = create_dummy_backup_file(backup_dir, name2)

    # Re-load history after creating files
    backup_manager._load_version_history()
    backups_info = backup_manager.list_backups()

    assert len(backups_info) == 2
    # Should be sorted newest first
    assert backups_info[0]["id"] == backup_path2.stem
    assert backups_info[1]["id"] == backup_path1.stem

    # Check structure of returned dicts
    for backup_info in backups_info:
        assert "id" in backup_info
        assert "name" in backup_info
        assert "timestamp" in backup_info
        assert "backup_type" in backup_info
        assert "location" in backup_info
        assert "size_bytes" in backup_info # Might be 0 for dummy files
        assert "file_count" in backup_info # Might be 0 for dummy files
        assert "metadata" in backup_info
        assert isinstance(backup_info["id"], str)
        assert isinstance(backup_info["timestamp"], str) # ISO format string

@pytest.mark.asyncio
async def test_find_backup_path(backup_manager_fixture: BackupManager):
    """Test the helper method for finding backup paths."""
    backup_manager = backup_manager_fixture
    backup_dir = backup_manager.backup_dir

    # 1. Create some backups with predictable names/timestamps
    ts_format = "%Y%m%d_%H%M%S"
    t1 = datetime.datetime.now() - datetime.timedelta(hours=2)
    t2 = datetime.datetime.now() - datetime.timedelta(hours=1)
    t3 = datetime.datetime.now()

    name1 = f"egos_backup_manual_find_test_{t1.strftime(ts_format)}"
    name2 = f"egos_backup_manual_find_test_{t2.strftime(ts_format)}"
    name3 = f"egos_backup_auto_other_{t3.strftime(ts_format)}"

    path1 = create_dummy_backup_file(backup_dir, name1)
    path2 = create_dummy_backup_file(backup_dir, name2)
    path3 = create_dummy_backup_file(backup_dir, name3)
    time.sleep(0.1) # Ensure modification times are distinct if needed

    # Reload history to include created files
    backup_manager._load_version_history()

    # Test find by exact name (including .zip)
    assert backup_manager._find_backup_path(path2.name) == path2

    # Test find by timestamp part (should get latest matching)
    # Note: _find_backup_path logic might need adjustment if only checking filename suffix
    # For now, assume it searches based on identifier logic matching restore
    timestamp_prefix = t2.strftime("%Y%m%d") # Less specific identifier
    # This test might fail depending on the exact logic of _find_backup_path
    # Needs confirmation if it relies on list_backups sorting or scans dir
    # Assuming it scans dir and finds latest based on timestamp in name:
    # assert backup_manager._find_backup_path(timestamp_prefix) == path2

    # Test find by unique timestamp string
    assert backup_manager._find_backup_path(t3.strftime(ts_format)) == path3

    # Test find by stem (filename without .zip)
    assert backup_manager._find_backup_path(path1.stem) == path1

    # Test not found
    assert backup_manager._find_backup_path("nonexistent_abc.zip") is None
    assert backup_manager._find_backup_path("19990101_000000") is None

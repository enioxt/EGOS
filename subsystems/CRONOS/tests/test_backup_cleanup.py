import pytest
from pathlib import Path
import time
import asyncio

from ..core.backup_manager import BackupManager

# Uses fixtures from conftest.py

@pytest.mark.asyncio
async def test_clean_old_backups_no_action(backup_manager_fixture: BackupManager):
    """Test cleanup when no backups exist or none meet deletion criteria."""
    manager = backup_manager_fixture
    # Ensure history is empty initially (mocked load returns None)
    manager.backups = {}
    manager._save_version_history() # Save empty history

    # Create one recent backup (should be kept)
    await manager.create_backup(name="recent")
    assert len(manager.list_backups()) == 1

    # Call cleanup - assumes policy is applied externally, so it only checks for orphans/missing
    await manager.clean_old_backups()

    # Assert no backups were deleted from history or disk (as none were orphaned/missing)
    assert len(manager.list_backups()) == 1
    assert len(list(manager.backup_dir.glob("*.zip"))) == 1

@pytest.mark.asyncio
async def test_clean_old_backups_orphaned_file(backup_manager_fixture: BackupManager):
    """Test cleanup deletes backup files on disk not present in history."""
    manager = backup_manager_fixture
    # Ensure history is empty
    manager.backups = {}
    manager._save_version_history()

    # Create an orphaned backup file manually on disk
    orphaned_path = manager.backup_dir / "egos_backup_manual_orphan_20240101_000000.zip"
    orphaned_path.touch()
    assert orphaned_path.exists()

    # Call cleanup
    await manager.clean_old_backups()

    # Assert the orphaned file was deleted
    assert not orphaned_path.exists()
    assert len(manager.list_backups()) == 0 # History remains empty

@pytest.mark.asyncio
async def test_clean_old_backups_missing_file(backup_manager_fixture: BackupManager):
    """Test cleanup removes history entries for files missing on disk."""
    manager = backup_manager_fixture

    # Create a backup and add it to history
    backup_path = await manager.create_backup(name="to_be_deleted")
    assert backup_path is not None
    assert len(manager.list_backups()) == 1
    backup_id = backup_path.stem

    # Manually delete the backup file from disk
    backup_path.unlink()
    assert not backup_path.exists()
    assert backup_id in manager.backups # Still in history

    # Call cleanup
    await manager.clean_old_backups()

    # Assert the entry was removed from history
    assert len(manager.list_backups()) == 0
    assert backup_id not in manager.backups

# NOTE: Testing the actual retention policy logic (which backups *should* be kept)
# needs to happen at the CronosService level, as that service is now responsible
# for applying the policy and pruning the self.backups dict BEFORE calling
# BackupManager.clean_old_backups(). These tests verify the BackupManager's
# cleanup correctly handles orphaned files and missing files based on the
# state of self.backups *when it is called*.

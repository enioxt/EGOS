import pytest
from pathlib import Path
import zipfile
import time
import asyncio
from unittest.mock import patch

from ..core.backup_manager import BackupManager

# Uses fixtures defined in conftest.py: test_project_root, backup_manager_fixture

# Helper function (can also be in conftest if used by multiple files)
def create_dummy_zip_file(backup_dir: Path, name: str, files: dict):
    """Helper to create a dummy backup zip file with specified contents."""
    backup_path = backup_dir / f"{name}.zip"
    with zipfile.ZipFile(backup_path, "w") as zf:
        for file_path, content in files.items():
            zf.writestr(file_path, content)
    time.sleep(0.1) # Ensure mtime is slightly different for timestamp checks
    return backup_path

# --- Test Restore Functionality (using backup_manager_fixture) ---

@pytest.mark.asyncio
async def test_restore_new_location_default(backup_manager_fixture: BackupManager, test_project_root):
    """Test restoring to a default new location using the main fixture."""
    backup_manager = backup_manager_fixture
    # 1. Create a backup
    backup_path = await backup_manager.create_backup(name="restore_test_new_default")
    assert backup_path is not None
    backup_id = backup_path.stem # Use stem (filename without .zip) as identifier

    # 2. Restore using default strategy ('new_location') and no target path
    success, msg = await backup_manager.restore_backup(backup_identifier=backup_id)

    # 3. Assertions
    assert success is True
    assert "Successfully restored" in msg

    # Find the created restore directory (should be in backups/restores/restore_...)
    restore_base = backup_manager.backup_dir / "restores"
    restore_dirs = list(restore_base.glob(f"restore_{backup_id}_*"))
    assert len(restore_dirs) == 1
    restore_target = restore_dirs[0]
    assert restore_target.is_dir()

    # Verify restored content
    assert (restore_target / "file1.txt").exists()
    assert (restore_target / "file1.txt").read_text() == "content1"
    assert (restore_target / "subdir" / "file2.py").exists()
    assert not (restore_target / ".venv").exists() # Should not restore excluded dirs

@pytest.mark.asyncio
async def test_restore_new_location_specific(
    backup_manager_fixture: BackupManager, test_project_root, tmp_path
):
    """Test restoring to a specific new location."""
    backup_manager = backup_manager_fixture
    # 1. Create a backup
    backup_path = await backup_manager.create_backup(name="restore_test_new_spec")
    assert backup_path is not None
    backup_id = backup_path.stem

    # 2. Define specific target and restore
    specific_target = tmp_path / "my_restore_location"
    success, msg = await backup_manager.restore_backup(
        backup_identifier=backup_id,
        restore_target_path_str=str(specific_target),
        strategy="new_location",
    )

    # 3. Assertions
    assert success is True
    assert str(specific_target) in msg
    assert specific_target.is_dir()
    assert (specific_target / "file1.txt").exists()
    assert (specific_target / "subdir" / "file2.py").exists()

@pytest.mark.asyncio
async def test_restore_new_location_target_exists_not_empty(
    backup_manager_fixture: BackupManager, test_project_root, tmp_path
):
    """Test failure when target for new_location exists and is not empty."""
    backup_manager = backup_manager_fixture
    # 1. Create a backup
    backup_path = await backup_manager.create_backup(name="restore_fail_exists")
    assert backup_path is not None
    backup_id = backup_path.stem

    # 2. Create existing target with content
    specific_target = tmp_path / "existing_restore"
    specific_target.mkdir()
    (specific_target / "dummy.txt").write_text("pre-existing")

    # 3. Attempt restore
    success, msg = await backup_manager.restore_backup(
        backup_identifier=backup_id,
        restore_target_path_str=str(specific_target),
        strategy="new_location",
    )

    # 4. Assertions
    assert success is False
    assert "must not exist or be empty" in msg
    assert (specific_target / "dummy.txt").exists() # Original file should remain
    assert not (specific_target / "file1.txt").exists() # Backup file should not be there

@pytest.mark.asyncio
async def test_restore_overwrite_with_restore_point(
    backup_manager_fixture: BackupManager, test_project_root
):
    """Test restoring with overwrite strategy, creating a restore point."""
    backup_manager = backup_manager_fixture
    # Ensure restore point creation is enabled in config (it is in fixture)
    assert backup_manager.config["restore"]["create_restore_point"] is True

    # 1. Create initial backup
    backup_path = await backup_manager.create_backup(name="restore_test_overwrite")
    assert backup_path is not None
    backup_id = backup_path.stem

    # 2. Modify a file in the original project root
    original_file = test_project_root / "file1.txt"
    original_content = original_file.read_text()
    modified_content = "modified content before restore"
    original_file.write_text(modified_content)
    assert original_file.read_text() == modified_content

    # 3. Restore using overwrite strategy (target is project_root)
    success, msg = await backup_manager.restore_backup(
        backup_identifier=backup_id,
        # restore_target_path_str is ignored for overwrite, target is project_root
        strategy="overwrite",
    )

    # 4. Assertions
    assert success is True
    assert "Successfully restored" in msg
    assert str(test_project_root) in msg

    # Verify file was overwritten with backup content
    assert original_file.read_text() == original_content
    assert (test_project_root / "subdir" / "file2.py").exists()

    # Verify restore point backup was created
    restore_point_backups = list(backup_manager.backup_dir.glob("egos_backup_restore_point_*.zip"))
    assert len(restore_point_backups) >= 1
    # Optional: Verify content of restore point backup
    rp_backup_path = restore_point_backups[0]
    with zipfile.ZipFile(rp_backup_path, "r") as zipf:
        assert "file1.txt" in zipf.namelist()
        # Check if the content is the modified one
        with zipf.open("file1.txt") as f_rp:
            assert f_rp.read().decode("utf-8") == modified_content

@pytest.mark.asyncio
async def test_restore_overwrite_no_restore_point(backup_manager_fixture: BackupManager, test_project_root):
    """Test restoring with overwrite, restore point disabled."""
    backup_manager = backup_manager_fixture
    # Disable restore point creation for this test
    backup_manager.config["restore"]["create_restore_point"] = False

    # 1. Create backup
    backup_path = await backup_manager.create_backup(name="restore_overwrite_no_rp")
    backup_id = backup_path.stem

    # 2. Modify file
    original_file = test_project_root / "file1.txt"
    original_content = original_file.read_text()
    original_file.write_text("modified again")

    # 3. Restore
    success, msg = await backup_manager.restore_backup(backup_id, strategy="overwrite")

    # 4. Assertions
    assert success is True
    assert original_file.read_text() == original_content # Overwritten
    # Check that NO restore point was created this time
    assert not any(
        p.name.startswith("egos_backup_restore_point_")
        for p in backup_manager.backup_dir.glob("*.zip")
    )

@pytest.mark.asyncio
async def test_restore_invalid_backup_id(backup_manager_fixture: BackupManager):
    """Test restoring with an invalid backup identifier."""
    backup_manager = backup_manager_fixture
    success, msg = await backup_manager.restore_backup("non_existent_backup_123")
    assert success is False
    assert "not found" in msg

@pytest.mark.asyncio
async def test_restore_corrupted_backup(backup_manager_fixture: BackupManager, test_project_root):
    """Test restoring from a corrupted zip file (with integrity check)."""
    backup_manager = backup_manager_fixture
    # Ensure integrity check is enabled
    backup_manager.config["restore"]["verify_integrity"] = True

    # 1. Create a dummy corrupted file
    corrupted_zip_path = backup_manager.backup_dir / "corrupted_backup_test.zip"
    corrupted_zip_path.write_text("this is not a zip file")

    # 2. Attempt restore
    success, msg = await backup_manager.restore_backup(backup_identifier=corrupted_zip_path.stem)

    # 3. Assertions
    assert success is False
    assert "corrupted" in msg or "BadZipFile" in msg or "integrity check failed" in msg

    # Try with integrity check disabled
    backup_manager.config["restore"]["verify_integrity"] = False
    success_no_check, msg_no_check = await backup_manager.restore_backup(
        backup_identifier=corrupted_zip_path.stem
    )
    assert success_no_check is False # Should still fail on extraction
    assert "corrupted" in msg_no_check or "BadZipFile" in msg_no_check

@pytest.mark.asyncio
async def test_restore_unsupported_strategy(backup_manager_fixture: BackupManager):
    """Test using an unsupported restore strategy."""
    backup_manager = backup_manager_fixture
    # 1. Create a backup first so find works
    backup_path = await backup_manager.create_backup(name="strategy_test")
    backup_id = backup_path.stem

    # 2. Attempt restore with bad strategy
    success, msg = await backup_manager.restore_backup(backup_id, strategy="merge_dangerously")

    # 3. Assertions
    assert success is False
    assert "Unsupported restore strategy" in msg

@pytest.mark.asyncio
async def test_restore_with_integrity_check_disabled(
    backup_manager_fixture: BackupManager, test_project_root
):
    """Test restoring with integrity check disabled."""
    backup_manager = backup_manager_fixture
    # Disable integrity check
    backup_manager.config["restore"]["verify_integrity"] = False

    # 1. Create a backup
    backup_path = await backup_manager.create_backup(name="restore_no_verify")
    assert backup_path is not None
    backup_id = backup_path.stem

    # 2. Restore without integrity check
    success, msg = await backup_manager.restore_backup(backup_identifier=backup_id)

    # 3. Assertions
    assert success is True
    assert "Successfully restored" in msg

@pytest.mark.asyncio
async def test_restore_with_timestamp_identifier(backup_manager_fixture: BackupManager, test_project_root):
    """Test restoring using timestamp as identifier."""
    backup_manager = backup_manager_fixture
    # 1. Create a backup
    backup_path = await backup_manager.create_backup(name="timestamp_test")
    assert backup_path is not None

    # Extract timestamp from backup name
    timestamp = backup_path.stem.split("_")[-1]

    # 2. Restore using just the timestamp as identifier
    success, msg = await backup_manager.restore_backup(backup_identifier=timestamp)

    # 3. Assertions
    assert success is True
    assert "Successfully restored" in msg

@pytest.mark.asyncio
async def test_restore_with_partial_identifier(backup_manager_fixture: BackupManager, test_project_root):
    """Test restoring using partial backup name as identifier."""
    backup_manager = backup_manager_fixture
    # 1. Create a backup with a distinctive name
    backup_path = await backup_manager.create_backup(name="unique_partial_test")
    assert backup_path is not None
    backup_id = backup_path.stem # Use stem for identifier

    # 2. Restore using a unique part of the stem
    success, msg = await backup_manager.restore_backup(backup_identifier="unique_partial_test") # Use unique part

    # 3. Assertions
    assert success is True
    assert "Successfully restored" in msg

@pytest.mark.asyncio
async def test_restore_with_multiple_matching_backups(
    backup_manager_fixture: BackupManager, test_project_root
):
    """Test restoring when multiple backups match the identifier (should use latest)."""
    backup_manager = backup_manager_fixture
    # 1. Create multiple backups with similar names/stems
    backup1 = await backup_manager.create_backup(name="similar_test")
    await asyncio.sleep(1) # Ensure different timestamps
    backup2 = await backup_manager.create_backup(name="similar_test")
    await asyncio.sleep(1)
    backup3 = await backup_manager.create_backup(name="other_test")

    assert backup2 is not None
    assert backup3 is not None

    # 2. Restore using a common part of the name/stem
    # _find_backup_path uses stem ending with identifier or exact filename match.
    # Let's use timestamp of backup2
    timestamp2 = backup2.stem.split("_")[-1]
    success, msg = await backup_manager.restore_backup(backup_identifier=timestamp2)

    # 3. Assertions
    assert success is True
    assert "Successfully restored" in msg
    # Verify it restored backup2 (need to check content or restore path)
    restore_base = backup_manager.backup_dir / "restores"
    restore_dirs = list(restore_base.glob(f"restore_{backup2.stem}_*"))
    assert len(restore_dirs) == 1

@pytest.mark.asyncio
async def test_restore_with_metadata_handling(backup_manager_fixture: BackupManager, test_project_root):
    """Test that metadata file is properly handled during restore."""
    backup_manager = backup_manager_fixture
    # 1. Create a backup with metadata
    metadata = {"test_key": "test_value", "backup_purpose": "testing"}
    backup_path = await backup_manager.create_backup(name="meta_test", metadata=metadata)
    assert backup_path is not None
    backup_id = backup_path.stem

    # 2. Restore to new location
    success, msg = await backup_manager.restore_backup(backup_id)
    assert success is True
    restore_target = Path(msg.split("'")[-2]) # Extract path from message

    # 3. Assert metadata file is NOT extracted
    assert not (restore_target / "backup_metadata.json").exists()
    # Assert other files are present
    assert (restore_target / "file1.txt").exists()

@pytest.mark.asyncio
async def test_restore_with_empty_backup(backup_manager_fixture: BackupManager, test_project_root):
    """Test restoring from an empty backup (only metadata file)."""
    backup_manager = backup_manager_fixture
    # 1. Create an empty backup (no files added to project root for backup)
    # Need to ensure _get_files_to_backup returns empty dict
    with patch.object(backup_manager, '_get_files_to_backup', return_value={}):
        backup_path = await backup_manager.create_backup(name="empty_test")

    assert backup_path is not None
    backup_id = backup_path.stem

    # 2. Restore
    success, msg = await backup_manager.restore_backup(backup_id)
    assert success is True
    restore_target = Path(msg.split("'")[-2])

    # 3. Assert target directory is empty (except maybe .gitkeep if created)
    assert restore_target.is_dir()
    # List directory contents excluding potential .gitkeep
    items_in_restore = [item for item in restore_target.iterdir() if item.name != '.gitkeep']
    assert len(items_in_restore) == 0

@pytest.mark.asyncio
async def test_restore_with_special_characters(backup_manager_fixture: BackupManager, test_project_root):
    """Test restoring files with special characters in names."""
    backup_manager = backup_manager_fixture
    # 1. Create files with special characters
    special_files = {
        "file with spaces.txt": "spaces",
        "file-with-hyphens.log": "hyphens",
        "file(paren).dat": "parens",
        "subdir/file&symbol.txt": "symbol"
    }
    for fname, content in special_files.items():
        fpath = test_project_root / fname
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content)

    # 2. Create backup
    backup_path = await backup_manager.create_backup(name="special_chars")
    assert backup_path is not None
    backup_id = backup_path.stem

    # 3. Restore
    success, msg = await backup_manager.restore_backup(backup_id)
    assert success is True
    restore_target = Path(msg.split("'")[-2])

    # 4. Assert files exist and have correct content
    for fname, content in special_files.items():
        restored_path = restore_target / fname
        assert restored_path.exists()
        assert restored_path.read_text() == content

@pytest.mark.asyncio
async def test_restore_with_large_directory_structure(
    backup_manager_fixture: BackupManager, test_project_root
):
    """Test restoring a backup with a large and deep directory structure."""
    backup_manager = backup_manager_fixture
    # 1. Create a complex directory structure
    complex_files = {}
    base = test_project_root
    for i in range(5):
        base = base / f"level_{i}"
        base.mkdir()
        for j in range(3):
            fpath = base / f"file_{i}_{j}.txt"
            content = f"content_{i}_{j}"
            fpath.write_text(content)
            complex_files[str(fpath.relative_to(test_project_root)).replace('\\', '/')] = content

    # 2. Create backup
    backup_path = await backup_manager.create_backup(name="deep_struct")
    assert backup_path is not None
    backup_id = backup_path.stem

    # 3. Restore
    success, msg = await backup_manager.restore_backup(backup_id)
    assert success is True
    restore_target = Path(msg.split("'")[-2])

    # 4. Assert structure and content
    for rel_path, content in complex_files.items():
        restored_path = restore_target / rel_path
        assert restored_path.exists()
        assert restored_path.read_text() == content

@pytest.mark.asyncio
async def test_restore_with_symlinks(backup_manager_fixture: BackupManager, test_project_root):
    """Test handling of symlinks during restore."""
    backup_manager = backup_manager_fixture
    # Skip on Windows if symlinks not supported or require admin
    import os
    if not hasattr(os, "symlink"):
        pytest.skip("Symlinks not supported/tested on this platform")

    # 1. Create a file and a symlink
    target_file = test_project_root / "target.txt"
    target_file.write_text("link target content")
    link_path = test_project_root / "link_to_target.txt"
    try:
        os.symlink(target_file.name, link_path) # Create relative link
    except OSError as e:
        pytest.skip(f"Could not create symlink, possibly due to permissions: {e}")

    # 2. Create backup (zipfile typically stores symlinks as is)
    backup_path = await backup_manager.create_backup(name="symlink_test")
    assert backup_path is not None
    backup_id = backup_path.stem

    # 3. Restore
    success, msg = await backup_manager.restore_backup(backup_id)
    assert success is True
    restore_target = Path(msg.split("'")[-2])

    # 4. Assert symlink exists and points correctly (relative to its location)
    restored_link = restore_target / "link_to_target.txt"
    restored_target = restore_target / "target.txt"
    assert restored_target.exists()
    assert restored_target.read_text() == "link target content"
    # Check if the link exists and is a symlink
    assert restored_link.exists() # zipfile should extract it
    if restored_link.exists(): # Add this check before is_symlink
        assert restored_link.is_symlink()
        # Check where the link points (os.readlink works on existing links)
        assert os.readlink(restored_link) == target_file.name

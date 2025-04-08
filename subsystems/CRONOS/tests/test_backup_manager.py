import asyncio
from datetime import datetime
import os
from pathlib import Path
import time
from typing import Any, Dict
from unittest.mock import MagicMock, patch
import zipfile

from koios.logger import KoiosLogger
from mycelium import Message
import pytest

from ..core.backup_manager import BackupManager


class MockMyceliumClient:
    def __init__(self):
        self.published_messages = []
        self.subscribed_handlers = {}

    async def publish(self, topic: str, data: Dict[str, Any]):
        self.published_messages.append({"topic": topic, "data": data})

    def subscribe(self, topic: str):
        def decorator(func):
            self.subscribed_handlers[topic] = func
            return func

        return decorator

    async def simulate_message(self, topic: str, data: Dict[str, Any], message_id: str = "test_id"):
        if topic in self.subscribed_handlers:
            message = Message(id=message_id, data=data)
            await self.subscribed_handlers[topic](message)


@pytest.fixture
def temp_backup_dir(tmp_path):
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    return backup_dir


@pytest.fixture
def temp_project_dir(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def mycelium_client():
    return MockMyceliumClient()


@pytest.fixture
def backup_manager(temp_backup_dir, temp_project_dir):
    return BackupManager(project_root=temp_project_dir, backup_dir=temp_backup_dir)


@pytest.fixture
def backup_manager_with_mycelium(temp_backup_dir, temp_project_dir, mycelium_client):
    return BackupManager(project_root=temp_project_dir, mycelium_client=mycelium_client)


def create_dummy_backup(backup_dir: Path, name: str, files: Dict[str, str]) -> Path:
    """Helper to create a dummy backup zip file with specified contents"""
    backup_path = backup_dir / f"{name}.zip"
    with zipfile.ZipFile(backup_path, "w") as zf:
        for file_path, content in files.items():
            zf.writestr(file_path, content)
    return backup_path


@pytest.mark.asyncio
async def test_list_backups_empty(backup_manager):
    """Test listing backups when directory is empty"""
    backups = await backup_manager.list_backups()
    assert len(backups) == 0


@pytest.mark.asyncio
async def test_list_backups_with_files(backup_manager, temp_backup_dir):
    """Test listing backups with multiple backup files present"""
    # Create some dummy backup files with slightly different times
    files = {"file1.txt": "content1", "file2.txt": "content2"}
    backup_path1 = create_dummy_backup(temp_backup_dir, "backup_20250401_001", files)
    # Ensure slightly different modification times for sorting
    time.sleep(0.1)
    backup_path2 = create_dummy_backup(temp_backup_dir, "backup_20250401_002", files)

    # list_backups is synchronous
    backups_info = backup_manager.list_backups()

    assert len(backups_info) == 2
    # Should be sorted newest first
    assert backups_info[0]["filename"] == backup_path2.name
    assert backups_info[1]["filename"] == backup_path1.name

    # Check structure of returned dicts
    for backup_info in backups_info:
        assert "filename" in backup_info
        assert "size_bytes" in backup_info
        assert "created_at" in backup_info
        assert isinstance(backup_info["filename"], str)
        assert isinstance(backup_info["size_bytes"], int)
        assert isinstance(backup_info["created_at"], str)  # ISO format string
        assert backup_info["size_bytes"] > 0


@pytest.mark.asyncio
async def test_restore_backup_replace_strategy(backup_manager, temp_backup_dir, temp_project_dir):
    """Test restoring backup with OVERWRITE strategy"""
    # Create initial project state
    (temp_project_dir / "existing.txt").write_text("old content")

    # Create backup with different content
    files = {"existing.txt": "new content", "new_file.txt": "backup content"}
    backup_path = create_dummy_backup(temp_backup_dir, "test_backup", files)

    # Restore backup with overwrite strategy
    success, message = await backup_manager.restore_backup(
        backup_identifier=backup_path.name, strategy="overwrite"
    )
    assert success is True

    # Verify restored state
    assert (temp_project_dir / "existing.txt").read_text() == "new content"
    assert (temp_project_dir / "new_file.txt").read_text() == "backup content"


@pytest.mark.asyncio
async def test_restore_backup_merge_strategy(backup_manager, temp_backup_dir, temp_project_dir):
    """Test restoring backup with merge strategy"""
    # Create initial project state
    (temp_project_dir / "existing.txt").write_text("keep this content")

    # Create backup with new files
    files = {"new_file1.txt": "backup content 1", "new_file2.txt": "backup content 2"}
    backup_path = create_dummy_backup(temp_backup_dir, "test_backup", files)

    # Restore backup with merge strategy
    await backup_manager.restore_backup(
        backup_identifier=backup_path.name, restore_target_path=temp_project_dir, strategy="merge"
    )

    # Verify merged state
    assert (temp_project_dir / "existing.txt").read_text() == "keep this content"
    assert (temp_project_dir / "new_file1.txt").read_text() == "backup content 1"
    assert (temp_project_dir / "new_file2.txt").read_text() == "backup content 2"


@pytest.mark.asyncio
async def test_restore_backup_invalid_strategy(backup_manager, temp_backup_dir, temp_project_dir):
    """Test restoring backup with invalid strategy"""
    files = {"test.txt": "content"}
    backup_path = create_dummy_backup(temp_backup_dir, "test_backup", files)

    with pytest.raises(ValueError, match="Invalid restore strategy"):
        await backup_manager.restore_backup(
            backup_identifier=backup_path.name,
            restore_target_path=temp_project_dir,
            strategy="invalid",
        )


@pytest.mark.asyncio
async def test_restore_backup_nonexistent_backup(backup_manager, temp_project_dir):
    """Test restoring nonexistent backup"""
    # Test with overwrite strategy (target path doesn't matter)
    success, message = await backup_manager.restore_backup(
        backup_identifier="nonexistent.zip", strategy="overwrite"
    )
    assert success is False
    assert "not found" in message.lower()

    # Test with new_location strategy
    success, message = await backup_manager.restore_backup(
        backup_identifier="nonexistent.zip", strategy="new_location"
    )
    assert success is False
    assert "not found" in message.lower()


@pytest.mark.asyncio
async def test_restore_backup_invalid_zip(backup_manager, temp_backup_dir, temp_project_dir):
    """Test restoring invalid zip file"""
    invalid_zip = temp_backup_dir / "invalid.zip"
    invalid_zip.write_text("not a zip file")

    # Test with overwrite strategy
    success, message = await backup_manager.restore_backup(
        backup_identifier="invalid.zip", strategy="overwrite"
    )
    assert success is False
    assert "corrupted or not a valid zip" in message.lower()

    # Test with new_location strategy
    success, message = await backup_manager.restore_backup(
        backup_identifier="invalid.zip",
        strategy="new_location",
        restore_target_path=str(
            temp_project_dir / "restore_target"
        ),  # Need target for new_location
    )
    assert success is False
    assert "corrupted or not a valid zip" in message.lower()


@pytest.mark.asyncio
async def test_backup_request_handler(backup_manager_with_mycelium, mycelium_client):
    """Test handling of backup requests via Mycelium."""
    # Create test files
    test_file = backup_manager_with_mycelium.project_root / "test.txt"
    test_file.write_text("test content")

    # Simulate backup request
    await mycelium_client.simulate_message(
        "cronos.backup.request", {"name": "test_backup", "type": "test"}
    )

    # Check published messages
    assert len(mycelium_client.published_messages) >= 2  # Status + at least one alert
    status_message = next(
        msg for msg in mycelium_client.published_messages if msg["topic"] == "cronos.backup.status"
    )
    assert status_message["data"]["status"] == "success"
    assert "backup_path" in status_message["data"]


@pytest.mark.asyncio
async def test_restore_request_handler(backup_manager_with_mycelium, mycelium_client):
    """Test handling of restore requests via Mycelium."""
    # Create a test backup
    test_file = backup_manager_with_mycelium.project_root / "test.txt"
    test_file.write_text("test content")
    backup_path = await backup_manager_with_mycelium.create_backup("test", "test")

    # Clear the project directory
    test_file.unlink()

    # Simulate restore request (using overwrite for simplicity here)
    await mycelium_client.simulate_message(
        backup_manager_with_mycelium.topics["restore_request"],
        {"backup_identifier": backup_path.name, "strategy": "overwrite"},  # Use overwrite strategy
    )

    # Check published messages
    restore_status = next(
        msg for msg in mycelium_client.published_messages if msg["topic"] == "cronos.restore.status"
    )
    assert restore_status["data"]["status"] == "success"

    # Verify restoration
    assert test_file.exists()
    assert test_file.read_text() == "test content"


@pytest.mark.asyncio
async def test_backup_progress_alerts(backup_manager_with_mycelium, mycelium_client):
    """Test that backup progress alerts are published."""
    # Create multiple test files
    for i in range(150):  # Should trigger at least one progress alert
        test_file = backup_manager_with_mycelium.project_root / f"test_{i}.txt"
        test_file.write_text(f"content {i}")

    # Create backup
    await backup_manager_with_mycelium.create_backup("test_progress", "test")

    # Check for progress alerts
    progress_alerts = [
        msg
        for msg in mycelium_client.published_messages
        if msg["topic"] == "cronos.alert" and "progress" in msg["data"]["message"].lower()
    ]
    assert len(progress_alerts) > 0


@pytest.mark.asyncio
async def test_backup_error_alerts(backup_manager_with_mycelium, mycelium_client, monkeypatch):
    """Test that error alerts are published when backup fails."""

    # Mock zipfile to raise an error
    def mock_zipfile_write(*args, **kwargs):
        raise Exception("Test error")

    monkeypatch.setattr(zipfile.ZipFile, "write", mock_zipfile_write)

    # Create test file
    test_file = backup_manager_with_mycelium.project_root / "test.txt"
    test_file.write_text("test content")

    # Attempt backup
    await backup_manager_with_mycelium.create_backup("test_error", "test")

    # Check for error alert
    error_alerts = [
        msg
        for msg in mycelium_client.published_messages
        if msg["topic"] == "cronos.alert" and msg["data"]["level"] == "error"
    ]
    assert len(error_alerts) > 0
    assert "error" in error_alerts[0]["data"]["message"].lower()


@pytest.mark.asyncio
async def test_restore_error_alerts(backup_manager_with_mycelium, mycelium_client):
    """Test that error alerts are published when restore fails."""
    # Simulate restore request with non-existent backup
    await mycelium_client.simulate_message(
        "cronos.restore.request", {"backup_identifier": "nonexistent.zip", "strategy": "replace"}
    )

    # Check for error status
    restore_status = next(
        msg for msg in mycelium_client.published_messages if msg["topic"] == "cronos.restore.status"
    )
    assert restore_status["data"]["status"] == "error"
    assert "error" in restore_status["data"]


@pytest.fixture
def mock_logger():
    """Fixture for a mock KoiosLogger."""
    # Use patch to temporarily replace the get_logger method if needed,
    # or just mock the instance methods used.
    mock = MagicMock(spec=KoiosLogger)
    # Mock methods used by BackupManager
    mock.info = MagicMock()
    mock.warning = MagicMock()
    mock.error = MagicMock()
    mock.debug = MagicMock()
    mock.exception = MagicMock()
    return mock


@pytest.fixture
def test_project_root(tmp_path):
    """Creates a temporary project root directory with some files."""
    root = tmp_path / "test_project"
    root.mkdir()
    (root / "file1.txt").write_text("content1")
    (root / "subdir").mkdir()
    (root / "subdir" / "file2.py").write_text("print('hello')")
    (root / ".venv").mkdir()  # Directory to be excluded
    (root / ".venv" / "some_lib").write_text("lib_content")
    (root / "backups").mkdir()  # Backup dir itself should be excluded from backups
    return root


@pytest.fixture
def backup_manager_config(test_project_root):
    """Provides configuration for BackupManager tests."""
    backup_dir = test_project_root / "test_backups"
    return {
        "backup": {
            "directory": str(backup_dir),  # Use str for JSON compatibility if loaded from file
            "retention_days": 1,  # Short retention for testing cleanup
            "max_backups": 2,  # Low max for testing cleanup
            "compression_level": 1,  # Faster compression for tests
        },
        "restore": {
            "default_strategy": "new_location",
            "verify_integrity": True,
            "create_restore_point": True,  # Enable restore points for testing
        },
        "performance": {"max_concurrent_operations": 1, "buffer_size_mb": 1},
        # Mock Mycelium config if needed by manager, though we pass mock client
        "mycelium": {
            "topics": {
                "alert": "test.cronos.alert"
                # Add other topics if handlers are tested directly
            }
        },
    }


@pytest.fixture
@patch(
    "subsystems.CRONOS.core.backup_manager.KoiosLogger"
)  # Patch KoiosLogger globally for this fixture
@pytest.fixture(scope="function")
def backup_manager_fixture(MockKoiosLogger, test_project_root, backup_manager_config, mock_logger):
    """Fixture for creating a BackupManager instance with mocks."""
    # Configure the class mock returned by patch
    MockKoiosLogger.get_logger.return_value = mock_logger

    mock_mycelium_client = MockMyceliumClient()

    # Create BackupManager instance
    # We need to simulate loading the config from a dict, not a path
    # Modify init slightly or create a helper if needed, for now assume direct dict usage
    # Or, mock the _load_config method
    with patch.object(BackupManager, "_load_config", return_value=backup_manager_config):
        manager = BackupManager(
            project_root=test_project_root, mycelium_client=mock_mycelium_client
        )
        # Ensure the backup dir exists after init
        manager.backup_dir.mkdir(parents=True, exist_ok=True)
        return manager


# --- Test Backup Creation (Prerequisite for Restore) ---
@pytest.mark.asyncio
async def test_create_simple_backup(backup_manager: BackupManager, test_project_root):
    """Test creating a basic backup."""
    backup_name = "test_backup_simple"
    backup_path = await backup_manager.create_backup(name=backup_name)

    assert backup_path is not None
    assert backup_path.exists()
    assert backup_path.name.startswith(f"egos_backup_manual_{backup_name}_")

    # Verify content (basic check)
    with zipfile.ZipFile(backup_path, "r") as zipf:
        namelist = zipf.namelist()
        assert "file1.txt" in namelist
        assert "subdir/file2.py" in namelist
        assert not any(f.startswith(".venv/") for f in namelist)
        assert not any(f.startswith(backup_manager.backup_dir.name + "/") for f in namelist)
        assert "backup_metadata.json" not in namelist  # No metadata passed


# --- Test Restore Functionality ---


@pytest.mark.asyncio
async def test_restore_new_location_default(backup_manager: BackupManager, test_project_root):
    """Test restoring to a default new location."""
    # 1. Create a backup
    backup_path = await backup_manager.create_backup(name="restore_test_new_default")
    assert backup_path is not None
    backup_id = backup_path.stem  # Use stem (filename without .zip) as identifier

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
    assert not (restore_target / ".venv").exists()  # Should not restore excluded dirs


@pytest.mark.asyncio
async def test_restore_new_location_specific(
    backup_manager: BackupManager, test_project_root, tmp_path
):
    """Test restoring to a specific new location."""
    # 1. Create a backup
    backup_path = await backup_manager.create_backup(name="restore_test_new_spec")
    assert backup_path is not None
    backup_id = backup_path.stem

    # 2. Define specific target and restore
    specific_target = tmp_path / "my_restore_location"
    success, msg = await backup_manager.restore_backup(
        backup_identifier=backup_id,
        restore_target_path=str(specific_target),
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
    backup_manager: BackupManager, test_project_root, tmp_path
):
    """Test failure when target for new_location exists and is not empty."""
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
        restore_target_path=str(specific_target),
        strategy="new_location",
    )

    # 4. Assertions
    assert success is False
    assert "must not exist or be empty" in msg
    assert (specific_target / "dummy.txt").exists()  # Original file should remain
    assert not (specific_target / "file1.txt").exists()  # Backup file should not be there


@pytest.mark.asyncio
async def test_restore_overwrite_with_restore_point(
    backup_manager: BackupManager, test_project_root
):
    """Test restoring with overwrite strategy, creating a restore point."""
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
        restore_target_path=str(test_project_root),  # Target must be specified for overwrite
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
async def test_restore_overwrite_no_restore_point(backup_manager: BackupManager, test_project_root):
    """Test restoring with overwrite, restore point disabled."""
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
    success, msg = await backup_manager.restore_backup(
        backup_id, str(test_project_root), "overwrite"
    )

    # 4. Assertions
    assert success is True
    assert original_file.read_text() == original_content  # Overwritten
    # Check that NO restore point was created this time
    assert not any(
        p.name.startswith("egos_backup_restore_point_")
        for p in backup_manager.backup_dir.glob("*.zip")
    )


@pytest.mark.asyncio
async def test_restore_invalid_backup_id(backup_manager: BackupManager):
    """Test restoring with an invalid backup identifier."""
    success, msg = await backup_manager.restore_backup("non_existent_backup_123")
    assert success is False
    assert "not found" in msg


@pytest.mark.asyncio
async def test_restore_corrupted_backup(backup_manager: BackupManager, test_project_root):
    """Test restoring from a corrupted zip file (with integrity check)."""
    # Ensure integrity check is enabled
    backup_manager.config["restore"]["verify_integrity"] = True

    # 1. Create a dummy corrupted file
    corrupted_zip_path = backup_manager.backup_dir / "corrupted_backup_test.zip"
    corrupted_zip_path.write_text("this is not a zip file")

    # 2. Attempt restore
    success, msg = await backup_manager.restore_backup(backup_identifier=corrupted_zip_path.name)

    # 3. Assertions
    assert success is False
    assert "corrupted" in msg or "BadZipFile" in msg or "integrity check failed" in msg

    # Try with integrity check disabled
    backup_manager.config["restore"]["verify_integrity"] = False
    success_no_check, msg_no_check = await backup_manager.restore_backup(
        backup_identifier=corrupted_zip_path.name
    )
    assert success_no_check is False  # Should still fail on extraction
    assert "corrupted" in msg_no_check or "BadZipFile" in msg_no_check


@pytest.mark.asyncio
async def test_restore_unsupported_strategy(backup_manager: BackupManager):
    """Test using an unsupported restore strategy."""
    # 1. Create a backup first so find works
    backup_path = await backup_manager.create_backup(name="strategy_test")
    backup_id = backup_path.stem

    # 2. Attempt restore with bad strategy
    success, msg = await backup_manager.restore_backup(backup_id, strategy="merge_dangerously")

    # 3. Assertions
    assert success is False
    assert "Unsupported restore strategy" in msg


# --- Test Helper Method (_find_backup_path) ---


@pytest.mark.asyncio
async def test_find_backup_path(backup_manager: BackupManager):
    """Test the helper method for finding backup paths."""
    # 1. Create some backups with predictable names/timestamps
    ts_format = "%Y%m%d_%H%M%S"
    t1 = datetime.datetime.now() - datetime.timedelta(hours=2)
    t2 = datetime.datetime.now() - datetime.timedelta(hours=1)
    t3 = datetime.datetime.now()

    name1 = f"egos_backup_manual_find_test_{t1.strftime(ts_format)}.zip"
    name2 = f"egos_backup_manual_find_test_{t2.strftime(ts_format)}.zip"
    name3 = f"egos_backup_auto_other_{t3.strftime(ts_format)}.zip"

    (backup_manager.backup_dir / name1).touch()
    (backup_manager.backup_dir / name2).touch()
    (backup_manager.backup_dir / name3).touch()
    time.sleep(0.1)  # Ensure modification times are distinct if needed

    # Test find by exact name
    assert backup_manager._find_backup_path(name2) == (backup_manager.backup_dir / name2)

    # Test find by timestamp part (should get latest matching)
    timestamp_prefix = t2.strftime("%Y%m%d")
    assert backup_manager._find_backup_path(timestamp_prefix) == (
        backup_manager.backup_dir / name2
    ), "Should find latest matching prefix"

    # Test find by unique timestamp
    assert backup_manager._find_backup_path(t3.strftime(ts_format)) == (
        backup_manager.backup_dir / name3
    )

    # Test find by stem
    assert backup_manager._find_backup_path(Path(name1).stem) == (backup_manager.backup_dir / name1)

    # Test not found
    assert backup_manager._find_backup_path("nonexistent_abc") is None
    assert backup_manager._find_backup_path("19990101_000000") is None


@pytest.mark.asyncio
async def test_restore_with_integrity_check_disabled(
    backup_manager: BackupManager, test_project_root
):
    """Test restoring with integrity check disabled."""
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
async def test_restore_with_timestamp_identifier(backup_manager: BackupManager, test_project_root):
    """Test restoring using timestamp as identifier."""
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
async def test_restore_with_partial_identifier(backup_manager: BackupManager, test_project_root):
    """Test restoring using partial backup name as identifier."""
    # 1. Create a backup with a distinctive name
    backup_path = await backup_manager.create_backup(name="unique_partial_test")
    assert backup_path is not None

    # 2. Restore using just part of the name
    success, msg = await backup_manager.restore_backup(backup_identifier="unique_partial")

    # 3. Assertions
    assert success is True
    assert "Successfully restored" in msg


@pytest.mark.asyncio
async def test_restore_with_multiple_matching_backups(
    backup_manager: BackupManager, test_project_root
):
    """Test restoring when multiple backups match the identifier (should use latest)."""
    # 1. Create multiple backups with similar names
    await asyncio.sleep(1)  # Ensure different timestamps
    backup2 = await backup_manager.create_backup(name="similar_test")

    # 2. Restore using a common part of the name
    success, msg = await backup_manager.restore_backup(backup_identifier="similar_test")

    # 3. Assertions
    assert success is True
    assert "Successfully restored" in msg
    # Should have used the latest backup (backup2)
    assert backup2.stem in msg


@pytest.mark.asyncio
async def test_restore_with_metadata_handling(backup_manager: BackupManager, test_project_root):
    """Test that metadata file is properly handled during restore."""
    # 1. Create a backup with metadata
    metadata = {"test_key": "test_value", "backup_purpose": "testing"}
    backup_path = await backup_manager.create_backup(name="metadata_test", metadata=metadata)
    assert backup_path is not None

    # 2. Verify metadata exists in backup
    with zipfile.ZipFile(backup_path, "r") as zipf:
        assert "backup_metadata.json" in zipf.namelist()

    # 3. Restore the backup
    success, msg = await backup_manager.restore_backup(backup_identifier=backup_path.stem)

    # 4. Verify metadata file was not restored (should be skipped)
    restore_base = backup_manager.backup_dir / "restores"
    restore_dirs = list(restore_base.glob(f"restore_{backup_path.stem}_*"))
    assert len(restore_dirs) == 1
    restore_target = restore_dirs[0]
    assert not (restore_target / "backup_metadata.json").exists()


@pytest.mark.asyncio
async def test_restore_with_empty_backup(backup_manager: BackupManager, test_project_root):
    """Test restoring from an empty backup."""
    # 1. Create an empty backup (no files)
    backup_path = create_dummy_backup(backup_manager.backup_dir, "empty_backup", {})

    # 2. Restore the empty backup
    success, msg = await backup_manager.restore_backup(backup_identifier=backup_path.stem)

    # 3. Assertions
    assert success is True
    assert "Extracted 0 items" in msg


@pytest.mark.asyncio
async def test_restore_with_special_characters(backup_manager: BackupManager, test_project_root):
    """Test restoring files with special characters in names."""
    # 1. Create files with special characters
    special_files = {
        "file with spaces.txt": "content1",
        "file_with_@#$%^.txt": "content2",
        "folder with spaces/nested file.txt": "content3",
        "deeply/nested/path/with/@#/special/chars.txt": "content4",
    }
    backup_path = create_dummy_backup(
        backup_manager.backup_dir, "special_chars_test", special_files
    )

    # 2. Restore the backup
    success, msg = await backup_manager.restore_backup(backup_identifier=backup_path.stem)

    # 3. Assertions
    assert success is True
    restore_base = backup_manager.backup_dir / "restores"
    restore_dirs = list(restore_base.glob(f"restore_{backup_path.stem}_*"))
    restore_target = restore_dirs[0]

    # Verify all files were restored correctly
    for file_path, content in special_files.items():
        restored_file = restore_target / file_path.replace("/", os.sep)
        assert restored_file.exists()
        assert restored_file.read_text() == content


@pytest.mark.asyncio
async def test_restore_with_large_directory_structure(
    backup_manager: BackupManager, test_project_root
):
    """Test restoring a backup with a large and deep directory structure."""
    # 1. Create a complex directory structure
    complex_files = {}
    for i in range(5):  # Create 5 levels
        for j in range(3):  # 3 files per level
            path = "/".join([f"level_{k}" for k in range(i + 1)])
            file_path = f"{path}/file_{j}.txt"
            complex_files[file_path] = f"content for {file_path}"

    backup_path = create_dummy_backup(backup_manager.backup_dir, "complex_structure", complex_files)

    # 2. Restore the backup
    success, msg = await backup_manager.restore_backup(backup_identifier=backup_path.stem)

    # 3. Assertions
    assert success is True
    restore_base = backup_manager.backup_dir / "restores"
    restore_dirs = list(restore_base.glob(f"restore_{backup_path.stem}_*"))
    restore_target = restore_dirs[0]

    # Verify directory structure was preserved
    for file_path, content in complex_files.items():
        restored_file = restore_target / file_path.replace("/", os.sep)
        assert restored_file.exists()
        assert restored_file.read_text() == content


@pytest.mark.asyncio
async def test_restore_with_symlinks(backup_manager: BackupManager, test_project_root):
    """Test handling of symlinks during restore."""
    # Skip on Windows if symlinks not supported
    if not hasattr(os, "symlink"):
        pytest.skip("Symlinks not supported on this platform")

    # 1. Create a file and a symlink to it
    original_file = test_project_root / "original.txt"
    original_file.write_text("original content")
    symlink_path = test_project_root / "link_to_original"
    try:
        os.symlink(original_file, symlink_path)
    except OSError as e:
        if "privilege" in str(e):
            pytest.skip("Insufficient privileges to create symlinks")
        raise

    # 2. Create backup
    backup_path = await backup_manager.create_backup(name="symlink_test")

    # 3. Restore to new location
    success, msg = await backup_manager.restore_backup(backup_identifier=backup_path.stem)

    # 4. Assertions
    assert success is True
    restore_base = backup_manager.backup_dir / "restores"
    restore_dirs = list(restore_base.glob(f"restore_{backup_path.stem}_*"))
    restore_target = restore_dirs[0]

    # Check if original file and symlink were restored
    restored_original = restore_target / "original.txt"
    restored_symlink = restore_target / "link_to_original"
    assert restored_original.exists()
    if restored_symlink.exists():
        assert restored_symlink.is_symlink()

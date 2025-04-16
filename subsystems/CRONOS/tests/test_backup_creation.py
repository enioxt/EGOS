import pytest
from pathlib import Path
import zipfile
from unittest.mock import patch, MagicMock

from ..core.backup_manager import BackupManager

# Uses fixtures defined in conftest.py: temp_project_dir, backup_manager_fixture

@pytest.mark.asyncio
async def test_create_simple_backup(backup_manager_fixture: BackupManager, test_project_root):
    """Test creating a basic backup using the main fixture."""
    backup_manager = backup_manager_fixture # Use the fixture instance
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
        # Backup dir exclusion check needs careful path handling
        # assert not any(f.startswith(backup_manager.backup_dir.name + "/") for f in namelist)
        assert "backup_metadata.json" in namelist # Metadata should be present now

@pytest.mark.asyncio
async def test_create_backup_with_metadata(backup_manager_fixture: BackupManager):
    """Test creating a backup with custom metadata."""
    backup_manager = backup_manager_fixture
    metadata = {"user": "test_user", "commit": "abc1234"}
    backup_path = await backup_manager.create_backup(name="backup_with_meta", metadata=metadata)

    assert backup_path is not None
    assert backup_path.exists()

    # Verify metadata was written
    with zipfile.ZipFile(backup_path, "r") as zipf:
        assert "backup_metadata.json" in zipf.namelist()
        with zipf.open("backup_metadata.json") as meta_f:
            import json
            written_meta = json.load(meta_f)
            assert written_meta["user"] == "test_user"
            assert written_meta["commit"] == "abc1234"
            assert written_meta["name"] == "backup_with_meta"
            assert written_meta["backup_type"] == "manual"

@pytest.mark.asyncio
async def test_create_backup_excludes(backup_manager_fixture: BackupManager, test_project_root):
    """Test backup creation honors exclusion patterns."""
    backup_manager = backup_manager_fixture
    # Add a file that should be excluded by default extension
    (test_project_root / "file.pyc").touch()
    # Add a file to be excluded by custom pattern
    (test_project_root / "subdir" / "exclude_this.log").write_text("exclude me")

    backup_path = await backup_manager.create_backup(
        name="backup_excludes",
        exclude_patterns=["subdir/exclude_this.log", "*.tmp"] # Add specific excludes
    )

    assert backup_path is not None
    with zipfile.ZipFile(backup_path, "r") as zipf:
        namelist = zipf.namelist()
        assert "file1.txt" in namelist
        assert "subdir/file2.py" in namelist
        assert "file.pyc" not in namelist # Excluded by default
        assert "subdir/exclude_this.log" not in namelist # Excluded by pattern
        assert not any(f.startswith(".venv/") for f in namelist)

@pytest.mark.asyncio
async def test_create_backup_failure_on_zip_error(backup_manager_fixture: BackupManager, mock_logger):
    """Test backup failure if zip writing fails."""
    backup_manager = backup_manager_fixture
    backup_name = "test_zip_fail"

    # Mock zipfile to raise an error during write
    with patch("zipfile.ZipFile") as mock_zip_class:
        mock_zip_instance = MagicMock()
        mock_zip_instance.writestr.side_effect = zipfile.BadZipFile("Simulated write error")
        mock_zip_instance.__enter__.return_value = mock_zip_instance # Handle context manager
        mock_zip_class.return_value = mock_zip_instance

        backup_path_result = await backup_manager.create_backup(name=backup_name)

        assert backup_path_result is None
        # Check logs for error message
        mock_logger.error.assert_called()
        args, kwargs = mock_logger.error.call_args
        assert "Backup creation failed" in args[0]
        assert isinstance(kwargs.get("exc_info"), zipfile.BadZipFile)

        # Check if incomplete file was removed
        backup_path_expected = backup_manager.backup_dir / f"egos_backup_manual_{backup_name}_*.zip" # Use glob pattern
        assert not list(backup_manager.backup_dir.glob(backup_path_expected.name)) # No matching file should exist

# Add more backup creation tests as needed (e.g., include patterns, empty project)

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from koios.logger import KoiosLogger
from ..core.backup_manager import BackupManager

# Define common fixtures here

@pytest.fixture
def temp_backup_dir(tmp_path):
    """Creates a temporary directory for storing backups."""
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    return backup_dir

@pytest.fixture
def temp_project_dir(tmp_path):
    """Creates a temporary directory representing the project root."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    # Add some initial files for backup tests
    (project_dir / "file1.txt").write_text("content1")
    (project_dir / "subdir").mkdir()
    (project_dir / "subdir" / "file2.py").write_text("print('hello')")
    (project_dir / ".venv").mkdir() # Directory to be excluded
    (project_dir / ".venv" / "some_lib").write_text("lib_content")
    (project_dir / "backups").mkdir() # Backup dir itself should be excluded
    return project_dir

@pytest.fixture
def mock_logger():
    """Fixture for a mock KoiosLogger."""
    mock = MagicMock(spec=KoiosLogger)
    mock.info = MagicMock()
    mock.warning = MagicMock()
    mock.error = MagicMock()
    mock.debug = MagicMock()
    mock.exception = MagicMock()
    mock.log = MagicMock() # Add mock for generic log method if used
    return mock

@pytest.fixture
def backup_manager_config(temp_backup_dir): # Use temp_backup_dir fixture
    """Provides configuration for BackupManager tests."""
    return {
        "backup": {
            "directory": str(temp_backup_dir), # Use the temp dir path
            "retention_days": 1, # Short retention for testing cleanup
            "max_backups": 2, # Low max for testing cleanup
            "compression_level": 1, # Faster compression for tests
        },
        "restore": {
            "default_strategy": "new_location",
            "verify_integrity": True,
            "create_restore_point": True, # Enable restore points for testing
        },
        "performance": {"max_concurrent_operations": 1, "buffer_size_mb": 1},
        "excluded_directories": [".venv", "__pycache__", ".git", "node_modules", "backups", "logs", "data", ".ruff_cache", "htmlcov", "dist", "build"],
        "excluded_extensions": [".pyc", ".egg-info"]
    }

@pytest.fixture
@patch("subsystems.CRONOS.core.backup_manager.KoiosLogger")
def backup_manager_fixture(MockKoiosLogger, test_project_root, backup_manager_config, mock_logger):
    """Fixture for creating a BackupManager instance with mocks."""
    MockKoiosLogger.get_logger.return_value = mock_logger

    # Mock the config loading to use our fixture config
    with patch.object(BackupManager, "_load_config", return_value=backup_manager_config):
         # Patch history loading to prevent actual file access during most tests
         # Tests specifically for history should unpatch this or mock differently
        with patch.object(BackupManager, "_load_version_history", return_value=None):
            # Instantiate WITHOUT config_path, relying on the patched _load_config
            manager = BackupManager(project_root=test_project_root)
            # Ensure the backup dir (from config) exists after init
            manager.backup_dir.mkdir(parents=True, exist_ok=True)
            # Assign the mock logger instance directly if needed elsewhere
            manager.logger = mock_logger
            return manager

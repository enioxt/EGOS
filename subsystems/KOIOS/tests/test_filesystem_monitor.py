"""
EVA & GUARANI - METADATA Subsystem
Test Suite for Filesystem Monitor
Version: 1.0
"""

from pathlib import Path
import tempfile
import time
from typing import List
from unittest.mock import MagicMock

import pytest

from ..core.filesystem_monitor import FilesystemMonitor, MetadataEventHandler
from ..core.metadata_manager import MetadataManager


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture
def callback():
    """Create a mock callback function."""
    return MagicMock()


@pytest.fixture
def monitor(temp_dir, callback):
    """Create a filesystem monitor instance for testing."""
    monitor = FilesystemMonitor(temp_dir, callback)
    yield monitor
    monitor.stop()


def create_test_file(directory: str, filename: str, content: str = "test content") -> Path:
    """Create a test file in the specified directory.

    Args:
        directory (str): Directory to create the file in
        filename (str): Name of the file
        content (str): Content to write to the file

    Returns:
        Path: Path to the created file
    """
    file_path = Path(directory) / filename
    file_path.write_text(content)
    return file_path


def test_monitor_initialization(monitor, temp_dir):
    """Test filesystem monitor initialization."""
    assert monitor is not None
    assert monitor.root_dir == Path(temp_dir)
    assert isinstance(monitor.metadata_manager, MetadataManager)
    assert isinstance(monitor.event_handler, MetadataEventHandler)
    assert isinstance(monitor._active_monitors, set)


def test_monitor_start_stop(monitor, temp_dir):
    """Test starting and stopping the monitor."""
    # Start monitoring
    monitor.start()
    assert str(monitor.root_dir) in monitor._active_monitors
    assert monitor.observer.is_alive()

    # Stop monitoring
    monitor.stop()
    assert str(monitor.root_dir) not in monitor._active_monitors
    assert not monitor.observer.is_alive()


def test_file_creation_event(monitor, temp_dir, callback):
    """Test handling of file creation events."""
    monitor.start()
    time.sleep(0.1)  # Allow monitor to start

    # Create a new file
    test_file = create_test_file(temp_dir, "test_creation.py")
    time.sleep(0.1)  # Allow event to be processed

    callback.assert_called_with(test_file, "created")


def test_file_modification_event(monitor, temp_dir, callback):
    """Test handling of file modification events."""
    # Create initial file
    test_file = create_test_file(temp_dir, "test_modification.py")

    monitor.start()
    time.sleep(0.1)  # Allow monitor to start

    # Modify the file
    test_file.write_text("modified content")
    time.sleep(0.1)  # Allow event to be processed

    callback.assert_called_with(test_file, "modified")


def test_ignored_patterns(monitor, temp_dir, callback):
    """Test that ignored patterns are respected."""
    monitor.start()
    time.sleep(0.1)  # Allow monitor to start

    # Create files in ignored directories
    ignored_dirs = [".git", "node_modules", "__pycache__", "venv", "temp", "logs", "Backups"]

    for ignored_dir in ignored_dirs:
        # Create directory
        dir_path = Path(temp_dir) / ignored_dir
        dir_path.mkdir(exist_ok=True)

        # Create file in ignored directory
        create_test_file(str(dir_path), "test.py")
        time.sleep(0.1)  # Allow event to be processed

        # Verify callback was not called
        callback.assert_not_called()


def test_directory_management(monitor, temp_dir):
    """Test adding and removing directories from monitoring."""
    monitor.start()

    # Create test directories
    test_dirs = ["dir1", "dir2", "dir3"]
    created_dirs: List[Path] = []

    for dir_name in test_dirs:
        dir_path = Path(temp_dir) / dir_name
        dir_path.mkdir()
        created_dirs.append(dir_path)

        # Add directory to monitoring
        monitor.add_directory(str(dir_path))
        assert monitor.is_monitoring(str(dir_path))

    # Verify all directories are being monitored
    active_monitors = monitor.get_active_monitors()
    assert len(active_monitors) == len(test_dirs) + 1  # +1 for root directory

    # Remove directories from monitoring
    for dir_path in created_dirs:
        monitor.remove_directory(str(dir_path))
        assert not monitor.is_monitoring(str(dir_path))

    # Verify only root directory remains
    assert len(monitor.get_active_monitors()) == 1
    assert str(monitor.root_dir) in monitor.get_active_monitors()


def test_process_existing_files(monitor, temp_dir, callback):
    """Test processing of existing files."""
    # Create test files before starting monitor
    test_files = [
        create_test_file(temp_dir, "existing1.py"),
        create_test_file(temp_dir, "existing2.py"),
        create_test_file(temp_dir, "existing3.py"),
    ]

    monitor.start()
    monitor.process_existing_files()
    time.sleep(0.1)  # Allow processing to complete

    # Verify each file was processed
    assert callback.call_count == len(test_files)
    for test_file in test_files:
        callback.assert_any_call(test_file, "existing")


def test_debounce_mechanism(monitor, temp_dir, callback):
    """Test the debounce mechanism for rapid file changes."""
    monitor.start()
    time.sleep(0.1)  # Allow monitor to start

    test_file = create_test_file(temp_dir, "test_debounce.py")

    # Rapidly modify the file multiple times
    for i in range(5):
        test_file.write_text(f"content {i}")
        time.sleep(0.1)  # Small delay between modifications

    time.sleep(1.0)  # Allow debounce period to complete

    # Verify that not all modifications triggered callbacks
    assert callback.call_count < 5


def test_error_handling(monitor, temp_dir, callback):
    """Test error handling in the monitor."""
    monitor.start()

    # Test with invalid directory path structure
    with pytest.raises(OSError):  # Expect OSError for invalid path format
        monitor.add_directory("invalid/path")

    # Test with non-existent directory path
    non_existent = str(Path(temp_dir) / "non_existent")
    with pytest.raises(FileNotFoundError):  # Expect FileNotFoundError if path doesn't exist
        monitor.add_directory(non_existent)

    # Test removing non-monitored directory
    random_dir = str(Path(temp_dir) / "random")
    monitor.remove_directory(random_dir)  # Should not raise exception

    # Verify monitor is still functioning
    test_file = create_test_file(temp_dir, "test_after_error.py")
    time.sleep(0.1)
    callback.assert_called_with(test_file, "created")


def test_multiple_monitors(temp_dir, callback):
    """Test running multiple monitors simultaneously."""
    # Create test directories
    dir1 = Path(temp_dir) / "dir1"
    dir2 = Path(temp_dir) / "dir2"
    dir1.mkdir()
    dir2.mkdir()

    # Create separate monitors
    monitor1 = FilesystemMonitor(str(dir1), callback)
    monitor2 = FilesystemMonitor(str(dir2), callback)

    try:
        # Start both monitors
        monitor1.start()
        monitor2.start()
        time.sleep(0.1)

        # Create files in both directories
        file1 = create_test_file(str(dir1), "test1.py")
        file2 = create_test_file(str(dir2), "test2.py")
        time.sleep(0.1)

        # Verify both files were detected
        assert callback.call_count == 2
        callback.assert_any_call(file1, "created")
        callback.assert_any_call(file2, "created")

    finally:
        monitor1.stop()
        monitor2.stop()


if __name__ == "__main__":
    pytest.main(["-v", __file__])

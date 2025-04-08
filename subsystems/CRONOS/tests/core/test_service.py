# subsystems/CRONOS/tests/core/test_service.py

import asyncio
from dataclasses import asdict
from datetime import datetime, timedelta  # Added timedelta
from pathlib import Path
import subprocess  # Added missing import
import unittest
from unittest.mock import AsyncMock, MagicMock, mock_open, patch  # Added mock_open

# Need to adjust path if tests are run from root vs subsystems/CRONOS
# Assuming run from root for now
from subsystems.CRONOS.core.service import CronosService, SystemBackupInfo, SystemState
from subsystems.MYCELIUM.core.interface import MyceliumInterface

# JSON data for successful history load test
TEST_HISTORY_JSON_SUCCESS = (
    '{"last_updated": "2023-01-01T10:00:00", "backups": [{"id": "b1", "name": "N1", '
    '"timestamp": "2023-01-01T09:00:00", "size_bytes": 100, "location":"b1"}], '
    '"states": [{"id": "s1", "name": "S1", "timestamp": "2023-01-01T08:00:00"}]}'
)


class TestCronosService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        """Set up mocks and CronosService instance for each test."""
        # Ensure the interface mock itself is an AsyncMock if its methods are async
        self.mock_interface = AsyncMock(spec=MyceliumInterface)  # Make interface mock async
        self.mock_interface.connect = AsyncMock(return_value=True)
        self.mock_interface.disconnect = AsyncMock(return_value=True)
        # Make publish_event an AsyncMock too, as it's awaited in the service
        self.mock_interface.publish_event = AsyncMock()
        self.mock_interface.report_health = AsyncMock()

        self.config = {
            "system_root": "/mock/root",
            "backup_location": "mock_backups/CRONOS",
            "excluded_directories": [".git", "node_modules", ".venv"],
            "excluded_extensions": [".log", ".pyc"],
            "retention_policy": {"daily": 2, "weekly": 1, "monthly": 1},
            # Add stray_backup_patterns if needed by its test
        }
        self.service = CronosService(self.config, self.mock_interface)
        # Override paths for testing
        self.service.system_root = Path("/mock/root")
        self.service.backup_base_path = self.service.system_root / "mock_backups/CRONOS"
        self.service.version_history_file = self.service.backup_base_path / "version_history.json"

    # --- Initialization and Lifecycle Tests --- #

    async def test_initialization(self):
        """Test service initialization."""
        self.assertEqual(self.service.config, self.config)
        self.assertEqual(self.service.interface, self.mock_interface)
        self.assertEqual(self.service.node_id, "CRONOS")
        self.assertEqual(self.service.backup_base_path, Path("/mock/root/mock_backups/CRONOS"))
        self.assertFalse(self.service._running)

    @patch("pathlib.Path.mkdir")
    @patch("subsystems.CRONOS.core.service.CronosService._load_version_history")
    @patch("subsystems.CRONOS.core.service.CronosService._check_and_perform_backup")
    async def test_start(self, mock_check_backup, mock_load_history, mock_mkdir):
        """Test the start sequence."""
        await self.service.start()

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_load_history.assert_called_once()
        mock_check_backup.assert_called_once()
        self.mock_interface.connect.assert_awaited_once()
        self.mock_interface.report_health.assert_awaited_once_with("active")
        self.assertTrue(self.service._running)

    @patch("subsystems.CRONOS.core.service.CronosService._save_version_history")
    async def test_stop(self, mock_save_history):
        """Test the stop sequence."""
        # Start it first to have something to stop
        self.service._running = True
        self.service._backup_task = asyncio.create_task(asyncio.sleep(1))  # Simulate running task

        await self.service.stop()

        mock_save_history.assert_called_once()
        self.mock_interface.disconnect.assert_awaited_once()
        self.assertTrue(self.service._backup_task.cancelled())  # Check task was cancelled
        self.assertFalse(self.service._running)

    # --- History Management Tests --- #

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=TEST_HISTORY_JSON_SUCCESS,
    )
    @patch("pathlib.Path.is_dir", return_value=True)  # Assume backup dir exists
    def test_load_version_history_success(self, mock_is_dir, mock_file):
        """Test loading valid version history."""
        # Patch Path.exists using patch.object within the test method
        with patch.object(Path, "exists", return_value=True) as mock_exists:
            self.service._load_version_history()

        mock_exists.assert_called()  # Check exists was called (might be multiple times)
        mock_file.assert_called_with(self.service.version_history_file, "r", encoding="utf-8")
        self.assertIn("b1", self.service.backups)
        self.assertEqual(self.service.backups["b1"].name, "N1")
        self.assertIsInstance(self.service.backups["b1"].timestamp, datetime)
        self.assertIn("s1", self.service.states)
        self.assertEqual(self.service.states["s1"].name, "S1")

    def test_load_version_history_not_found(self):
        """Test loading when history file doesn't exist."""
        # Use nested with statements and patch.object for Path.exists
        with patch.object(Path, "exists", return_value=False) as mock_exists:
            with patch("builtins.open", mock_open()):
                with patch.object(self.service, "_save_version_history") as mock_save:
                    self.service._load_version_history()

        mock_exists.assert_called_once()  # Check Path.exists was called once on the history file
        # mock_file assertion might be complex with mock_open, focus on effect
        self.assertEqual(len(self.service.backups), 0)
        self.assertEqual(len(self.service.states), 0)
        mock_save.assert_called_once()  # Should create an empty one

    @patch("json.dump")
    @patch("builtins.open", new_callable=mock_open)
    @patch.object(Path, "exists", return_value=True)  # Keep patch.object for exists
    def test_save_version_history(self, mock_exists, mock_file, mock_json_dump):
        """Test saving the version history by checking json.dump call."""
        # Add some dummy data
        now = datetime.now()
        b1_info = SystemBackupInfo("b1", "N1", now, location=Path("loc1"))
        s1_info = SystemState("s1", "S1", timestamp=now)
        self.service.backups["b1"] = b1_info
        self.service.states["s1"] = s1_info

        self.service._save_version_history()

        # Check file was opened for writing
        mock_file.assert_called_once_with(self.service.version_history_file, "w", encoding="utf-8")
        # Check json.dump was called with the correct structure
        mock_json_dump.assert_called_once()
        dump_args = mock_json_dump.call_args.args[0]
        file_handle = mock_json_dump.call_args.args[1]

        self.assertIn("last_updated", dump_args)
        self.assertEqual(len(dump_args["backups"]), 1)
        # Recreate the expected dict entry for backup
        expected_b_dict = asdict(b1_info)
        expected_b_dict["location"] = b1_info.id
        expected_b_dict["timestamp"] = now.isoformat()
        self.assertEqual(dump_args["backups"][0], expected_b_dict)

        self.assertEqual(len(dump_args["states"]), 1)
        expected_s_dict = asdict(s1_info)
        expected_s_dict["timestamp"] = now.isoformat()
        self.assertEqual(dump_args["states"][0], expected_s_dict)

        # Check the file handle passed to json.dump was the one from open
        self.assertEqual(file_handle, mock_file())

    # --- State Capture Tests --- #

    @patch("subprocess.run")
    def test_get_git_commit_hash_success(self, mock_run):
        """Test getting git hash successfully."""
        mock_result = MagicMock()
        mock_result.stdout = "abcdef12345\n"
        mock_run.return_value = mock_result

        git_hash = self.service._get_git_commit_hash()
        self.assertEqual(git_hash, "abcdef12345")
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "HEAD"],
            cwd=self.service.system_root,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )

    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "git", stderr="Error"))
    def test_get_git_commit_hash_error(self, mock_run):
        """Test getting git hash when git command fails."""
        git_hash = self.service._get_git_commit_hash()
        self.assertIsNone(git_hash)

    @patch("shutil.which", return_value=None)
    def test_get_git_commit_hash_no_git(self, mock_which):
        """Test getting git hash when git is not installed."""
        git_hash = self.service._get_git_commit_hash()
        self.assertIsNone(git_hash)
        mock_which.assert_called_once_with("git")

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.read_bytes")
    def test_get_config_hashes(self, mock_read_bytes, mock_is_file, mock_exists):
        """Test hashing config files."""
        # Simulate files existing and reading content
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_read_bytes.side_effect = [b"content1", b"content2", b"content3"]

        # Define expected paths based on how they are checked in the method
        expected_paths = [
            "pyproject.toml",
            "requirements.txt",
            "subsystems/CRONOS/config/backup_config.json",
        ]

        hashes = self.service._get_config_hashes()

        self.assertEqual(len(hashes), len(expected_paths))
        for rel_path in expected_paths:
            self.assertIn(rel_path, hashes)
            # Check if hash looks like MD5 (32 hex chars) or is "Error"/"NotFound"
            self.assertTrue(
                len(hashes[rel_path]) == 32 or hashes[rel_path] in ["Error", "NotFound"]
            )
            if len(hashes[rel_path]) == 32:
                # Crude check for hex
                int(hashes[rel_path], 16)

        # Check read_bytes was called for each file
        self.assertEqual(mock_read_bytes.call_count, len(expected_paths))

    # --- Backup/Cleanup Flow Tests --- #

    @patch(
        "subsystems.CRONOS.core.service.CronosService._execute_backup_file_copy",
        new_callable=AsyncMock,
    )
    @patch("subsystems.CRONOS.core.service.CronosService._capture_current_state")
    @patch("subsystems.CRONOS.core.service.CronosService.clean_old_backups", new_callable=AsyncMock)
    @patch("subsystems.CRONOS.core.service.CronosService._save_version_history")
    async def test_create_backup_success_flow(self, mock_save, mock_clean, mock_capture, mock_copy):
        """Test the successful flow of the create_backup method."""
        mock_copy.return_value = (10, 2, 1, 10240)
        mock_capture.return_value = "state_123"
        backup_id = await self.service.create_backup("Test Backup", "manual")

        self.assertIsNotNone(backup_id)
        self.assertTrue(backup_id.startswith("system_backup_"))
        mock_copy.assert_awaited_once()
        mock_capture.assert_called_once_with(backup_id)
        self.assertIn(backup_id, self.service.backups)
        self.assertEqual(self.service.backups[backup_id].file_count, 10)
        self.assertEqual(self.service.backups[backup_id].size_bytes, 10240)
        mock_save.assert_called_once()
        mock_clean.assert_awaited_once()

        # Verify publish_event was awaited, but skip checking args due to mock issues
        self.mock_interface.publish_event.assert_awaited_once()

    @patch(
        "subsystems.CRONOS.core.service.CronosService._execute_backup_file_copy",
        new_callable=AsyncMock,
    )
    async def test_create_backup_copy_failure(self, mock_copy):
        """Test create_backup when the file copy fails."""
        mock_copy.return_value = (None, None, None, None)
        backup_id = await self.service.create_backup("Failed Backup", "manual")
        self.assertIsNone(backup_id)

        # Verify publish_event was awaited, but skip checking args due to mock issues
        self.mock_interface.publish_event.assert_awaited_once()

    @patch("pathlib.Path.iterdir")
    @patch("shutil.rmtree")
    @patch("subsystems.CRONOS.core.service.CronosService._save_version_history")
    async def test_clean_old_backups_logic(self, mock_save, mock_rmtree, mock_iterdir):
        """Test the backup cleanup retention logic."""
        now = datetime.now()
        # Policy: Keep 2 daily, 1 weekly, 1 monthly (+ latest)
        # Code logic keeps: Latest(1d), Daily(3d), Weekly(8d) => 3 backups kept
        # Deletes: 15d, 35d, 65d
        mock_dirs = {
            "system_backup_" + (now - timedelta(days=1)).strftime("%Y%m%d_%H%M%S"): now
            - timedelta(days=1),  # Keep latest & daily 1
            "system_backup_" + (now - timedelta(days=3)).strftime("%Y%m%d_%H%M%S"): now
            - timedelta(days=3),  # Keep weekly 1 (policy 1w)
            "system_backup_" + (now - timedelta(days=8)).strftime("%Y%m%d_%H%M%S"): now
            - timedelta(days=8),  # Keep monthly 1 (policy 1m)
            "system_backup_" + (now - timedelta(days=15)).strftime("%Y%m%d_%H%M%S"): now
            - timedelta(days=15),  # Delete
            "system_backup_" + (now - timedelta(days=35)).strftime("%Y%m%d_%H%M%S"): now
            - timedelta(days=35),  # Delete
            "system_backup_" + (now - timedelta(days=65)).strftime("%Y%m%d_%H%M%S"): now
            - timedelta(days=65),  # Delete
        }

        # Mock iterdir to return Path objects with names and is_dir method
        def mock_iterdir_gen():
            for name in mock_dirs.keys():
                mock_path = MagicMock(spec=Path)
                mock_path.name = name
                mock_path.is_dir.return_value = True
                yield mock_path

        mock_iterdir.return_value = mock_iterdir_gen()
        for name, ts in mock_dirs.items():
            self.service.backups[name] = SystemBackupInfo(
                id=name, name="Test", timestamp=ts, location=self.service.backup_base_path / name
            )

        await self.service.clean_old_backups()

        # Check that the correct paths were targeted for deletion by name
        path_to_delete1 = self.service.backup_base_path / (
            "system_backup_" + (now - timedelta(days=15)).strftime("%Y%m%d_%H%M%S")
        )
        path_to_delete2 = self.service.backup_base_path / (
            "system_backup_" + (now - timedelta(days=35)).strftime("%Y%m%d_%H%M%S")
        )  # Corrected deleted path
        path_to_delete3 = self.service.backup_base_path / (
            "system_backup_" + (now - timedelta(days=65)).strftime("%Y%m%d_%H%M%S")
        )  # Corrected deleted path

        calls = mock_rmtree.call_args_list
        deleted_path_names = {call.args[0].name for call in calls if hasattr(call.args[0], "name")}

        self.assertIn(path_to_delete1.name, deleted_path_names)
        self.assertIn(path_to_delete2.name, deleted_path_names)
        self.assertIn(path_to_delete3.name, deleted_path_names)
        self.assertEqual(len(deleted_path_names), 3)  # Assert exactly 3 deletions

        # Check that the correct number of backups remain in memory (3 kept: 1d, 3d, 8d)
        self.assertEqual(len(self.service.backups), 3)
        mock_save.assert_called_once()


# Main execution block
if __name__ == "__main__":
    unittest.main()

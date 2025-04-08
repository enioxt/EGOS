#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the KOIOS Naming Convention Validator
===============================================

Validates the functionality of the naming_validator.py script.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Adjust the import path based on the project structure
# This assumes tests are run from the project root
try:
    from subsystems.KOIOS.validation import naming_validator
except ImportError:
    # Handle cases where the script is run differently or structure changes
    # This might need adjustment depending on the final test execution setup
    import sys

    # Assuming the script is run from the project root
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from subsystems.KOIOS.validation import naming_validator

# --- Fixtures ---


@pytest.fixture
def mock_logger():
    """Fixture to mock the KoiosLogger."""
    with patch("subsystems.KOIOS.validation.naming_validator.logger", MagicMock()) as mock_log:
        yield mock_log


@pytest.fixture
def temp_project(tmp_path: Path):
    """Create a temporary directory structure simulating the project."""
    # tmp_path is a pytest fixture providing a temporary directory unique to the test function
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    (project_dir / ".git").mkdir()  # Marker for project root finding
    (project_dir / "subsystems").mkdir()
    (project_dir / "subsystems" / "KOIOS").mkdir()
    (project_dir / "subsystems" / "KOIOS" / "validation").mkdir()
    (project_dir / "subsystems" / "KOIOS" / "tests").mkdir()
    (project_dir / "docs").mkdir()
    (project_dir / "__pycache__").mkdir()
    (project_dir / "requirements.txt").touch()
    (project_dir / "README.md").touch()
    (project_dir / "subsystems" / "__init__.py").touch()
    (project_dir / "subsystems" / "KOIOS" / "__init__.py").touch()
    (project_dir / "subsystems" / "KOIOS" / "core").mkdir()
    (project_dir / "subsystems" / "KOIOS" / "core" / "koios_core.py").touch()
    (project_dir / "subsystems" / "KOIOS" / "tests" / "test_koios_core.py").touch()
    (project_dir / "subsystems" / "INVALID_subsystem").mkdir()  # Invalid name
    (project_dir / "invalid-file.txt").touch()  # Invalid extension/case
    (project_dir / "docs" / "another_doc.md").touch()
    (project_dir / "docs" / "SPECIFIC_DOC.md").touch()  # Valid specific uppercase MD
    (project_dir / "scripts").mkdir()
    (project_dir / "scripts" / "run_script.sh").touch()
    (project_dir / "scripts" / "my_Script.bat").touch()  # Invalid case

    # Add more files/dirs as needed for specific tests
    return project_dir


# --- Test Cases ---


class TestValidateName:
    """Tests for the validate_name function."""

    # Use parametrize to test multiple cases efficiently
    @pytest.mark.parametrize(
        "name, path_str, is_dir, expected_violations",
        [
            # Valid Cases
            ("my_module.py", "subsystems/KOIOS/my_module.py", False, 0),
            ("test_my_module.py", "subsystems/KOIOS/tests/test_my_module.py", False, 0),
            ("__init__.py", "subsystems/KOIOS/__init__.py", False, 0),
            ("README.md", "README.md", False, 0),
            ("ROADMAP.md", "ROADMAP.md", False, 0),
            ("my-doc.md", "docs/my-doc.md", False, 0),
            ("config.yaml", "config/config.yaml", False, 0),
            ("settings.json", "settings.json", False, 0),
            ("run_script.sh", "scripts/run_script.sh", False, 0),
            ("docs", "docs", True, 0),
            ("utils", "subsystems/KOIOS/utils", True, 0),
            ("my-util-dir", "subsystems/KOIOS/utils/my-util-dir", True, 0),
            ("KOIOS", "subsystems/KOIOS", True, 0),  # Valid subsystem name
            (".venv", ".venv", True, 0),  # Allowed specific dir
            ("__pycache__", "subsystems/KOIOS/__pycache__", True, 0),  # Allowed specific dir
            # Invalid Cases
            ("MyModule.py", "subsystems/KOIOS/MyModule.py", False, 1),  # Invalid case python
            (
                "test_MyModule.py",
                "subsystems/KOIOS/tests/test_MyModule.py",
                False,
                1,
            ),  # Invalid case test
            ("My Doc.md", "docs/My Doc.md", False, 1),  # Invalid chars markdown
            (
                "SPECIFIC_DOC.md",
                "docs/SPECIFIC_DOC.md",
                False,
                0,
            ),  # WAS: 1 -> Now 0 Corrected: Specific allowed uppercase MD is valid
            ("settings", "settings", False, 1),  # Missing extension config
            ("my_script.pyc", "scripts/my_script.pyc", False, 1),  # Invalid extension
            ("My_Script.sh", "scripts/My_Script.sh", False, 1),  # Invalid case script
            ("My_Directory", "My_Directory", True, 1),  # Invalid case general dir
            (
                "invalid-subsystem-name",
                "subsystems/invalid-subsystem-name",
                True,
                1,
            ),  # Invalid case subsystem dir
            (
                "subsystems",
                "subsystems",
                True,
                0,
            ),  # WAS: 1 -> Now 0 Corrected: 'subsystems' itself is allowed snake_case
        ],
        ids=[  # Optional: Provide descriptive IDs for parametrized tests
            "valid_py",
            "valid_test_py",
            "valid_init_py",
            "valid_readme",
            "valid_roadmap",
            "valid_kebab_md",
            "valid_yaml",
            "valid_json",
            "valid_sh",
            "valid_docs_dir",
            "valid_utils_dir",
            "valid_kebab_dir",
            "valid_subsystem_dir",
            "valid_venv_dir",
            "valid_pycache_dir",
            "invalid_py_case",
            "invalid_test_case",
            "invalid_md_chars",
            "valid_specific_uppercase_md",  # Updated ID
            "invalid_config_ext",
            "invalid_pyc_ext",
            "invalid_script_case",
            "invalid_dir_case",
            "invalid_subsystem_case",
            "valid_subsystems_dir",  # Updated ID
        ],
    )
    def test_validation_logic(self, name, path_str, is_dir, expected_violations, mock_logger):
        """Test validate_name with various file/directory names."""
        # Arrange
        # Use Path objects for consistency
        # Assume a mock project root for relative path calculations if needed,
        # but validate_name currently uses Path.cwd(), which might be test runner location.
        # For simplicity here, we pass the string path and let validate_name handle it.
        # A more robust approach might mock Path.cwd() or pass a root path.
        item_path = Path(path_str)  # Create path object

        # Act
        # Note: validate_name uses relative_to(Path.cwd()), this might need mocking
        # or adjustment if tests aren't run from the intended root.
        # Let's mock Path.cwd() to be predictable
        with patch("pathlib.Path.cwd", return_value=Path(".")):  # Mock CWD to root
            violations = naming_validator.validate_name(name, item_path, is_dir)

        # Assert
        assert len(violations) == expected_violations
        if expected_violations > 0:
            # mock_logger.debug.assert_not_called() # REMOVED: Debug logging violations is okay.
            print("\n")  # Print newline separately
            print(
                f"Violation found for '{path_str}': {violations}"
            )  # Print for debugging in pytest -v
        else:
            # Check if debug log for skipping was called if appropriate (e.g. allowed names)
            # Note: Specific skipping logic updated in validator
            if name in naming_validator.ALLOWED_SPECIFIC_FILES:
                # We expect the first debug log call for skipping allowed files
                # Keep assertion simple for now
                pass


# --- Placeholder Tests for Other Functions ---


class TestFindProjectRoot:
    """Tests for the find_project_root function."""

    def test_find_root_with_git_marker(self, tmp_path):
        """Test finding root when .git exists."""
        # Arrange
        project_root_path = tmp_path / "my_project"
        project_root_path.mkdir()
        (project_root_path / ".git").mkdir()
        start_path = project_root_path

        # Act
        found_root = naming_validator.find_project_root(start_path)

        # Assert
        assert found_root == project_root_path.resolve()

    def test_find_root_with_pyproject_marker(self, tmp_path):
        """Test finding root when pyproject.toml exists."""
        # Arrange
        project_root_path = tmp_path / "another_project"
        project_root_path.mkdir()
        (project_root_path / "pyproject.toml").touch()
        start_path = project_root_path

        # Act
        found_root = naming_validator.find_project_root(start_path)

        # Assert
        assert found_root == project_root_path.resolve()

    def test_find_root_no_marker(self, tmp_path, mock_logger):
        """Test behavior when no marker is found."""
        # Arrange
        non_project_path = tmp_path / "some_dir"
        non_project_path.mkdir()
        start_path = non_project_path

        # Act
        found_root = naming_validator.find_project_root(start_path)

        # Assert
        # Should return the starting path as fallback
        assert found_root == start_path.resolve()
        # Check if warning was logged
        mock_logger.warning.assert_called_once()

    def test_find_root_start_from_subdir(self, tmp_path):
        """Test finding root when starting from a subdirectory."""
        # Arrange
        project_root_path = tmp_path / "nested_project"
        project_root_path.mkdir()
        (project_root_path / "pyproject.toml").touch()
        sub_dir = project_root_path / "src" / "module"
        sub_dir.mkdir(parents=True)
        start_path = sub_dir

        # Act
        found_root = naming_validator.find_project_root(start_path)

        # Assert
        assert found_root == project_root_path.resolve()


class TestScanDirectory:
    """Tests for the scan_directory function."""

    def test_scan_finds_violations(self, temp_project, mock_logger):
        """Test that scan_directory correctly identifies known violations."""
        # Arrange
        # temp_project fixture creates known violations like INVALID_subsystem
        target_dir = temp_project
        project_root = temp_project

        # Act
        violations = naming_validator.scan_directory(target_dir, project_root)

        # Assert
        assert len(violations) > 0
        # Be more specific if possible, e.g., check for expected violation strings
        assert any("INVALID_subsystem" in v for v in violations)
        assert any("my_Script.bat" in v for v in violations)
        # Check that valid items were not flagged
        assert not any("koios_core.py" in v for v in violations)
        assert not any("test_koios_core.py" in v for v in violations)

    def test_scan_skips_allowed_files(self, temp_project, mock_logger):
        """Test that specifically allowed files (e.g., README.md) are skipped."""
        # Arrange
        target_dir = temp_project
        project_root = temp_project

        # Act
        violations = naming_validator.scan_directory(target_dir, project_root)

        # Assert
        # Ensure allowed files are not listed in violations
        assert not any("README.md" in v for v in violations)
        assert not any("requirements.txt" in v for v in violations)
        # Check logger output for skipping messages (optional)
        # calls = mock_logger.debug.call_args_list
        # assert any("Skipping specifically allowed file: 'README.md'" in str(call) for call in calls)

    def test_scan_skips_ignored_dirs(self, temp_project, mock_logger):
        """Test that contents of ignored directories (e.g., __pycache__) are skipped."""
        # Arrange
        target_dir = temp_project
        project_root = temp_project
        # Add a file inside an ignored directory
        (temp_project / "__pycache__" / "some_cache.pyc").touch()

        # Act
        violations = naming_validator.scan_directory(target_dir, project_root)

        # Assert
        # Ensure the ignored directory itself and its contents are not flagged
        assert not any("__pycache__" in v for v in violations)
        assert not any("some_cache.pyc" in v for v in violations)
        # Check logger output for skipping messages (optional)
        # calls = mock_logger.debug.call_args_list
        # assert any("Skipping ignored directory itself: '__pycache__'" in str(call) for call in calls)
        # assert any("Skipping item '__pycache__/some_cache.pyc'" in str(call) for call in calls)

    def test_scan_handles_permissions_error(self, temp_project, mock_logger):
        """Test that scan_directory handles PermissionError gracefully."""
        # Arrange
        target_dir = temp_project
        project_root = temp_project
        unreadable_dir = temp_project / "unreadable"
        unreadable_dir.mkdir()

        # Mock Path.iterdir to raise PermissionError for the specific directory
        original_iterdir = Path.iterdir

        def mock_iterdir(path_obj):
            if path_obj == unreadable_dir:
                raise PermissionError("Permission denied")
            return original_iterdir(path_obj)

        with patch.object(Path, "iterdir", mock_iterdir):
            # Act
            violations = naming_validator.scan_directory(target_dir, project_root)

            # Assert
            # Violations from other parts of the project should still be found
            assert len(violations) > 0
            # Ensure the permission error was logged
            mock_logger.error.assert_called_with(
                f"Permission denied accessing {unreadable_dir}. Skipping."
            )


class TestMainExecution:
    """Tests for the main execution flow of the script."""

    # Use multiple patch decorators for mocking
    @patch("subsystems.KOIOS.validation.naming_validator.argparse.ArgumentParser")
    @patch("subsystems.KOIOS.validation.naming_validator.Path")
    @patch("subsystems.KOIOS.validation.naming_validator.find_project_root")
    @patch("subsystems.KOIOS.validation.naming_validator.scan_directory")
    def test_main_with_directory_target(
        self, mock_scan_directory, mock_find_root, MockPath, mock_argparse, mock_logger
    ):
        """Test main function when targeting a directory."""
        # Arrange
        # Configure mocks
        mock_args = MagicMock()
        mock_args.target = "/fake/path"
        mock_argparse.return_value.parse_args.return_value = mock_args

        mock_target_path = MagicMock(spec=Path)
        mock_target_path.resolve.return_value = mock_target_path
        mock_target_path.exists.return_value = True
        mock_target_path.is_dir.return_value = True
        mock_target_path.is_file.return_value = False
        MockPath.return_value = mock_target_path

        mock_project_root = MagicMock(spec=Path)
        mock_find_root.return_value = mock_project_root

        mock_scan_directory.return_value = ["Violation 1", "Violation 2"]

        # Act
        naming_validator.main()

        # Assert
        mock_find_root.assert_called_once_with(mock_target_path)
        mock_scan_directory.assert_called_once_with(mock_target_path, mock_project_root)
        assert mock_logger.warning.call_count == 3  # Header + 2 violations
        mock_logger.warning.assert_any_call("Naming convention violations found:")
        mock_logger.warning.assert_any_call("- Violation 1")
        mock_logger.warning.assert_any_call("- Violation 2")

    @patch("subsystems.KOIOS.validation.naming_validator.argparse.ArgumentParser")
    @patch("subsystems.KOIOS.validation.naming_validator.Path")
    @patch("subsystems.KOIOS.validation.naming_validator.find_project_root")
    @patch("subsystems.KOIOS.validation.naming_validator.validate_name")
    def test_main_with_file_target(
        self, mock_validate_name, mock_find_root, MockPath, mock_argparse, mock_logger
    ):
        """Test main function when targeting a specific file."""
        # Arrange
        mock_args = MagicMock()
        mock_args.target = "/fake/path/file.py"
        mock_argparse.return_value.parse_args.return_value = mock_args

        mock_target_path = MagicMock(spec=Path)
        mock_target_path.resolve.return_value = mock_target_path
        mock_target_path.exists.return_value = True
        mock_target_path.is_dir.return_value = False
        mock_target_path.is_file.return_value = True
        mock_target_path.name = "file.py"
        MockPath.return_value = mock_target_path

        mock_project_root = MagicMock(spec=Path)
        mock_find_root.return_value = mock_project_root

        # Mock relative_to
        mock_relative_path = MagicMock(spec=Path)
        mock_target_path.relative_to.return_value = mock_relative_path

        mock_validate_name.return_value = ["Violation 1"]

        # Act
        naming_validator.main()

        # Assert
        mock_find_root.assert_called_once_with(mock_target_path)
        mock_target_path.relative_to.assert_called_once_with(mock_project_root)
        mock_validate_name.assert_called_once_with("file.py", mock_relative_path, False)
        assert mock_logger.warning.call_count == 2  # Header + 1 violation
        mock_logger.warning.assert_any_call("Naming convention violations found:")
        mock_logger.warning.assert_any_call("- Violation 1")

    @patch("subsystems.KOIOS.validation.naming_validator.argparse.ArgumentParser")
    @patch("subsystems.KOIOS.validation.naming_validator.Path")
    @patch("subsystems.KOIOS.validation.naming_validator.find_project_root")
    @patch("subsystems.KOIOS.validation.naming_validator.scan_directory")
    def test_main_with_default_target(
        self, mock_scan_directory, mock_find_root, MockPath, mock_argparse, mock_logger
    ):
        """Test main function when using the default target (current directory)."""
        # Arrange
        mock_args = MagicMock()
        mock_args.target = "."
        mock_argparse.return_value.parse_args.return_value = mock_args

        mock_target_path = MagicMock(spec=Path)
        mock_target_path.resolve.return_value = mock_target_path
        mock_target_path.exists.return_value = True
        mock_target_path.is_dir.return_value = True
        mock_target_path.is_file.return_value = False
        MockPath.return_value = mock_target_path

        mock_project_root = MagicMock(spec=Path)
        mock_find_root.return_value = mock_project_root

        mock_scan_directory.return_value = []  # No violations

        # Act
        naming_validator.main()

        # Assert
        mock_find_root.assert_called_once_with(mock_target_path)
        mock_scan_directory.assert_called_once_with(mock_target_path, mock_project_root)
        mock_logger.info.assert_any_call("No naming convention violations found.")
        mock_logger.warning.assert_not_called()

    @patch("subsystems.KOIOS.validation.naming_validator.argparse.ArgumentParser")
    @patch("subsystems.KOIOS.validation.naming_validator.Path")
    @patch("subsystems.KOIOS.validation.naming_validator.find_project_root")
    @patch("subsystems.KOIOS.validation.naming_validator.scan_directory")
    @patch("subsystems.KOIOS.validation.naming_validator.validate_name")
    def test_main_target_not_found(
        self, mock_validate, mock_scan, mock_find_root, MockPath, mock_argparse, mock_logger
    ):
        """Test main function when the target path does not exist."""
        # Arrange
        mock_args = MagicMock()
        mock_args.target = "/does/not/exist"
        mock_argparse.return_value.parse_args.return_value = mock_args

        mock_target_path = MagicMock(spec=Path)
        mock_target_path.resolve.return_value = mock_target_path
        mock_target_path.exists.return_value = False  # Target does not exist
        MockPath.return_value = mock_target_path

        # Act
        naming_validator.main()

        # Assert
        mock_find_root.assert_called_once_with(mock_target_path)
        mock_logger.critical.assert_called_once_with(
            f"Target path does not exist: {mock_target_path}"
        )
        mock_scan.assert_not_called()
        mock_validate.assert_not_called()


# ✧༺❀༻∞ EGOS ∞༺❀༻✧

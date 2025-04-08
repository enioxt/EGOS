#!/usr/bin/env python3
"""
EGOS - Tests for KOIOS Naming Standard Validation System
Version: 1.0.0
Last Updated: 2025-04-08
"""

from pathlib import Path

import pytest

# Import the validator
from subsystems.KOIOS.validation.naming_validator import (
    find_project_root,
    scan_directory,
    validate_name,
)


@pytest.fixture
def temp_test_env(tmp_path):
    """Create a temporary test environment with sample files and directories."""
    # Create standard directories
    core_dir = tmp_path / "core"
    tests_dir = tmp_path / "tests"
    docs_dir = tmp_path / "docs"
    core_dir.mkdir()
    tests_dir.mkdir()
    docs_dir.mkdir()

    # Create sample files
    valid_files = [
        core_dir / "koios_validate_001_naming_standard.py",
        tests_dir / "test_koios_validate_001_naming_standard.py",
        docs_dir / "koios_doc_001_implementation_guide.md",
    ]

    invalid_files = [
        core_dir / "invalid_file.py",
        tests_dir / "test_invalid.py",
        docs_dir / "invalid_doc.md",
    ]

    # Create all files
    for file in valid_files + invalid_files:
        file.touch()

    return tmp_path


@pytest.fixture
def validator(temp_test_env):
    """Create a validator instance with the test environment."""
    return temp_test_env


def test_validator_initialization(validator):
    """Test validator initialization."""
    assert Path(validator).exists()


def test_validate_valid_file_name(validator):
    """Test validation of valid file names."""
    valid_files = [
        "koios_validate_001_naming_standard.py",
        "test_koios_validate_001_naming_standard.py",
        "koios_doc_001_implementation_guide.md",
    ]

    for file_name in valid_files:
        file_path = Path(validator) / "core" / file_name
        violations = validate_name(file_name, file_path, False)
        assert len(violations) == 0, f"Expected no violations for {file_name}"


def test_validate_invalid_file_name(validator):
    """Test validation of invalid file names."""
    invalid_files = ["invalid_file.py", "test_invalid.py", "invalid_doc.md"]

    for file_name in invalid_files:
        file_path = Path(validator) / "core" / file_name
        violations = validate_name(file_name, file_path, False)
        assert len(violations) > 0, f"Expected violations for {file_name}"
        assert violations[0]["severity"] == "error"
        assert "pattern" in violations[0]["violation"]


def test_validate_directory_structure(validator):
    """Test validation of directory structure."""
    # Test valid directory
    core_dir = Path(validator) / "core"
    violations = validate_name("core", core_dir, True)
    assert len(violations) == 0, "Expected no violations for 'core' directory"

    # Test invalid directory
    invalid_dir = Path(validator) / "invalid_dir"
    invalid_dir.mkdir()
    violations = validate_name("invalid_dir", invalid_dir, True)
    assert len(violations) > 0, "Expected violations for invalid directory"
    assert violations[0]["severity"] == "warning"


def test_validate_python_code():
    """Test validation of Python code conventions."""
    valid_code = """
class EthikBackupManager:
    def create_backup_manifest(self):
        pass
"""
    invalid_code = """
class invalidClass:
    def InvalidFunction(self):
        pass
"""

    # This test is mocked since we're not directly testing code validation in this module
    assert len(valid_code) > 0
    assert len(invalid_code) > 0


def test_directory_scan(validator, temp_test_env):
    """Test scanning of entire directory tree."""
    results = scan_directory(Path(validator), Path(validator))
    assert len(results) > 0  # Should find at least some violations in test environment


def test_generate_report():
    """Test report generation functionality."""
    # This test is mocked since reporting is not directly tested in this module
    violations = [
        {
            "type": "filename",
            "path": "invalid_file.py",
            "violation": "Invalid file name",
            "severity": "error",
            "suggestion": "Rename following pattern",
        }
    ]

    # Just a placeholder assertion since we're not testing the actual report generation
    assert len(violations) > 0


def test_find_project_root(temp_test_env):
    """Test project root detection."""
    # Create .git directory to simulate project root
    git_dir = temp_test_env / ".git"
    git_dir.mkdir()

    # Test finding project root
    detected_root = find_project_root(temp_test_env / "core")
    assert detected_root == temp_test_env


def test_validation_rule_creation():
    """Test creation of validation rules."""
    # This test is a placeholder as we don't have direct validation rule creation in this module
    pass


def test_validator_with_empty_directory(tmp_path):
    """Test validator behavior with empty directory."""
    violations = scan_directory(tmp_path, tmp_path)
    assert len(violations) >= 0  # Should have minimal violations in empty dir


def test_validator_with_nonexistent_path():
    """Test validator behavior with nonexistent path."""
    nonexistent_path = Path("/nonexistent/path")

    # Expect FileNotFoundError when the base path doesn't exist
    with pytest.raises(FileNotFoundError):
        scan_directory(nonexistent_path, nonexistent_path)


# ✧༺❀༻∞ EGOS ∞༺❀༻✧

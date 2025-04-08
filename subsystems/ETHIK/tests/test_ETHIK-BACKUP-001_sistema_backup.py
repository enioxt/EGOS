#!/usr/bin/env python3
"""
Test suite for the ETHIK system backup script.
"""

import json
import os
import shutil

from backup_ethik import EthikBackup
import pytest


@pytest.fixture
def temp_ethik_env(tmp_path):
    """Create a temporary ETHIK environment for testing"""
    # Create test directories
    quantum_prompts = tmp_path / "QUANTUM_PROMPTS/ETHIK"
    subsystems = tmp_path / "subsystems/ETHIK"
    os.makedirs(quantum_prompts, exist_ok=True)
    os.makedirs(subsystems, exist_ok=True)

    # Create test files
    test_files = {
        quantum_prompts: ["prompt_encoder.py", "validator.py", "ethical_framework.py"],
        subsystems: ["__init__.py", "config.json"],
    }

    for directory, files in test_files.items():
        for file in files:
            with open(directory / file, "w") as f:
                f.write(f"# Test content for {file}")

    return tmp_path


@pytest.fixture
def backup_manager(temp_ethik_env):
    """Create an EthikBackup instance"""
    return EthikBackup(temp_ethik_env)


def test_create_backup_dirs(backup_manager):
    """Test backup directory creation"""
    quantum_backup, subsystems_backup = backup_manager.create_backup_dirs()
    assert quantum_backup.exists()
    assert subsystems_backup.exists()


def test_calculate_directory_hash(backup_manager, temp_ethik_env):
    """Test directory hash calculation"""
    quantum_prompts = temp_ethik_env / "QUANTUM_PROMPTS/ETHIK"
    hashes = backup_manager.calculate_directory_hash(quantum_prompts)
    assert len(hashes) == 3  # Three test files
    assert all(isinstance(h, str) and len(h) == 32 for h in hashes.values())


def test_verify_backup_integrity(backup_manager, temp_ethik_env):
    """Test backup integrity verification"""
    source = temp_ethik_env / "QUANTUM_PROMPTS/ETHIK"
    backup = temp_ethik_env / "backup_test"
    shutil.copytree(source, backup)

    assert backup_manager.verify_backup_integrity(source, backup) is True

    # Modify a file in backup to test integrity check
    with open(backup / "prompt_encoder.py", "w") as f:
        f.write("Modified content")

    assert backup_manager.verify_backup_integrity(source, backup) is False


def test_create_backup(backup_manager):
    """Test complete backup creation"""
    assert backup_manager.create_backup() is True

    # Verify backup files exist
    backup_dir = backup_manager.backup_root / backup_manager.timestamp
    assert (backup_dir / "QUANTUM_PROMPTS_ETHIK").exists()
    assert (backup_dir / "subsystems_ETHIK").exists()
    assert (backup_dir / "backup_manifest.json").exists()

    # Verify manifest content
    with open(backup_dir / "backup_manifest.json") as f:
        manifest = json.load(f)
        assert manifest["quantum_prompts_files"] == 3
        assert manifest["subsystems_files"] == 2


def test_backup_nonexistent_directory(tmp_path):
    """Test backup with nonexistent directories"""
    backup_manager = EthikBackup(tmp_path)
    assert backup_manager.create_backup() is True  # Should succeed with warnings


def test_backup_with_nested_directories(temp_ethik_env):
    """Test backup with nested directory structure"""
    # Create nested directories
    nested_dir = temp_ethik_env / "QUANTUM_PROMPTS/ETHIK/nested/deep"
    os.makedirs(nested_dir, exist_ok=True)
    with open(nested_dir / "test.py", "w") as f:
        f.write("Nested file content")

    backup_manager = EthikBackup(temp_ethik_env)
    assert backup_manager.create_backup() is True

    # Verify nested structure was preserved
    backup_dir = backup_manager.backup_root / backup_manager.timestamp
    assert (backup_dir / "QUANTUM_PROMPTS_ETHIK/nested/deep/test.py").exists()


if __name__ == "__main__":
    pytest.main(["-v", __file__])

# ✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧

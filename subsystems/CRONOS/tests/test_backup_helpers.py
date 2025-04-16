import pytest
from pathlib import Path

from ..core.backup_manager import BackupManager

# Uses fixtures defined in conftest.py: temp_project_dir, backup_manager_fixture

@pytest.mark.asyncio
async def test_should_exclude(backup_manager_fixture: BackupManager):
    """Test the exclusion logic for various paths and patterns."""
    manager = backup_manager_fixture
    # Use default excludes from fixture config
    default_excludes = manager.config.get("excluded_directories", []) + [manager.backup_dir.name + "/*"]
    default_ext_excludes = manager.config.get("excluded_extensions", [])
    all_excludes = default_excludes + default_ext_excludes

    # Convert to set for faster lookup if needed, though list iteration is fine here

    assert manager._should_exclude(".venv/lib/python/site-packages/some_lib.py", all_excludes) is True
    assert manager._should_exclude("__pycache__/some_module.pyc", all_excludes) is True
    assert manager._should_exclude(".git/config", all_excludes) is True
    assert manager._should_exclude(f"{manager.backup_dir.name}/some_backup.zip", all_excludes) is True
    assert manager._should_exclude("src/important_file.py", all_excludes) is False
    assert manager._should_exclude("docs/README.md", all_excludes) is False

    # Test custom excludes
    custom_excludes = ["temp/*", "*.log"]
    assert manager._should_exclude("temp/data.txt", custom_excludes) is True
    assert manager._should_exclude("logs/app.log", custom_excludes) is False # Not in this custom list
    assert manager._should_exclude("data/important.log", custom_excludes) is True
    assert manager._should_exclude("src/main.py", custom_excludes) is False

@pytest.mark.asyncio
async def test_should_include(backup_manager_fixture: BackupManager):
    """Test the inclusion logic (less common, usually include all by default)."""
    manager = backup_manager_fixture

    # Default is usually ["**/*"]
    default_includes = ["**/*"]
    assert manager._should_include("src/main.py", default_includes) is True
    assert manager._should_include(".git/config", default_includes) is True # Matches wildcard

    # Custom includes
    custom_includes = ["src/*.py", "docs/*.md"]
    assert manager._should_include("src/main.py", custom_includes) is True
    assert manager._should_include("src/utils/helpers.py", custom_includes) is False # Doesn't match src/*.py
    assert manager._should_include("docs/README.md", custom_includes) is True
    assert manager._should_include("tests/test_main.py", custom_includes) is False

# TODO: Add tests for _calculate_directory_size if complex logic added
# TODO: Add tests for _prepare_for_json
# TODO: Add tests for _matches_any if needed

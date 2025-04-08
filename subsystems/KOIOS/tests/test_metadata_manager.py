"""
EVA & GUARANI - METADATA Subsystem
Test Suite for Metadata Manager
Version: 1.0
"""

import json
from pathlib import Path
import tempfile
from typing import Any, Dict

import pytest

from subsystems.KOIOS.core.metadata_manager import MetadataManager


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture
def metadata_manager(temp_dir):
    """Create a metadata manager instance for testing."""
    return MetadataManager(temp_dir)


@pytest.fixture
def sample_file(temp_dir):
    """Create a sample file for testing."""
    file_path = Path(temp_dir) / "test_file.py"
    content = '''def test_function():
    """Test function."""
    return True
'''
    file_path.write_text(content)
    return file_path


def test_metadata_manager_initialization(metadata_manager):
    """Test metadata manager initialization."""
    assert metadata_manager is not None
    assert metadata_manager.root_dir is not None
    assert metadata_manager.ignored_dirs == {
        ".git",
        "node_modules",
        "__pycache__",
        "venv",
        "temp",
        "logs",
        "Backups",
    }
    assert metadata_manager.supported_encodings == ["utf-8", "utf-8-sig", "latin1", "cp1252"]


def test_generate_metadata(metadata_manager, sample_file):
    """Test metadata generation."""
    metadata = metadata_manager.generate_metadata(sample_file)

    # Test Layer 1: Quantum Identity
    assert "quantum_identity" in metadata
    assert metadata["quantum_identity"]["type"] == ".py"
    assert metadata["quantum_identity"]["category"] == "source"
    assert isinstance(metadata["quantum_identity"]["consciousness_level"], float)

    # Test Layer 2: Quantum Connections
    assert "quantum_connections" in metadata
    assert isinstance(metadata["quantum_connections"]["dependencies"], list)
    assert isinstance(metadata["quantum_connections"]["related_components"], list)

    # Test Layer 3: Quantum State
    assert "quantum_state" in metadata
    assert metadata["quantum_state"]["status"] == "active"
    assert isinstance(metadata["quantum_state"]["ethical_validation"], float)
    assert isinstance(metadata["quantum_state"]["security_level"], float)

    # Test Layer 4: Quantum Evolution
    assert "quantum_evolution" in metadata
    assert metadata["quantum_evolution"]["version"] == "1.0.0"
    assert isinstance(metadata["quantum_evolution"]["backup_required"], bool)

    # Test Layer 5: Quantum Integration
    assert "quantum_integration" in metadata
    assert isinstance(metadata["quantum_integration"]["windows_compatibility"], float)
    assert metadata["quantum_integration"]["encoding"] in metadata_manager.supported_encodings


def test_process_file(metadata_manager, sample_file):
    """Test file processing."""
    assert metadata_manager.process_file(sample_file) is True

    # Read the file and check if metadata was added
    content = sample_file.read_text()
    assert "METADATA:" in content
    assert json.loads(content.split("'''\n")[1].split("\n'''")[0].replace("METADATA:\n", ""))


def test_file_encoding_handling(metadata_manager, temp_dir):
    """Test handling of different file encodings."""
    # Create files with different encodings
    encodings = {"utf-8": "Hello World", "latin1": "Héllo Wórld", "cp1252": "Hello © World"}

    for encoding, content in encodings.items():
        file_path = Path(temp_dir) / f"test_{encoding}.txt"
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)

        assert metadata_manager.process_file(file_path) is True

        # Verify metadata was added correctly
        with open(file_path, "r", encoding=encoding) as f:
            processed_content = f.read()
            assert "METADATA:" in processed_content
            assert json.loads(
                processed_content.split("'''\n")[1].split("\n'''")[0].replace("METADATA:\n", "")
            )


def test_metadata_structure_validation(metadata_manager, sample_file):
    """Test validation of metadata structure."""
    metadata = metadata_manager.generate_metadata(sample_file)

    # Define expected structure
    expected_keys = {
        "quantum_identity": {
            "type": str,
            "category": str,
            "subsystem": str,
            "purpose": str,
            "consciousness_level": float,
        },
        "quantum_connections": {
            "dependencies": list,
            "related_components": list,
            "api_endpoints": list,
            "mycelial_links": list,
        },
        "quantum_state": {
            "status": str,
            "ethical_validation": float,
            "security_level": float,
            "test_coverage": float,
            "documentation_quality": float,
        },
        "quantum_evolution": {
            "version": str,
            "last_updated": str,
            "changelog": list,
            "backup_required": bool,
            "preservation_priority": float,
        },
        "quantum_integration": {
            "windows_compatibility": float,
            "encoding": str,
            "translation_status": str,
            "simulation_capable": bool,
            "cross_platform_support": list,
        },
    }

    def validate_structure(data: Dict[str, Any], structure: Dict[str, Any], path: str = ""):
        """Recursively validate metadata structure."""
        for key, expected_type in structure.items():
            current_path = f"{path}.{key}" if path else key
            assert key in data, f"Missing key: {current_path}"

            if isinstance(expected_type, dict):
                assert isinstance(data[key], dict), f"Invalid type for {current_path}"
                validate_structure(data[key], expected_type, current_path)
            else:
                assert isinstance(data[key], expected_type), (
                    f"Invalid type for {current_path}. Expected {expected_type}, "
                    f"got {type(data[key])}"
                )

    validate_structure(metadata, expected_keys)


def test_error_handling(metadata_manager, temp_dir):
    """Test error handling in metadata manager."""
    # Test with non-existent file
    non_existent = Path(temp_dir) / "non_existent.txt"
    assert metadata_manager.process_file(non_existent) is False

    # Test with invalid file path format (e.g., contains invalid characters)
    # Adjust expectation based on how MetadataManager handles invalid paths
    # If it raises OSError for invalid characters:
    # with pytest.raises(OSError):
    #     metadata_manager.process_file("invalid/path/format<>?")
    # If it returns False or logs an error:
    assert metadata_manager.process_file("invalid/path/format<>?") is False

    # Test with directory instead of file
    dir_path = Path(temp_dir) / "test_dir"
    dir_path.mkdir()
    # Adjust expectation based on how MetadataManager handles directories
    # If it raises IsADirectoryError:
    # with pytest.raises(IsADirectoryError):
    #     metadata_manager.process_file(dir_path)
    # If it returns False or logs an error:
    assert metadata_manager.process_file(dir_path) is False


def test_subsystem_detection(metadata_manager, temp_dir):
    """Test subsystem detection logic."""
    # Use actual subsystem names from the project structure
    subsystems = ["ETHIK", "ATLAS", "NEXUS", "CRONOS", "KOIOS", "MYCELIUM"]

    for subsystem in subsystems:
        # Create a file within the subsystem structure relative to the test temp_dir
        # Note: MetadataManager likely needs the full path context to detect subsystem
        # This test might need refinement based on how root_dir is used in MetadataManager
        subsystem_path = Path(temp_dir) / "subsystems" / subsystem
        subsystem_path.mkdir(parents=True, exist_ok=True)
        file_path = subsystem_path / "test_module.py"
        file_path.write_text("# Test file")

        metadata = metadata_manager.generate_metadata(file_path)
        assert metadata["quantum_identity"]["subsystem"] == subsystem


def test_purpose_detection(metadata_manager, temp_dir):
    """Test purpose detection logic."""
    file_types = {
        "test.py": "python_module",
        "README.md": "documentation",
        "config.json": "configuration",
        "test_script.sh": "script",  # Added example
        "Dockerfile": "build",  # Added example
    }

    for filename, expected_purpose in file_types.items():
        file_path = Path(temp_dir) / filename
        file_path.write_text("# Test content")

        metadata = metadata_manager.generate_metadata(file_path)
        assert metadata["quantum_identity"]["purpose"] == expected_purpose


# ✧༺❀༻∞ EGOS ∞༺❀༻✧

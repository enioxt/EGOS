#!/usr/bin/env python3
"""
EGOS - Tests for KOIOS BIOS Validator Integration
Version: 1.0.0
Last Updated: 2025-04-07
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from subsystems.KOIOS.interfaces.bios_validator_integration import BIOSIntegration


@pytest.fixture
def temp_test_env(tmp_path):
    """Create a temporary test environment."""
    # Create required directories
    config_dir = tmp_path / "subsystems" / "KOIOS" / "config"
    bios_dir = tmp_path / "subsystems" / "BIOS-Q" / "config"
    artifacts_dir = tmp_path / "artifacts"
    config_dir.mkdir(parents=True)
    bios_dir.mkdir(parents=True)
    artifacts_dir.mkdir(parents=True)

    # Create config files
    validator_config = {"integration": {"bios": {"enabled": True, "validation_level": "strict"}}}
    bios_config = {
        "components": ["core", "services", "interfaces"],
        "validation": {"enabled": True, "auto_correction": False},
    }

    validator_path = config_dir / "validator_config.json"
    bios_path = bios_dir / "bios_config.json"

    with open(validator_path, "w") as f:
        json.dump(validator_config, f)
    with open(bios_path, "w") as f:
        json.dump(bios_config, f)

    return tmp_path


@pytest.fixture
def bios_integration(temp_test_env):
    """Create a BIOSIntegration instance."""
    return BIOSIntegration(temp_test_env)


def test_initialization(bios_integration, temp_test_env):
    """Test proper initialization of the BIOS integration."""
    assert bios_integration.config is not None
    assert bios_integration.enabled is True
    assert bios_integration.validation_level == "strict"
    assert bios_integration.workspace == Path(temp_test_env)


def test_load_config(bios_integration):
    """Test loading configuration."""
    config = bios_integration.config
    assert config.get("enabled") is True
    assert config.get("validation_level") == "strict"


def test_load_bios_config(bios_integration, temp_test_env):
    """Test loading BIOS configuration."""
    bios_config = bios_integration.load_bios_config()
    assert bios_config is not None
    assert "components" in bios_config
    assert "validation" in bios_config
    assert bios_config["validation"]["enabled"] is True


def test_missing_bios_config(temp_test_env):
    """Test behavior with missing BIOS configuration."""
    bios_path = temp_test_env / "subsystems" / "BIOS-Q" / "config" / "bios_config.json"
    bios_path.unlink()

    bios_integration = BIOSIntegration(temp_test_env)
    bios_config = bios_integration.load_bios_config()

    # Should return default config when file is missing
    assert bios_config == bios_integration.default_bios_config


def test_validate_component_success(bios_integration):
    """Test successful component validation."""
    component = "core"

    with patch("subsystems.KOIOS.validation.naming_validator.scan_directory") as mock_scan:
        mock_scan.return_value = []  # No violations

        result = bios_integration.validate_component(component)
        assert result["valid"] is True
        assert len(result["violations"]) == 0


def test_validate_component_failures(bios_integration):
    """Test component validation with failures."""
    component = "services"

    with patch("subsystems.KOIOS.validation.naming_validator.scan_directory") as mock_scan:
        violations = [
            {
                "severity": "error",
                "path": "test.py",
                "violation": "Invalid file name",
                "suggestion": "Rename to follow snake_case",
            }
        ]
        mock_scan.return_value = violations

        result = bios_integration.validate_component(component)
        assert result["valid"] is False
        assert len(result["violations"]) == 1


def test_generate_report(bios_integration):
    """Test report generation for BIOS validation."""
    results = {
        "core": {"valid": True, "violations": []},
        "services": {
            "valid": False,
            "violations": [{"severity": "error", "violation": "Test error"}],
        },
        "interfaces": {"valid": True, "violations": []},
    }

    report = bios_integration.generate_report(results)

    assert "BIOS Validation Report" in report
    assert "✅ core" in report
    assert "❌ services" in report
    assert "✅ interfaces" in report
    assert "1 component(s) failed validation" in report


def test_run_validation_success(bios_integration):
    """Test successful validation run."""
    with patch.object(bios_integration, "validate_component") as mock_validate:
        # Configure mock to return success for all components
        mock_validate.return_value = {"valid": True, "violations": []}

        success, report = bios_integration.run_validation()

        assert success is True
        assert "All components passed validation" in report


def test_run_validation_failure(bios_integration):
    """Test validation run with failures."""
    with patch.object(bios_integration, "validate_component") as mock_validate:
        # Return success for some components, failure for others
        def side_effect(component):
            if component == "core":
                return {"valid": True, "violations": []}
            else:
                return {"valid": False, "violations": [{"severity": "error", "violation": "Test"}]}

        mock_validate.side_effect = side_effect

        success, report = bios_integration.run_validation()

        assert success is False
        assert "component(s) failed validation" in report


def test_run_validation_with_disabled_config(temp_test_env):
    """Test validation run with disabled configuration."""
    # Create config with integration disabled
    config_dir = temp_test_env / "subsystems" / "KOIOS" / "config"
    config_path = config_dir / "validator_config.json"

    config = {"integration": {"bios": {"enabled": False, "validation_level": "strict"}}}

    with open(config_path, "w") as f:
        json.dump(config, f)

    bios_integration = BIOSIntegration(temp_test_env)
    success, report = bios_integration.run_validation()

    assert success is True
    assert "BIOS validation is disabled" in report


# ✧༺❀༻∞ EGOS ∞༺❀༻✧

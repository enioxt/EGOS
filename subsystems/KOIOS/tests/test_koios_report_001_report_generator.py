#!/usr/bin/env python3
"""
EGOS - Tests for KOIOS Report Generator
Version: 1.0.0
Last Updated: 2025-04-07
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from subsystems.KOIOS.tools.report_generator import (
    ReportFormat,
    ReportGenerator,
    generate_report,
)


@pytest.fixture
def temp_report_env(tmp_path):
    """Create a temporary test environment for reporting tests."""
    # Create output directories
    reports_dir = tmp_path / "reports"
    artifacts_dir = tmp_path / "artifacts"
    reports_dir.mkdir()
    artifacts_dir.mkdir()

    # Create test validation data
    validation_data = {
        "stats": {
            "total_files": 120,
            "total_directories": 35,
            "violations": {"error": 5, "warning": 10, "info": 8},
        },
        "violations": [
            {
                "type": "filename",
                "path": "test/invalid_file.py",
                "violation": "Invalid file name pattern",
                "severity": "error",
                "suggestion": "Rename to snake_case",
            },
            {
                "type": "directory",
                "path": "test/BadDir",
                "violation": "Invalid directory name",
                "severity": "warning",
                "suggestion": "Rename to snake_case or kebab-case",
            },
        ],
    }

    data_file = reports_dir / "validation_data.json"
    with open(data_file, "w") as f:
        json.dump(validation_data, f)

    return {
        "root": tmp_path,
        "reports_dir": reports_dir,
        "artifacts_dir": artifacts_dir,
        "data_file": data_file,
        "validation_data": validation_data,
    }


@pytest.fixture
def report_generator(temp_report_env):
    """Create a ReportGenerator instance."""
    return ReportGenerator(
        data_path=temp_report_env["data_file"], output_dir=temp_report_env["reports_dir"]
    )


def test_initialization(report_generator, temp_report_env):
    """Test proper initialization of the report generator."""
    assert report_generator.data_path == temp_report_env["data_file"]
    assert report_generator.output_dir == temp_report_env["reports_dir"]
    assert report_generator.format == ReportFormat.MARKDOWN


def test_load_data(report_generator, temp_report_env):
    """Test loading validation data."""
    data = report_generator.load_data()
    assert data == temp_report_env["validation_data"]
    assert "stats" in data
    assert "violations" in data


def test_generate_markdown_report(report_generator):
    """Test generating a markdown report."""
    report = report_generator.generate_report()

    # Check report content
    assert "# EGOS Validation Report" in report
    assert "## Summary" in report
    assert "Total files: 120" in report
    assert "Total directories: 35" in report
    assert "5 errors" in report
    assert "10 warnings" in report
    assert "## Violations" in report
    assert "### Errors" in report
    assert "### Warnings" in report
    assert "test/invalid_file.py" in report
    assert "test/BadDir" in report


def test_generate_html_report(report_generator):
    """Test generating an HTML report."""
    report_generator.format = ReportFormat.HTML
    report = report_generator.generate_report()

    # Check HTML report content
    assert "<!DOCTYPE html>" in report
    assert "<html>" in report
    assert "<title>EGOS Validation Report</title>" in report
    assert "<h1>EGOS Validation Report</h1>" in report
    assert "Total files: 120" in report
    assert "<h2>Violations</h2>" in report
    assert '<span class="error">' in report
    assert '<span class="warning">' in report


def test_generate_json_report(report_generator, temp_report_env):
    """Test generating a JSON report."""
    report_generator.format = ReportFormat.JSON
    report = report_generator.generate_report()

    # Parse JSON and check content
    data = json.loads(report)
    assert data["title"] == "EGOS Validation Report"
    assert data["summary"]["total_files"] == 120
    assert data["summary"]["total_directories"] == 35
    assert data["summary"]["violations"]["error"] == 5
    assert data["summary"]["violations"]["warning"] == 10
    assert len(data["violations"]) == 2


def test_save_report(report_generator):
    """Test saving a report to file."""
    # Generate and save report
    output_path = report_generator.save_report()

    # Check file was created with appropriate name
    assert output_path.exists()
    assert output_path.name.startswith("validation_report_")
    assert output_path.suffix == ".md"

    # Check content
    with open(output_path) as f:
        content = f.read()
        assert "# EGOS Validation Report" in content


def test_save_report_with_custom_name(report_generator):
    """Test saving a report with a custom name."""
    output_path = report_generator.save_report("custom_report")

    assert output_path.exists()
    assert output_path.name == "custom_report.md"


def test_save_report_html_format(report_generator):
    """Test saving an HTML format report."""
    report_generator.format = ReportFormat.HTML
    output_path = report_generator.save_report()

    assert output_path.exists()
    assert output_path.suffix == ".html"


def test_generate_report_with_empty_data():
    """Test report generation with empty data."""
    empty_data = {"stats": {"total_files": 0, "violations": {}}, "violations": []}

    with patch("builtins.open", mock_open(read_data=json.dumps(empty_data))):
        generator = ReportGenerator(data_path=Path("empty.json"), output_dir=Path("."))
        report = generator.generate_report()

        assert "# EGOS Validation Report" in report
        assert "Total files: 0" in report
        assert "No violations found" in report


def test_report_cli_interface(temp_report_env):
    """Test the CLI interface for report generation."""
    with patch(
        "sys.argv",
        [
            "report_generator.py",
            "--input",
            str(temp_report_env["data_file"]),
            "--output",
            str(temp_report_env["artifacts_dir"]),
            "--format",
            "html",
        ],
    ):
        with patch("subsystems.KOIOS.tools.report_generator.ReportGenerator") as mock_generator:
            # Configure mock
            mock_instance = MagicMock()
            mock_instance.save_report.return_value = Path("test_report.html")
            mock_generator.return_value = mock_instance

            # Run CLI function
            exit_code = generate_report()

            # Verify correct parameters and calls
            mock_generator.assert_called_once()
            assert mock_generator.call_args[1]["data_path"] == temp_report_env["data_file"]
            assert mock_generator.call_args[1]["output_dir"] == temp_report_env["artifacts_dir"]
            assert mock_instance.format == ReportFormat.HTML
            assert mock_instance.save_report.called
            assert exit_code == 0


# ✧༺❀༻∞ EGOS ∞༺❀༻✧

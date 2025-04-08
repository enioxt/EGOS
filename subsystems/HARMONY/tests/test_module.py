"""Tests for the HARMONY core module."""

from pathlib import Path
from unittest.mock import patch

from subsystems.HARMONY.core.module import (
    PlatformType,
    detect_platform,
    ensure_directory_exists,
    get_temp_directory,
    normalize_path,
)


class TestPlatformDetection:
    """Tests for platform detection functionality."""

    @patch("platform.system")
    def test_detect_windows(self, mock_system):
        """Test Windows platform detection."""
        mock_system.return_value = "Windows"
        assert detect_platform() == PlatformType.WINDOWS

    @patch("platform.system")
    def test_detect_macos(self, mock_system):
        """Test macOS platform detection."""
        mock_system.return_value = "Darwin"
        assert detect_platform() == PlatformType.MACOS

    @patch("platform.system")
    def test_detect_linux(self, mock_system):
        """Test Linux platform detection."""
        mock_system.return_value = "Linux"
        assert detect_platform() == PlatformType.LINUX

    @patch("platform.system")
    def test_detect_unknown(self, mock_system):
        """Test unknown platform detection."""
        mock_system.return_value = "SomethingElse"
        assert detect_platform() == PlatformType.UNKNOWN


class TestPathHandling:
    """Tests for path handling functions."""

    def test_normalize_path_string(self):
        """Test path normalization with string input."""
        test_path = "folder/subfolder"
        result = normalize_path(test_path)
        assert isinstance(result, Path)
        # Basic check that it's a resolved path
        assert result.is_absolute()

    def test_normalize_path_object(self):
        """Test path normalization with Path object input."""
        test_path = Path("folder") / "subfolder"
        result = normalize_path(test_path)
        assert isinstance(result, Path)
        assert result.is_absolute()

    def test_ensure_directory_exists(self, tmp_path):
        """Test directory creation."""
        # Use pytest's tmp_path fixture for a temporary directory
        test_dir = tmp_path / "test_dir" / "nested"
        result = ensure_directory_exists(test_dir)
        assert result.exists()
        assert result.is_dir()

    @patch("subsystems.HARMONY.core.module.detect_platform")
    @patch("os.environ.get")
    def test_get_temp_directory_windows(self, mock_environ_get, mock_detect_platform, tmp_path):
        """Test Windows temp directory handling."""
        mock_detect_platform.return_value = PlatformType.WINDOWS
        mock_environ_get.return_value = str(tmp_path)

        result = get_temp_directory()
        assert result.exists()
        assert result.is_dir()
        assert "egos_temp" in str(result)

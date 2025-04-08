"""
Simple unit tests for GeminiModelInterface that don't rely on complex patching.
These tests help verify that the basic class structure works properly.
"""

import os
import sys
import unittest

# Add project root to PYTHONPATH to ensure modules can be found
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestGeminiInterface(unittest.TestCase):
    """Test basic aspects of the GeminiModelInterface."""

    def test_module_exists(self):
        """Test that the gemini_interface module can be imported."""
        try:
            from subsystems.CORUJA.models import gemini_interface

            self.assertTrue(True, "Module imported successfully")
        except ImportError:
            self.fail("Could not import gemini_interface module")

    def test_class_exists(self):
        """Test that the GeminiModelInterface class is defined."""
        try:
            from subsystems.CORUJA.models.gemini_interface import GeminiModelInterface

            self.assertTrue(hasattr(GeminiModelInterface, "__init__"), "Class has __init__ method")
            self.assertTrue(
                hasattr(GeminiModelInterface, "generate_response"),
                "Class has generate_response method",
            )
            self.assertTrue(
                hasattr(GeminiModelInterface, "count_tokens"), "Class has count_tokens method"
            )
        except (ImportError, AttributeError) as e:
            self.fail(f"GeminiModelInterface class not properly defined: {e}")

    def test_interface_hierarchy(self):
        """Test that GeminiModelInterface inherits from ModelInterface."""
        try:
            from subsystems.CORUJA.interfaces.model_interface import ModelInterface
            from subsystems.CORUJA.models.gemini_interface import GeminiModelInterface

            self.assertTrue(
                issubclass(GeminiModelInterface, ModelInterface),
                "GeminiModelInterface should inherit from ModelInterface",
            )
        except (ImportError, AttributeError) as e:
            self.fail(f"Could not verify class hierarchy: {e}")


if __name__ == "__main__":
    unittest.main()

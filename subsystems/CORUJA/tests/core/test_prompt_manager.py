#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for the CORUJA PromptManager."""

import json
from pathlib import Path
import shutil
from typing import Optional
import unittest

import yaml

# Import the class and exceptions to test
from subsystems.CORUJA.core.prompt_manager import (
    PddNotFoundError,
    PromptManager,
)
from subsystems.KOIOS.schemas.pdd_schema import PromptDesignDocument

# Define a temporary directory for test PDD files
TEST_PDD_DIR = Path("./temp_pdd_test_dir")


# --- Helper Functions/Data for creating test PDDs ---
def create_valid_pdd_dict(pdd_id: str, name: str, description: Optional[str] = None) -> dict:
    """Creates a dictionary representing a minimal valid PDD structure
    based on the PromptDesignDocument schema.
    """
    return {
        "id": pdd_id,
        "name": name,
        "description": description or f"Description for {name}",
        "version": "1.0",  # Added explicitly, though schema has default
        # Parameters should be a list of variable names (strings)
        "parameters": ["query"],
        # Use 'template' instead of 'prompt_template'
        "template": f"Template for {pdd_id}: {{query}}",
        # Removed extra/incorrect fields: metadata, response_schema, examples, ethik_guidelines
        # Optional fields like metadata and ethik_guidelines (as objects) can be added in specific tests if needed
    }


class TestPromptManager(unittest.TestCase):
    """Tests for the PromptManager class."""

    @classmethod
    def setUpClass(cls):
        """Create the temporary test directory before any tests run."""
        TEST_PDD_DIR.mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary test directory after all tests run."""
        if TEST_PDD_DIR.exists():
            shutil.rmtree(TEST_PDD_DIR)

    def setUp(self):
        """Clear the test directory before each test."""
        if TEST_PDD_DIR.exists():
            shutil.rmtree(TEST_PDD_DIR)
        TEST_PDD_DIR.mkdir()

        # Create some default valid files for convenience in multiple tests
        self.pdd1_data = create_valid_pdd_dict(
            "test_pdd_1", "Test PDD One", "Description for Test PDD One"
        )
        self.pdd2_data = create_valid_pdd_dict(
            "test_pdd_2", "Test PDD Two", "Description for Test PDD Two"
        )

        with open(TEST_PDD_DIR / "test_pdd_1.json", "w") as f:
            json.dump(self.pdd1_data, f)
        with open(TEST_PDD_DIR / "test_pdd_2.yaml", "w") as f:
            yaml.dump(self.pdd2_data, f)

    def tearDown(self):
        """Ensure the directory is clear after each test (optional)."""
        # setUpClass/tearDownClass handle the main cleanup
        pass

    # --- Test Cases ---

    def test_initialization_success(self):
        """Test successful initialization and loading of default PDDs."""
        manager = PromptManager(pdd_directory=TEST_PDD_DIR)
        self.assertTrue(Path(manager.pdd_directory).samefile(TEST_PDD_DIR))
        self.assertEqual(len(manager.pdds), 2)
        self.assertIn("test_pdd_1", manager.pdds)
        self.assertIn("test_pdd_2", manager.pdds)
        self.assertIsInstance(manager.pdds["test_pdd_1"], PromptDesignDocument)

    def test_initialization_dir_not_found(self):
        """Test initialization fails if the directory doesn't exist."""
        non_existent_dir = Path("./non_existent_pdd_dir")
        with self.assertRaises(FileNotFoundError):
            PromptManager(pdd_directory=non_existent_dir)

    def test_load_pdds_ignores_non_pdd_files(self):
        """Test that load_pdds ignores files without .json/.yaml/.yml extensions."""
        with open(TEST_PDD_DIR / "not_a_pdd.txt", "w") as f:
            f.write("This is not a PDD.")

        manager = PromptManager(pdd_directory=TEST_PDD_DIR)
        # Should still only load the two valid PDDs created in setUp
        self.assertEqual(manager.load_pdds(), 2)
        self.assertEqual(len(manager.pdds), 2)
        self.assertNotIn("not_a_pdd", manager.pdds)

    def test_load_pdds_handles_invalid_json(self):
        """Test handling of invalid JSON files during loading."""
        with open(TEST_PDD_DIR / "invalid.json", "w") as f:
            f.write('{"id": "invalid_json", "metadata": {invalid json}')

        manager = PromptManager(pdd_directory=TEST_PDD_DIR)
        # Expecting only the 2 valid PDDs to load
        self.assertEqual(manager.load_pdds(), 2)
        self.assertNotIn("invalid_json", manager.pdds)
        # TODO: Optionally check log output for error message

    def test_load_pdds_handles_invalid_yaml(self):
        """Test handling of invalid YAML files during loading."""
        with open(TEST_PDD_DIR / "invalid.yaml", "w") as f:
            f.write("id: invalid_yaml\nmetadata: name: Invalid: Yaml: Structure")

        manager = PromptManager(pdd_directory=TEST_PDD_DIR)
        self.assertEqual(manager.load_pdds(), 2)
        self.assertNotIn("invalid_yaml", manager.pdds)
        # TODO: Optionally check log output for error message

    def test_load_pdds_handles_validation_error(self):
        """Test handling of PDDs failing Pydantic validation."""
        invalid_pdd_data = create_valid_pdd_dict("invalid_schema", "Invalid Schema PDD")
        del invalid_pdd_data["template"]  # Make it invalid by removing required field 'template'

        with open(TEST_PDD_DIR / "invalid_schema.json", "w") as f:
            json.dump(invalid_pdd_data, f)

        manager = PromptManager(pdd_directory=TEST_PDD_DIR)
        self.assertEqual(manager.load_pdds(), 2)
        self.assertNotIn("invalid_schema", manager.pdds)
        # TODO: Optionally check log output for ValidationError

    def test_load_pdds_handles_missing_id(self):
        """Test handling of PDDs missing the required 'id' field."""
        no_id_pdd = create_valid_pdd_dict("temp_id", "No ID PDD")
        del no_id_pdd["id"]

        with open(TEST_PDD_DIR / "no_id.yaml", "w") as f:
            yaml.dump(no_id_pdd, f)

        manager = PromptManager(pdd_directory=TEST_PDD_DIR)
        self.assertEqual(manager.load_pdds(), 2)
        # The file is ignored, so no ID related to it should be present
        self.assertNotIn("temp_id", manager.pdds)
        self.assertNotIn("no_id", manager.pdds)
        # TODO: Optionally check log output for ValueError about missing ID

    def test_load_pdds_handles_duplicate_id(self):
        """Test that duplicate PDD IDs result in overwriting and a warning."""
        duplicate_data = create_valid_pdd_dict(
            "test_pdd_1", "Duplicate PDD One Name", "Duplicate PDD One Desc"
        )
        with open(TEST_PDD_DIR / "duplicate_pdd_1.yaml", "w") as f:
            yaml.dump(duplicate_data, f)

        # Use assertLogs to capture the warning
        with self.assertLogs(logger="CORUJA.PromptManager", level="WARNING") as log_watcher:
            manager = PromptManager(pdd_directory=TEST_PDD_DIR)
            load_count = manager.load_pdds()  # Perform the load
            # Assert on the final state of the manager's dictionary
            self.assertEqual(len(manager.pdds), 2)  # Should only contain 2 unique IDs
            self.assertIn("test_pdd_1", manager.pdds)
            # Assert the name matches the one likely processed last (the .json from setUp)
            self.assertEqual(manager.pdds["test_pdd_1"].name, "Test PDD One")

            # Check if the warning was logged
            self.assertTrue(
                any("Duplicate PDD ID 'test_pdd_1'" in msg for msg in log_watcher.output)
            )

    def test_get_pdd_success(self):
        """Test retrieving an existing PDD."""
        manager = PromptManager(pdd_directory=TEST_PDD_DIR)
        manager.load_pdds()  # Ensure PDDs are loaded
        pdd = manager.get_pdd("test_pdd_1")
        self.assertIsInstance(pdd, PromptDesignDocument)
        self.assertEqual(pdd.id, "test_pdd_1")
        self.assertEqual(pdd.name, "Test PDD One")

    def test_get_pdd_not_found(self):
        """Test retrieving a non-existent PDD raises PddNotFoundError."""
        manager = PromptManager(pdd_directory=TEST_PDD_DIR)
        with self.assertRaises(PddNotFoundError):
            manager.get_pdd("non_existent_pdd")

    def test_list_pdds(self):
        """Test listing the IDs of loaded PDDs."""
        manager = PromptManager(pdd_directory=TEST_PDD_DIR)
        pdd_ids = manager.list_pdds()
        self.assertIsInstance(pdd_ids, list)
        self.assertCountEqual(pdd_ids, ["test_pdd_1", "test_pdd_2"])  # Order doesn't matter

    def test_list_pdd_summaries(self):
        """Test listing summaries of loaded PDDs."""
        manager = PromptManager(pdd_directory=TEST_PDD_DIR)
        manager.load_pdds()  # Ensure PDDs are loaded
        summaries = manager.list_pdd_summaries()
        self.assertIsInstance(summaries, list)
        self.assertEqual(len(summaries), 2)

        # Check structure and content of one summary (order might vary)
        summary1 = next((s for s in summaries if s["id"] == "test_pdd_1"), None)
        self.assertIsNotNone(summary1)
        self.assertEqual(summary1["name"], "Test PDD One")
        self.assertEqual(summary1["description"], "Description for Test PDD One")

    def test_reload_pdds(self):
        """Test reloading PDDs by calling load_pdds again."""
        manager = PromptManager(pdd_directory=TEST_PDD_DIR)
        manager.load_pdds()  # Initial load
        self.assertEqual(len(manager.pdds), 2)

        # Add a new PDD file using the updated helper
        pdd3_data = create_valid_pdd_dict("test_pdd_3", "Test PDD Three", "Desc for PDD Three")
        with open(TEST_PDD_DIR / "test_pdd_3.json", "w") as f:
            json.dump(pdd3_data, f)

        # Reload and check by calling load_pdds again
        reloaded_count = manager.load_pdds()
        self.assertEqual(reloaded_count, 3)  # load_pdds returns count of files processed
        self.assertEqual(len(manager.pdds), 3)  # Check final count in manager
        self.assertIn("test_pdd_3", manager.pdds)
        self.assertEqual(manager.pdds["test_pdd_3"].name, "Test PDD Three")

    # --- Tests for render_prompt --- #

    def test_render_prompt_success(self):
        """Test successful prompt rendering with correct parameters."""
        manager = PromptManager(pdd_directory=TEST_PDD_DIR)
        manager.load_pdds()
        params = {"query": "What is the weather?"}
        expected_render = "Template for test_pdd_1: What is the weather?"
        rendered = manager.render_prompt("test_pdd_1", params)
        self.assertEqual(rendered, expected_render)

    def test_render_prompt_missing_parameter(self):
        """Test render_prompt raises ValueError if a required parameter is missing."""
        manager = PromptManager(pdd_directory=TEST_PDD_DIR)
        manager.load_pdds()
        params = {"wrong_param": "some value"}  # Missing 'query'
        with self.assertRaisesRegex(ValueError, "Missing required parameters.*query"):
            manager.render_prompt("test_pdd_1", params)

    def test_render_prompt_pdd_not_found(self):
        """Test render_prompt raises PddNotFoundError for non-existent PDD ID."""
        manager = PromptManager(pdd_directory=TEST_PDD_DIR)
        manager.load_pdds()
        params = {"query": "test"}
        with self.assertRaises(PddNotFoundError):
            manager.render_prompt("non_existent_pdd_id", params)

    def test_render_prompt_template_key_error(self):
        """Test render_prompt handles KeyError during formatting (e.g., bad template)."""
        # Create a PDD with a template mismatch
        bad_template_data = create_valid_pdd_dict("bad_template", "Bad Template PDD")
        bad_template_data["template"] = (
            "This template expects {wrong_variable}"  # Correct param is 'query'
        )
        with open(TEST_PDD_DIR / "bad_template.json", "w") as f:
            json.dump(bad_template_data, f)

        manager = PromptManager(pdd_directory=TEST_PDD_DIR)
        manager.load_pdds()
        params = {"query": "test value"}  # Correct param provided

        # Expect ValueError because format() will fail due to missing 'wrong_variable' key in params
        with self.assertRaisesRegex(
            ValueError, "Template formatting error.*"
        ):  # Check for our wrapper error
            manager.render_prompt("bad_template", params)


# Allow running tests directly
if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CORUJA Prompt Manager

Manages the loading, validation, and retrieval of Prompt Design Documents (PDDs).
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Union

from pydantic import ValidationError
import yaml

from subsystems.KOIOS.core.logging import KoiosLogger

# Assuming PDD schema is defined here, adjust if necessary
from subsystems.KOIOS.schemas.pdd_schema import PromptDesignDocument

# Get logger for this module
logger = KoiosLogger.get_logger("CORUJA.PromptManager")


class PddError(Exception):
    """Base exception for Prompt Design Document errors."""

    pass


class PddNotFoundError(PddError):
    """Raised when a requested PDD ID is not found."""

    pass


class PddValidationError(PddError):
    """Raised when a PDD file fails validation against the schema."""

    pass


class PromptManager:
    """Manages the loading, validation, retrieval, and rendering of Prompt Design Documents (PDDs).

    Attributes:
        pdd_directory (Path): The directory containing PDD files.
        pdds (Dict[str, PromptDesignDocument]): A dictionary storing loaded and validated PDDs, keyed by ID.
        logger (logging.Logger): Logger instance for this class.
    """

    def __init__(self, pdd_directory: Union[str, Path]):
        """Initializes the PromptManager.

        Args:
            pdd_directory: The path to the directory containing PDD files (.json, .yaml, .yml).

        Raises:
            FileNotFoundError: If the specified directory does not exist.
        """
        self.pdd_directory = Path(pdd_directory)
        self.pdds: Dict[str, PromptDesignDocument] = {}
        # Initialize logger for the instance
        self.logger = logger  # Use the module-level logger

        if not self.pdd_directory.is_dir():
            self.logger.error(f"PDD directory not found: {self.pdd_directory}")
            raise FileNotFoundError(f"PDD directory not found: {self.pdd_directory}")

        self.logger.info(f"Initializing PromptManager with directory: {self.pdd_directory}")
        # Load PDDs upon initialization
        self.load_pdds()

    def load_pdds(self) -> int:
        """Scans the PDD directory, loads, and validates PDD files.

        Clears existing loaded PDDs before loading.

        Returns:
            The number of PDDs successfully loaded.
        """
        self.pdds.clear()
        loaded_count = 0
        logger.info(f"Scanning for PDDs in {self.pdd_directory}...")

        for file_path in self.pdd_directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in [".json", ".yaml", ".yml"]:
                logger.debug(f"Attempting to load PDD from: {file_path.name}")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        if file_path.suffix.lower() == ".json":
                            pdd_data = json.load(f)
                        else:  # .yaml or .yml
                            pdd_data = yaml.safe_load(f)

                    if not isinstance(pdd_data, dict):
                        raise ValueError("PDD content is not a dictionary.")

                    # Basic check for required 'id' field before validation
                    pdd_id = pdd_data.get("id")
                    if not pdd_id or not isinstance(pdd_id, str):
                        raise ValueError(
                            "PDD data missing required 'id' field or it is not a string."
                        )

                    # Validate against the Pydantic model
                    pdd_model = PromptDesignDocument(**pdd_data)

                    if pdd_id in self.pdds:
                        logger.warning(
                            f"Duplicate PDD ID '{pdd_id}' found in {file_path.name}. "
                            f"Overwriting previous entry from {self.pdds[pdd_id]._source_file}"
                        )  # Assuming we add _source_file

                    pdd_model._source_file = file_path  # Store source for reference
                    self.pdds[pdd_id] = pdd_model
                    loaded_count += 1
                    logger.debug(f"Successfully loaded and validated PDD: {pdd_id}")

                except (json.JSONDecodeError, yaml.YAMLError) as e:
                    logger.error(f"Error decoding PDD file {file_path.name}: {e}")
                except ValidationError as e:
                    logger.error(f"Validation error in PDD file {file_path.name}:\n{e}")
                except ValueError as e:
                    logger.error(f"Value error loading PDD file {file_path.name}: {e}")
                except Exception as e:
                    logger.error(
                        f"Unexpected error loading PDD file {file_path.name}: {e}", exc_info=True
                    )

        logger.info(f"Finished loading PDDs. Successfully loaded {loaded_count} PDDs.")
        return loaded_count

    def get_pdd(self, pdd_id: str) -> PromptDesignDocument:
        """Retrieves a specific PDD by its ID.

        Args:
            pdd_id: The unique identifier of the PDD.

        Returns:
            The validated PromptDesignDocument object.

        Raises:
            PddNotFoundError: If the PDD ID is not found.
        """
        pdd = self.pdds.get(pdd_id)
        if pdd is None:
            logger.warning(f"PDD with ID '{pdd_id}' not found.")
            raise PddNotFoundError(f"PDD with ID '{pdd_id}' not found.")
        logger.debug(f"Retrieved PDD: {pdd_id}")
        return pdd

    def list_pdds(self) -> List[str]:
        """Returns a list of IDs of the loaded PDDs."""
        return list(self.pdds.keys())

    def list_pdd_summaries(self) -> List[Dict[str, str]]:
        """Returns a list of summaries (ID, name, description) for loaded PDDs."""
        summaries = []
        for pdd_id, pdd in self.pdds.items():
            summaries.append({"id": pdd_id, "name": pdd.name, "description": pdd.description})
        return summaries

    def reload(self) -> int:
        """Reloads all PDDs from the directory."""
        logger.info("Reloading PDDs...")
        return self.load_pdds()

    def render_prompt(self, pdd_id: str, parameters: Dict[str, Any]) -> str:
        """Renders the prompt template for a given PDD ID using provided parameters.

        Args:
            pdd_id: The unique ID of the Prompt Design Document.
            parameters: A dictionary containing the key-value pairs for template variables.

        Returns:
            The rendered prompt string with variables substituted.

        Raises:
            PddNotFoundError: If the PDD with the specified ID is not found.
            ValueError: If required parameters are missing from the input dictionary.
        """
        pdd = self.get_pdd(pdd_id)  # Raises PddNotFoundError if not found

        # Validate that all parameters listed in the PDD are provided
        missing_params = []
        for required_param in pdd.parameters:
            if required_param not in parameters:
                missing_params.append(required_param)

        if missing_params:
            raise ValueError(
                f"Missing required parameters for PDD '{pdd_id}': {', '.join(missing_params)}"
            )

        # Perform the template rendering using standard string formatting
        try:
            rendered_prompt = pdd.template.format(**parameters)
            return rendered_prompt
        except KeyError as e:
            # This might happen if the template string contains placeholders
            # not listed in pdd.parameters, or if parameters has extra keys
            # not used in the template (which is usually fine, but KeyError
            # specifically points to a missing key *in the template*).
            self.logger.error(
                f"KeyError during template rendering for PDD '{pdd_id}'. "
                f"Template might contain unexpected placeholder: {e}",
                exc_info=True,  # Include traceback for debugging
            )
            raise ValueError(
                f"Template formatting error for PDD '{pdd_id}'. "
                f"Ensure all template variables {pdd.parameters} are correctly defined "
                f"and provided. Error detail: {e}"
            ) from e
        except Exception as e:
            # Catch other potential formatting errors
            self.logger.error(
                f"Unexpected error rendering template for PDD '{pdd_id}': {e}", exc_info=True
            )
            raise ValueError(f"Failed to render prompt for PDD '{pdd_id}': {e}") from e


# Example Usage (Optional, for testing or demonstration)
# if __name__ == "__main__":
#     # Assuming PDDs are in a 'pdds' subdirectory relative to this script
#     script_dir = Path(__file__).parent
#     pdd_dir = script_dir.parent / "pdds"
#     pdd_dir.mkdir(exist_ok=True)

#     # Create a dummy PDD file for testing
#     dummy_pdd = {
#         "id": "dummy_v1",
#         "metadata": {
#             "name": "Dummy Prompt",
#             "version": "1.0",
#             "description": "A simple test prompt.",
#             "tags": ["test", "dummy"],
#             "author": "KoiosLogger Test",
#             "created_date": "2024-08-15T12:00:00Z",
#             "last_updated": "2024-08-15T12:00:00Z"
#         },
#         "parameters": [
#             {"name": "user_query", "description": "The user's input", "type": "string", "required": True}
#         ],
#         "prompt_template": "Answer this query: {user_query}",
#         "response_schema": {"type": "string"},
#         "ethik_guidelines": None,
#         "examples": []
#     }
#     with open(pdd_dir / "dummy_v1.json", "w") as f:
#         json.dump(dummy_pdd, f, indent=2)

#     try:
#         manager = PromptManager(pdd_directory=pdd_dir)
#         print(f"Loaded PDD IDs: {manager.list_pdds()}")
#         print(f"Summaries: {manager.list_pdd_summaries()}")
#         dummy = manager.get_pdd("dummy_v1")
#         print(f"Retrieved Dummy PDD Name: {dummy.metadata.name}")
#     except Exception as e:
#         print(f"Error during example usage: {e}")
#     finally:
#         # Clean up dummy file
#         (pdd_dir / "dummy_v1.json").unlink(missing_ok=True)

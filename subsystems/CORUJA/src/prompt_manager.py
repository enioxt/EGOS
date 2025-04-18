"""
PromptManager for CORUJA subsystem.

- Loads, parses, formats, and caches Prompt Design Documents (PDDs).
- Uses config from ConfigLoader for PDD paths.
- Provides load_pdd, format_prompt, and cache management methods.
- Logs actions via KoiosLogger or fallback logger.
- References PDD standards and usage in CORUJA architecture.

Usage:
    from prompt_manager import PromptManager
    pm = PromptManager()
    pdd = pm.get_pdd("AgentRole")
    prompt = pm.format_prompt("AgentRole", variables={"goal": "Write code"})

"""
import logging
import json
import yaml  # Requires PyYAML installation
import os
from typing import Any, Dict, Optional
from functools import lru_cache
from subsystems.CORUJA.src.config_loader import ConfigLoader

try:
    from koios_utils.log import KoiosLogger  # Assuming KoiosLogger is available

    logger = KoiosLogger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    logger.warning("KoiosLogger not found, falling back to standard logging.")


class PromptManagerError(Exception):
    """Custom exception for PromptManager errors."""

    pass


class PromptManager:
    """
    Manages Prompt Design Documents (PDDs).

    - Loads PDDs from files (JSON/YAML) or dictionaries.
    - Caches loaded PDDs for performance.
    - Formats prompts using variable injection.
    - Logs actions and errors.
    """

    def __init__(self, pdd_source: Optional[Dict[str, Dict]] = None):
        """
        Initializes the PromptManager.

        Args:
            pdd_source: Optional dictionary containing PDDs directly,
                        or paths to PDD files.
                        Keys are PDD names, values are dicts or file paths.
        """
        self.config = ConfigLoader.get()
        self.pdd_source = pdd_source if pdd_source is not None else {}
        logger.info("PromptManager initialized.")

    @lru_cache(maxsize=128)
    def _load_pdd(self, pdd_name: str) -> Dict[str, Any]:
        """Loads a specific PDD, caching the result."""
        if pdd_name not in self.pdd_source:
            msg = f"PDD source not found for name: {pdd_name}"
            logger.error(msg)
            raise PromptManagerError(msg)

        source_value = self.pdd_source[pdd_name]

        if isinstance(source_value, dict):
            logger.debug(f"Loaded PDD '{pdd_name}' directly from source.")
            return source_value
        elif isinstance(source_value, str) and os.path.exists(source_value):
            file_path = source_value
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    if file_path.endswith(".json"):
                        pdd = json.load(f)
                    elif file_path.endswith((".yaml", ".yml")):
                        pdd = yaml.safe_load(f)
                    else:
                        msg = f"Unsupported PDD file format: {file_path}"
                        logger.error(msg)
                        raise PromptManagerError(msg)
                logger.info(f"Loaded PDD '{pdd_name}' from file: {file_path}")
                return pdd
            except Exception as e:
                msg = f"Error loading PDD file '{file_path}': {e}"
                logger.exception(msg)
                raise PromptManagerError(msg) from e
        else:
            msg = f"Invalid PDD source for '{pdd_name}': {source_value}"
            logger.error(msg)
            raise PromptManagerError(msg)

    def get_pdd(self, pdd_name: str) -> Dict[str, Any]:
        """Retrieves a PDD by name, utilizing the cache."""
        try:
            return self._load_pdd(pdd_name)
        except PromptManagerError:
            raise  # Re-raise specific error
        except Exception as e:
            msg = f"Unexpected error getting PDD '{pdd_name}': {e}"
            logger.exception(msg)
            raise PromptManagerError(msg) from e

    def format_prompt(self, pdd_name: str, variables: Dict[str, Any]) -> str:
        """
        Loads a PDD and formats its template using provided variables.

        Args:
            pdd_name: The name of the PDD to use.
            variables: A dictionary of variables to inject into the prompt template.

        Returns:
            The formatted prompt string.

        Raises:
            PromptManagerError: If the PDD cannot be loaded or formatted.
            KeyError: If a required variable is missing during formatting.
        """
        try:
            pdd = self.get_pdd(pdd_name)
            template = pdd.get("template")
            if not isinstance(template, str):
                msg = f"PDD '{pdd_name}' is missing a valid 'template' string."
                logger.error(msg)
                raise PromptManagerError(msg)

            formatted = template.format(**variables)
            logger.debug(f"Formatted prompt using PDD '{pdd_name}'.")
            return formatted
        except KeyError as e:
            msg = f"Missing variable '{e}' for PDD '{pdd_name}' formatting."
            logger.error(msg)
            raise PromptManagerError(msg) from e
        except PromptManagerError:
            raise
        except Exception as e:
            msg = f"Error formatting prompt for PDD '{pdd_name}': {e}"
            logger.exception(msg)
            raise PromptManagerError(msg) from e

    def clear_cache(self):
        """Clears the PDD cache."""
        self._load_pdd.cache_clear()
        logger.info("PromptManager PDD cache cleared.")

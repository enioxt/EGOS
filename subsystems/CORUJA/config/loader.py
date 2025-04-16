"""
Handles loading configuration for the CORUJA subsystem,
including API keys, model settings, and other parameters.
"""
# Standard library imports
import os
import json
from typing import Dict, Any, Optional, List

# EGOS Subsystem Imports (Placeholders - uncomment/adjust paths when implemented)

from koios.logger import KoiosLogger
# from subsystems.CRONOS.interfaces import CronosInterface # Example adjusted path

logger = KoiosLogger.get_logger("CORUJA.ConfigLoader")

# Potential configuration file paths (relative to project root or config dir)
DEFAULT_CONFIG_PATHS = [
    "config/coruja_config.json",
    "config/api_keys.json" # Example for secrets
]

class ConfigurationLoader:
    """
    Loads and provides access to CORUJA configuration settings.

    Prioritizes environment variables over configuration files.
    Handles secure loading of secrets like API keys.
    """

    def __init__(self, config_paths: Optional[List[str]] = None):
        """
        Initializes the ConfigurationLoader and loads configuration.

        Args:
            config_paths: Optional list of paths to configuration files.
                          Defaults to DEFAULT_CONFIG_PATHS.
        """
        self.config_paths = config_paths or DEFAULT_CONFIG_PATHS
        self.config: Dict[str, Any] = {}
        self.secrets: Dict[str, Any] = {} # Store sensitive data separately
        self.load_config()
        logger.info("ConfigurationLoader initialized.")

    def load_config(self):
        """
        Loads configuration from files and environment variables.
        Environment variables override file settings.
        Secrets (like API keys) are loaded primarily from environment or specific secret files.
        """
        loaded_config = {}
        loaded_secrets = {}

        # 1. Load from files
        for path in self.config_paths:
            try:
                # TODO: Use CRONOS interface for file access if needed
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        file_content = json.load(f)
                        logger.info(f"Loaded configuration from: {path}")
                        # Distinguish secrets based on filename or content structure (example)
                        if "api_keys" in path.lower() or "secrets" in path.lower():
                             loaded_secrets.update(file_content)
                        else:
                             loaded_config.update(file_content)
                else:
                    logger.warning(f"Configuration file not found: {path}")
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in configuration file: {path}")
            except IOError as e:
                logger.error(f"Error reading configuration file {path}: {e}")
            except Exception as e:
                 logger.error(f"Unexpected error loading config file {path}: {e}", exc_info=True)


        # 2. Load/Override Secrets from Environment Variables (Example: CORUJA_OPENAI_API_KEY)
        # Example for OpenAI API Key
        openai_key_env = os.environ.get("CORUJA_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if openai_key_env:
            loaded_secrets["openai"] = {"api_key": openai_key_env} # Structure might vary
            logger.info("Loaded OpenAI API key from environment variable.")
        # Add similar logic for other providers (Anthropic, Google, etc.)

        # 3. Load/Override General Config from Environment Variables (Example: CORUJA_LOG_LEVEL)
        log_level_env = os.environ.get("CORUJA_LOG_LEVEL")
        if log_level_env:
            loaded_config["logging"] = loaded_config.get("logging", {})
            loaded_config["logging"]["level"] = log_level_env
            logger.info(f"Overrode log level from environment variable: {log_level_env}")

        self.config = loaded_config
        self.secrets = loaded_secrets
        logger.debug(f"Final loaded config (non-secrets): {self.config}")
        logger.debug(f"Final loaded secrets keys: {list(self.secrets.keys())}") # Avoid logging secret values

    def get_config(self) -> Dict[str, Any]:
        """Returns the loaded general configuration."""
        return self.config

    def get_setting(self, key: str, default: Optional[Any] = None) -> Any:
        """Gets a specific setting from the general configuration."""
        return self.config.get(key, default)

    def get_api_key(self, provider_name: str) -> Optional[str]:
        """
        Retrieves the API key for a specific provider from the loaded secrets.

        Args:
            provider_name: The name of the provider (e.g., 'openai', 'anthropic').

        Returns:
            The API key string, or None if not found.
        """
        provider_key = provider_name.lower()
        key_info = self.secrets.get(provider_key)
        if isinstance(key_info, dict):
            potential_key: Any = key_info.get('api_key') # Assign to intermediate variable
            # Explicitly check if the retrieved key is a string
            if isinstance(potential_key, str):
                 logger.debug(f"Retrieved API key for provider: {provider_name}")
                 return potential_key # Return the typed variable
            elif potential_key is not None:
                 # Log if it exists but isn't a string
                 logger.warning(f"API key found for provider {provider_name} but is not a string (Type: {type(potential_key)}).")
                 return None
            else:
                 # Key 'api_key' was not found in the dict
                 logger.warning(f"API key ('api_key' field) not found within secrets dictionary for provider: {provider_name}")
                 return None
        elif isinstance(key_info, str): # Allow direct key storage under provider name
             logger.debug(f"Retrieved API key directly for provider: {provider_name}")
             return key_info
        else:
            logger.warning(f"API key information not found or in unexpected format for provider: {provider_name}")
            return None

# Example Usage (Conceptual)
# loader = ConfigurationLoader()
# general_config = loader.get_config()
# openai_key = loader.get_api_key("openai")
# log_level = loader.get_setting("logging", {}).get("level", "INFO")
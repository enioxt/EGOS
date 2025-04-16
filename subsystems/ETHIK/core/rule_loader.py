import json
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime, timezone

from koios.logger import KoiosLogger
from .validator import ValidationRule # Assuming ValidationRule is in validator.py

logger = KoiosLogger.get_logger("ETHIK.Core.RuleLoader")

class RuleLoader:
    """Handles loading and parsing validation rules from a file."""

    def __init__(self, config: Dict[str, Any]):
        """Initializes the RuleLoader.

        Args:
            config: Configuration dictionary, expected to contain 'rules_file'.
        """
        self.config = config

    def load_rules(self) -> Dict[str, ValidationRule]:
        """Loads validation rules from the JSON file specified in the configuration."""
        rules_file_path_str = self.config.get("rules_file")
        if not rules_file_path_str:
            logger.error("'rules_file' not found in config. Cannot load rules.")
            return {}

        # Assume relative path from project root for now, needs clarification
        rules_path = Path(rules_file_path_str)
        if not rules_path.is_absolute():
            # This assumes the script runs from project root
            try:
                rules_path = Path.cwd() / rules_file_path_str
                if not rules_path.is_file():
                    logger.warning(f"Relative rules path '{rules_file_path_str}' not found relative to CWD. Specify absolute path or path from project root.")
                    return {}
            except Exception as path_e:
                logger.error(f"Error resolving relative rules path '{rules_file_path_str}': {path_e}")
                return {}

        logger.info(f"Attempting to load validation rules from: {rules_path}")
        if not rules_path.is_file():
            logger.warning(f"Validation rules file not found: {rules_path}. No rules loaded.")
            return {}

        try:
            with rules_path.open("r", encoding="utf-8") as f:
                rules_data = json.load(f)

            if not isinstance(rules_data, dict) or "rules" not in rules_data:
                raise ValueError("Invalid format: Missing top-level 'rules' key.")
            if not isinstance(rules_data["rules"], list):
                raise ValueError("Invalid format: 'rules' key must contain a list.")

            loaded_rules: Dict[str, ValidationRule] = {}
            for i, rule_dict in enumerate(rules_data["rules"]):
                if not isinstance(rule_dict, dict):
                    logger.warning(f"Skipping invalid rule entry #{i+1}: Not a dict.")
                    continue
                try:
                    required_keys = {"id", "name", "description", "severity", "conditions", "threshold", "action"}
                    if not required_keys.issubset(rule_dict.keys()):
                        missing = required_keys - rule_dict.keys()
                        raise TypeError(f"Rule entry #{i+1} missing required keys: {missing}")

                    # Handle datetime strings if present
                    if "created" in rule_dict and isinstance(rule_dict["created"], str):
                         rule_dict["created"] = datetime.fromisoformat(rule_dict["created"].replace("Z", "+00:00"))
                    if "last_updated" in rule_dict and isinstance(rule_dict["last_updated"], str):
                         rule_dict["last_updated"] = datetime.fromisoformat(rule_dict["last_updated"].replace("Z", "+00:00"))

                    rule = ValidationRule(**rule_dict)
                    if rule.id in loaded_rules:
                        logger.warning(f"Duplicate rule ID '{rule.id}'. Overwriting.")
                    loaded_rules[rule.id] = rule
                except (TypeError, ValueError) as rule_parse_err:
                    logger.error(f"Error parsing rule entry #{i+1}: {rule_parse_err}")
                except Exception as inner_e:
                     logger.error(f"Unexpected error processing rule entry #{i+1}: {inner_e}", exc_info=True)

            logger.info(f"Successfully loaded {len(loaded_rules)} validation rules from {rules_path.name}")
            return loaded_rules

        except Exception as e:
            logger.error(f"Failed to load rules from {rules_path}: {e}", exc_info=True)
            return {}

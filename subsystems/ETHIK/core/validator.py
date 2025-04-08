#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ETHIK Validator: Performs ethical validation based on configurable rules.

This module defines the EthikValidator class responsible for loading rules,
listening for validation requests (potentially via Mycelium), evaluating actions
against rules, and reporting results.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone  # Use timezone-aware datetimes
import json  # Ensure json is imported
import logging
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

# TypeAlias,  # Use TypeAlias for placeholder types - Requires Python 3.10+
from koios.logger import KoiosLogger  # Assuming KoiosLogger is available
from typing_extensions import TypeAlias  # Use this for compatibility < 3.10

from subsystems.ETHIK.core.patterns import PatternRegistry  # Assuming PatternRegistry exists

# TODO: Replace with KoiosLogger import and usage
# from koios.logger import KoiosLogger
logger = KoiosLogger.get_logger("ETHIK.Validator")  # Use standard logger for now

MyceliumClient: TypeAlias = Any  # Placeholder type
Message: TypeAlias = Any  # Placeholder type


@dataclass
class ValidationRule:
    """Defines a single ethical validation rule."""

    id: str
    name: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    conditions: List[str]  # Conditions expressed as strings (evaluation TBD)
    threshold: float  # Threshold for rule activation (meaning depends on evaluation)
    action: str  # 'block', 'warn', 'log'
    created: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ValidationResult:
    """Represents the result of applying validation rules to an action."""

    is_valid: bool
    action_taken: str  # e.g., 'allowed', 'blocked', 'warned'
    severity: str  # Overall severity if invalid ('critical', 'high', etc.)
    score: float  # Overall score (if applicable)
    details: str  # Summary of findings or reasons
    rule_results: List[Dict[str, Any]]  # List of individual rule results
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    affected_components: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EthikValidator:
    """Performs real-time ethical validation based on loaded rules.

    Connects to Mycelium (optional) to listen for validation requests and publish results.
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        mycelium_client: Optional[MyceliumClient] = None,
        pattern_registry: Optional[PatternRegistry] = None,
    ):
        """Initializes the EthikValidator.

        Args:
            config_path: Path to the JSON configuration file.
            mycelium_client: An initialized Mycelium client instance (optional).
            pattern_registry: An initialized PatternRegistry instance (optional).
        """
        # self.logger = KoiosLogger.get_logger("ETHIK.Validator") # Target state
        self.logger = logger  # Use module logger for now
        self.mycelium = mycelium_client
        self.pattern_registry = pattern_registry or PatternRegistry()
        self.rules: Dict[str, ValidationRule] = {}
        self.validation_history: List[ValidationResult] = []

        try:
        self.config = self._load_config(config_path)
            self.max_history = self.config.get("max_history_size", 1000)
            self._load_rules()  # Load initial rules
        except Exception as e:
            self.logger.critical(f"Failed to initialize EthikValidator: {e}", exc_info=True)
            # Depending on severity, either raise or continue in a degraded state
            self.config = self._load_config(None)  # Load defaults
        self.max_history = self.config.get("max_history_size", 1000)
            self.rules = {}  # Ensure rules are empty if loading failed
            # raise EthikConfigurationError("Failed to initialize Validator") from e

        # Setup Mycelium handlers only if client provided and config exists
        if self.mycelium and "mycelium" in self.config:
            self.topics = self.config["mycelium"].get("topics", {})
            if not self.topics:
                self.logger.warning("Mycelium client provided but no topics found in config.")
            else:
            self._setup_mycelium_handlers()
        elif self.mycelium:
            self.logger.warning("Mycelium client provided but no 'mycelium' section in config.")

        self.logger.info(f"EthikValidator initialized. Rules loaded: {len(self.rules)}")

    def _setup_mycelium_handlers(self):
        """Sets up handlers for Mycelium message subscriptions."""
        self.logger.debug("Setting up Mycelium handlers...")

        validate_topic = self.topics.get("validate_request")
        if validate_topic and self.mycelium:
            try:
                # TODO: Update with actual Mycelium subscribe signature
                # Example assumes subscribe returns a registration ID
                # sub_id = await self.mycelium.subscribe(validate_topic, self._handle_validation_request)
                # self.logger.info(f"Subscribed to '{validate_topic}' (ID: {sub_id})")
                self.logger.info(f"Attempting to subscribe to '{validate_topic}' (simulation)")
            except Exception as e:
                self.logger.error(f"Failed to subscribe to '{validate_topic}': {e}", exc_info=True)
        else:
            self.logger.warning(
                "'validate_request' topic not configured or Mycelium client missing."
            )

        rules_update_topic = self.topics.get("rules_update")
        if rules_update_topic and self.mycelium:
            try:
                # sub_id = await self.mycelium.subscribe(rules_update_topic, self._handle_rules_update)
                # self.logger.info(f"Subscribed to '{rules_update_topic}' (ID: {sub_id})")
                self.logger.info(f"Attempting to subscribe to '{rules_update_topic}' (simulation)")
            except Exception as e:
                self.logger.error(
                    f"Failed to subscribe to '{rules_update_topic}': {e}", exc_info=True
                )
        else:
            self.logger.warning("'rules_update' topic not configured or Mycelium client missing.")

    # TODO: Make handler methods async if Mycelium callbacks are async
    # Wrapped handlers for Mycelium messages:
    async def _handle_validation_request(self, message: Message):
        """Handles incoming validation requests received via Mycelium."""
        try:
            # TODO: Replace with actual message attribute access
            request_id = getattr(message, "id", "unknown")
            message_data = getattr(message, "data", None)
            if not isinstance(message_data, dict):
                self.logger.error(f"Invalid message data type received: {type(message_data)}")
                return  # Or publish error

            self.logger.info(f"Received validation request: {request_id}")

            action_context = message_data.get("action_context", None)
            params = message_data.get("params", {})
            rule_ids = message_data.get("rule_ids", [])  # Optional: specific rules to apply

            if not action_context:
                raise ValueError("'action_context' missing in validation request")

                # Perform validation
            result = await self.validate_action(action_context, params, rule_ids)

                # Publish result
            result_topic = self.topics.get("validate_result", "ethik.validate.result.default")
            result_payload = {
                "request_id": request_id,
                "action_context": action_context,
                "result": asdict(result),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            # TODO: Replace with actual Mycelium publish call
            # await self.mycelium.publish(result_topic, result_payload)
            self.logger.debug(f"Simulating publish to '{result_topic}': {result_payload}")

            # If validation failed, publish alert based on severity
            alert_threshold_str = self.config.get("alert_severity_threshold", "high").lower()
            severity_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            if not result.is_valid and severity_map.get(
                result.severity.lower(), 0
            ) >= severity_map.get(alert_threshold_str, 3):
                    await self._publish_alert(
                    alert_type="validation_failure",
                    message=f"Action failed validation: {result.details}",
                    details={
                        "action_context": action_context,
                        "result": asdict(result),
                        },
                    )

            except Exception as e:
                self.logger.error(f"Error handling validation request: {e}", exc_info=True)
            error_topic = self.topics.get("validate_result", "ethik.validate.result.default")
            error_payload = {"request_id": request_id, "status": "error", "error": str(e)}
            try:
                # TODO: Replace with actual Mycelium publish call
                # await self.mycelium.publish(error_topic, error_payload)
                self.logger.debug(f"Simulating error publish to '{error_topic}': {error_payload}")
            except Exception as pub_e:
                self.logger.error(f"Failed to publish error result: {pub_e}", exc_info=True)

    async def _handle_rules_update(self, message: Message):
        """Handles rule update requests received via Mycelium.

        Args:
            message: The Mycelium message containing the rule update information.
                     Expected data format: {'update_type': 'add'/'remove'/'reload', 'rules': [...], 'config': {...}}
        """
        request_id = getattr(message, "id", "unknown_rules_update")
        message_data = getattr(message, "data", None)
        status_topic = self.topics.get("rules_status", "ethik.rules.status.default")
        status_payload = {"request_id": request_id, "status": "pending"}

        self.logger.info(f"Received rules update request: {request_id}")
        if not isinstance(message_data, dict):
            self.logger.error(f"Invalid rules update data type received: {type(message_data)}")
            status_payload["status"] = "error"
            status_payload["error"] = "Invalid message data type"
            # TODO: Publish error status
            # await self.mycelium.publish(status_topic, status_payload)
            self.logger.debug(f"Simulating error publish to '{status_topic}': {status_payload}")
            return

        try:
            # TODO: Implement detailed rule update logic based on message_data
            # - Parse update_type ('add', 'remove', 'reload', 'config_update')
            # - Validate new rule structures
            # - Update self.rules dictionary (add/remove)
            # - Reload rules from file if 'reload'
            # - Update self.config if 'config_update'
            update_type = message_data.get("update_type", "unknown")
            if update_type == "reload":
                self._load_rules()  # Reload all rules
                status_payload["status"] = "success"
                status_payload["details"] = f"Reloaded {len(self.rules)} rules."
            elif update_type == "add":
                # TODO: Implement adding individual rules
                status_payload["status"] = "error"
                status_payload["error"] = "Add rule not yet implemented"
                self.logger.warning(f"Rule update type '{update_type}' not implemented.")
            elif update_type == "remove":
                # TODO: Implement removing individual rules
                status_payload["status"] = "error"
                status_payload["error"] = "Remove rule not yet implemented"
                self.logger.warning(f"Rule update type '{update_type}' not implemented.")
            elif update_type == "config_update":
                # TODO: Implement dynamic config update
                status_payload["status"] = "error"
                status_payload["error"] = "Config update not yet implemented"
                self.logger.warning(f"Rule update type '{update_type}' not implemented.")
            else:
                raise ValueError(f"Unknown rules update type: {update_type}")

            self.logger.info(
                f"Rules update '{update_type}' processed for request {request_id}. Status: {status_payload['status']}"
            )
            # TODO: Publish success/final status
            # await self.mycelium.publish(status_topic, status_payload)
            self.logger.debug(f"Simulating status publish to '{status_topic}': {status_payload}")

            except Exception as e:
            self.logger.error(
                f"Error handling rules update request {request_id}: {e}", exc_info=True
            )
            status_payload["status"] = "error"
            status_payload["error"] = str(e)
            try:
                # TODO: Replace with actual Mycelium publish call
                # await self.mycelium.publish(status_topic, status_payload)
                self.logger.debug(f"Simulating error publish to '{status_topic}': {status_payload}")
            except Exception as pub_e:
                self.logger.error(
                    f"Failed to publish rules update error status: {pub_e}", exc_info=True
                )

    async def _publish_alert(self, alert_type: str, message: str, details: Dict[str, Any]):
        """Publishes an alert message via Mycelium if configured.

        Args:
            alert_type: A string indicating the category of the alert (e.g., 'validation_failure').
            message: A human-readable summary of the alert.
            details: A dictionary containing specific details related to the alert.
        """
        if not self.mycelium:
            self.logger.warning(
                f"Cannot publish alert (Type: {alert_type}), Mycelium client not configured."
            )
            return

        alert_topic = self.topics.get("alert", "ethik.alert.default")
        if not alert_topic:
            self.logger.warning(
                f"Cannot publish alert (Type: {alert_type}), 'alert' topic not configured."
            )
            return

        try:
            payload = {
                    "type": alert_type,
                    "message": message,
                    "details": details,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            # TODO: Replace with actual Mycelium publish call
            # await self.mycelium.publish(alert_topic, payload)
            self.logger.info(f"Simulating publish alert to '{alert_topic}': Type={alert_type}")
            self.logger.debug(f"Alert details: {details}")

        except Exception as e:
            self.logger.error(f"Failed to publish alert to {alert_topic}: {e}", exc_info=True)

    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Loads validator configuration from a JSON file or returns defaults.

        Args:
            config_path: Optional path to the JSON configuration file.

        Returns:
            A dictionary containing the configuration.

        Raises:
            # TODO: Consider raising EthikConfigurationError for critical loading failures
            #       if recovery to default state is not desired.
            pass # Placeholder for potential future raises
        """
        # Define default configuration structure clearly
        default_config = {
            "rules_file": "config/ethik_rules.json",  # Default relative path
            "max_history_size": 1000,
            "alert_severity_threshold": "high",  # e.g., 'critical', 'high', 'medium', 'low'
            "mycelium": {
                "topics": {
                    "validate_request": "ethik.validate.request",
                    "validate_result": "ethik.validate.result",
                    "rules_update": "ethik.rules.update",
                    "rules_status": "ethik.rules.status",
                    "alert": "ethik.alert",
                }
            },
            # Add other configuration sections as needed
        }

        if config_path and config_path.is_file():
            try:
                self.logger.info(f"Loading configuration from: {config_path}")
                with config_path.open("r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                # Recursively merge loaded config onto defaults (creates a new dict)
                merged_config = self._deep_merge(default_config, loaded_config)
                self.logger.info("Configuration loaded successfully.")
                return merged_config
            except json.JSONDecodeError as e:
                self.logger.error(
                    f"Invalid JSON in configuration file {config_path}: {e}. Using default config.",
                    exc_info=True,
                )
            except IOError as e:
                self.logger.error(
                    f"Error reading configuration file {config_path}: {e}. Using default config.",
                    exc_info=True,
                )
            except Exception as e:
                self.logger.error(
                    f"Unexpected error loading configuration from {config_path}: {e}. "
                    "Using default config.",
                    exc_info=True,
                )
        elif config_path:
            self.logger.warning(
                f"Configuration file not found at {config_path}. Using default config."
            )
        else:
            self.logger.info("No configuration path provided. Using default config.")

        # Return a copy of defaults if loading failed or no path provided
        return default_config.copy()

    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge the update dictionary into the base dictionary.

        Creates new dictionaries for nested structures to avoid modifying the original base.

        Args:
            base: The base dictionary (e.g., defaults).
            update: The dictionary with updates to merge.

        Returns:
            A new dictionary representing the merged result.
        """
        merged = base.copy()  # Start with a copy of the base
        for key, value in update.items():
            if key in merged:
                if isinstance(merged[key], dict) and isinstance(value, dict):
                    # If both are dicts, recurse
                    merged[key] = self._deep_merge(merged[key], value)
                # Example: Extend lists (optional, default is replace)
                # elif isinstance(merged[key], list) and isinstance(value, list):
                #     merged[key] = merged[key] + value # Or other merge strategy
                else:
                    # If types differ or not dict/list, update replaces base value
                    merged[key] = value
            else:
                # If key is not in base, add it
                merged[key] = value
        return merged

    def _load_rules(self) -> None:
        """Loads validation rules from the JSON file specified in the configuration."""
        rules_file_path_str = self.config.get("rules_file")

        if not rules_file_path_str:
            self.logger.error(
                "Validation rules file path ('rules_file') not found in configuration. "
                "No rules will be loaded."
            )
            self.rules.clear()
            return

        # Assume relative path from workspace root if not absolute
        # TODO: Clarify how relative paths are resolved (e.g., relative to config file or workspace?)
        rules_path = Path(rules_file_path_str)

        self.logger.info(f"Attempting to load validation rules from: {rules_path}")
        if not rules_path.is_file():
            self.logger.warning(
                f"Validation rules file not found or is not a file: {rules_path}. "
                "Validator will operate without rules."
            )
            self.rules.clear()
            return

        try:
            with rules_path.open("r", encoding="utf-8") as f:
                rules_data = json.load(f)

            if not isinstance(rules_data, dict) or "rules" not in rules_data:
            self.logger.error(
                    f"Invalid format in rules file {rules_path}: Missing top-level 'rules' key."
                )
                self.rules.clear()
            return

            if not isinstance(rules_data["rules"], list):
                self.logger.error(
                    f"Invalid format in rules file {rules_path}: 'rules' key must contain a list."
                )
                self.rules.clear()
            return

            loaded_rules: Dict[str, ValidationRule] = {}
            for i, rule_dict in enumerate(rules_data["rules"]):
                if not isinstance(rule_dict, dict):
                    self.logger.warning(
                        f"Skipping invalid rule entry #{i + 1} in {rules_path}: Not a dictionary."
                    )
                    continue

                # TODO: Implement robust schema validation for each rule_dict here
                #       using something like Pydantic or jsonschema before creating ValidationRule.

                try:
                    # Ensure required fields are present before ** unpacking
                    required_keys = {
                        "id",
                        "name",
                        "description",
                        "severity",
                        "conditions",
                        "threshold",
                        "action",
                    }
                    if not required_keys.issubset(rule_dict.keys()):
                        missing = required_keys - rule_dict.keys()
                        raise TypeError(f"Missing required keys: {missing}")

                    # Handle potential datetime conversion if rules file stores them as strings
                    if "created" in rule_dict and isinstance(rule_dict["created"], str):
                        try:
                            rule_dict["created"] = datetime.fromisoformat(
                                rule_dict["created"].replace("Z", "+00:00")
                            )
                        except ValueError:
                            self.logger.warning(
                                f"Invalid ISO format for 'created' in rule {rule_dict.get('id', i + 1)}. Using current time."
                            )
                            # Decide on fallback: use current time or fail the rule?
                            rule_dict.pop("created", None)  # Remove invalid string
                    if "last_updated" in rule_dict and isinstance(rule_dict["last_updated"], str):
                        try:
                            rule_dict["last_updated"] = datetime.fromisoformat(
                                rule_dict["last_updated"].replace("Z", "+00:00")
                            )
                        except ValueError:
                            self.logger.warning(
                                f"Invalid ISO format for 'last_updated' in rule {rule_dict.get('id', i + 1)}. Using current time."
                            )
                            rule_dict.pop("last_updated", None)

                    rule = ValidationRule(**rule_dict)
                    if rule.id in loaded_rules:
                        self.logger.warning(
                            f"Duplicate rule ID '{rule.id}' found in {rules_path}. Overwriting."
                        )
                    loaded_rules[rule.id] = rule
                except (
                    TypeError,
                    ValueError,
                ) as te:  # Catches missing args, wrong types, datetime format errors
                    rule_id_str = rule_dict.get("id", f"entry #{i + 1}")
                    self.logger.error(
                        f"Error parsing validation rule '{rule_id_str}' in {rules_path}: {te}",
                        exc_info=False,  # Keep log concise for type/value errors
                    )
                except Exception as item_e:  # Catch unexpected errors during rule creation
                    rule_id_str = rule_dict.get("id", f"entry #{i + 1}")
                    self.logger.error(
                        f"Unexpected error parsing rule item '{rule_id_str}' in {rules_path}: {item_e}",
                        exc_info=True,
                    )

            self.rules = loaded_rules  # Atomically update rules
            self.logger.info(
                f"Successfully loaded {len(self.rules)} validation rules from {rules_path.name}"
            )

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in rules file: {rules_path}. Details: {e}")
            self.rules.clear()
        except IOError as e:
            self.logger.error(f"Error reading rules file {rules_path}: {e}", exc_info=True)
            self.rules.clear()
        except Exception as e:
            # Catch-all for other unexpected errors during loading
            self.logger.critical(
                f"Unexpected critical error loading validation rules file {rules_path}: {e}",
                exc_info=True,
            )
            self.rules.clear()  # Ensure safe state

    # --- Core Validation Logic --- #

    async def validate_action(
        self,
        action_context: Dict[str, Any],
        params: Dict[str, Any],  # Keep params even if unused for now, might be needed
        rule_ids: Optional[List[str]] = None,
    ) -> ValidationResult:
        """Validates a proposed action against defined rules.

        Args:
            action_context: Dictionary containing the context of the action to validate.
                            Expected to contain details needed by rule conditions.
            params: Additional parameters related to the action (currently unused placeholder).
            rule_ids: Optional list of specific rule IDs to apply. If None, applies all relevant rules.

        Returns:
            A ValidationResult object summarizing the outcome.
        """
        action_type = action_context.get("action_type", "Unknown Action")
        self.logger.info(f"Starting validation for action: {action_type}")

        applicable_rules = []
        if rule_ids:
            # Validate against a specific subset of rules
            for rule_id in rule_ids:
                rule = self.rules.get(rule_id)
                if rule:
                    if self._should_apply_rule(rule, action_context):
                        applicable_rules.append(rule)
                else:
                    self.logger.warning(f"Requested rule ID '{rule_id}' not found.")
        else:
            # Validate against all rules that should apply
            for rule in self.rules.values():
                if self._should_apply_rule(rule, action_context):
                    applicable_rules.append(rule)

        if not applicable_rules:
            self.logger.info(f"No applicable validation rules found for action: {action_type}")
            # Create a default passing result if no rules apply
            default_pass = ValidationResult(
                is_valid=True,
                action_taken="allowed",
                severity="none",
                score=1.0,
                details="No applicable rules found or executed.",
                rule_results=[],
                affected_components=action_context.get("affected_components", []),
                metadata=action_context.get("metadata", {}),
            )
            return default_pass

        self.logger.debug(f"Applying {len(applicable_rules)} rules for action: {action_type}")
        individual_results: List[Dict[str, Any]] = []
        try:
            # TODO: Consider running rule applications concurrently if they are I/O bound
            for rule in applicable_rules:
                rule_result = self._apply_rule(rule, action_context)
                individual_results.append(rule_result)

            # Consolidate results
            final_result = self._consolidate_results(individual_results, action_context)

        except Exception as e:
            self.logger.error(
                f"Critical error during rule application for {action_type}: {e}", exc_info=True
            )
            # Create a generic error result
            final_result = ValidationResult(
                is_valid=False,
                action_taken="error",
                severity="critical",
                score=0.0,
                details=f"Internal error during validation: {e}",
                rule_results=individual_results,  # Include results obtained before error
                affected_components=action_context.get("affected_components", []),
                metadata=action_context.get("metadata", {}),
                timestamp=datetime.now(timezone.utc),  # Ensure timestamp is set
            )

        # Record the final result (success or error state)
        self._process_validation_result(final_result)

        # Note: Alerting is currently handled by the calling Mycelium handler
        # based on the returned result and severity threshold.

        self.logger.info(
            f"Validation completed for {action_type}. Valid: {final_result.is_valid}, Action: {final_result.action_taken}"
        )
        return final_result

    def _should_apply_rule(self, rule: ValidationRule, action_context: Dict[str, Any]) -> bool:
        """Determines if a rule should be applied based on its conditions and the context.

        Args:
            rule: The ValidationRule object.
            action_context: The context of the action being validated.

        Returns:
            True if the rule should be applied, False otherwise.
        """
        # TODO: Implement actual condition evaluation logic.
        # This logic would parse rule.conditions (which might be strings,
        # DSL objects, etc.) and evaluate them against the action_context.

        # Placeholder: Apply all rules for now
        self.logger.debug(f"Checking applicability of rule '{rule.id}'. (Placeholder: Always True)")
        return True

    def _apply_rule(self, rule: ValidationRule, action_context: Dict[str, Any]) -> Dict[str, Any]:
        """Applies a single validation rule to the action context.

        Args:
            rule: The ValidationRule to apply.
            action_context: The context of the action being validated.

        Returns:
            A dictionary representing the result of this single rule application.
        """
        rule_result = {
            "rule_id": rule.id,
            "rule_name": rule.name,
            "is_valid": True,
            "score": 1.0,  # Default pass score
            "details": "Rule passed (Placeholder logic)",
            "action_suggested": "none",  # Action suggested by *this* rule
            "severity": rule.severity,  # Severity of the rule itself
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.logger.debug(f"Applying rule '{rule.id} ({rule.name})'...")

        try:
            # TODO: Implement the core validation logic for the rule here.
            # This involves evaluating rule.conditions against action_context.
            # The evaluation should determine the 'score' and 'is_valid' status.
            # Based on the score and rule.threshold, determine if the rule fails.

            # --- Placeholder Evaluation Logic --- #
            # Simulate a check based on keywords in context (very basic example)
            conditions_met_count = 0
            content_str = str(action_context.get("content", "")).lower()
                for condition in rule.conditions:
                if condition.lower() in content_str:
                    conditions_met_count += 1

            # Example scoring logic - lower score if conditions are met (inverted logic)
            # Ensure threshold is handled as float throughout
            try:
                threshold_float = float(rule.threshold)
            except (ValueError, TypeError) as conv_err:
                self.logger.error(
                    f"Invalid threshold value '{rule.threshold}' for rule '{rule.id}'. "
                    f"Cannot convert to float: {conv_err}",
                    exc_info=False,
                )
                # Mark rule as invalid due to configuration error
                rule_result["is_valid"] = False
                rule_result["score"] = 0.0
                rule_result["details"] = "Rule configuration error: Invalid threshold value."
                rule_result["action_suggested"] = "error"  # Treat as an error state
                # Skip further evaluation using threshold_float for this rule
                self.logger.debug(
                    f"Rule '{rule.id}' application result: Invalid config (threshold)"
                )
                return rule_result

            if conditions_met_count > 0 and len(rule.conditions) > 0:
                # Simulate score based on conditions met relative to threshold
                # This scoring logic is arbitrary and needs proper definition.
                simulated_score = threshold_float - (conditions_met_count * 0.1)
                rule_result["score"] = max(0.0, simulated_score)  # Ensure score >= 0
            else:
                rule_result["score"] = 1.0  # Passed if no conditions met
            # --- End Placeholder Logic --- #

            # Determine validity based on score and threshold
            # Now threshold_float is guaranteed to be a float if we reach this point
            if rule_result["score"] < threshold_float:
                rule_result["is_valid"] = False
                rule_result["details"] = (
                    f"Rule failed. Score {rule_result['score']:.2f} < threshold {threshold_float:.2f}. "
                    f"(Conditions met: {conditions_met_count}/{len(rule.conditions)} - Placeholder)"
                )
                rule_result["action_suggested"] = rule.action
                self.logger.info(f"Rule '{rule.id}' failed: {rule_result['details']}")
            else:
                rule_result["is_valid"] = True
                rule_result["details"] = "Rule passed (Placeholder logic)"
                rule_result["action_suggested"] = "none"

        except Exception as e:
            self.logger.error(f"Error applying rule '{rule.id}': {e}", exc_info=True)
            rule_result["is_valid"] = False
            rule_result["score"] = 0.0
            rule_result["details"] = f"Error during rule application: {e}"
            rule_result["action_suggested"] = "error"

        self.logger.debug(
            f"Rule '{rule.id}' application result: Valid={rule_result['is_valid']}, Score={rule_result['score']:.2f}"
        )
        return rule_result

    def _consolidate_results(
        self, rule_results: List[Dict[str, Any]], action_context: Dict[str, Any]
    ) -> ValidationResult:
        """Consolidates results from multiple rule applications into a single ValidationResult.

        Args:
            rule_results: A list of dictionaries, result from `_apply_rule`.
            action_context: The original action context.

        Returns:
            A final ValidationResult instance.
        """
        if not rule_results:
            self.logger.warning("Consolidating results called with an empty list.")
            return ValidationResult(
                is_valid=True,
                action_taken="allowed",
                severity="none",
                score=1.0,
                details="No rule results to consolidate.",
                rule_results=[],
                affected_components=action_context.get("affected_components", []),
                metadata=action_context.get("metadata", {}),
            )

        final_is_valid = True
        final_score = 1.0
        final_details = []
        final_action = "allowed"
        highest_severity_level = 0
        final_severity_str = "none"
        severity_map_to_level = {
            "none": 0,
            "log": 1,
            "warn": 2,
            "block": 3,
            "critical": 4,
            "error": 4,
        }
        level_to_severity_str = {v: k for k, v in severity_map_to_level.items()}

        for res in rule_results:
            if not res.get("is_valid", True):
                final_is_valid = False
                detail_msg = f"Rule '{res.get('rule_name', res.get('rule_id'))}': {res.get('details', 'Failed')}"
                final_details.append(detail_msg)
                action_suggested = res.get("action_suggested", "log").lower()
                current_severity_level = severity_map_to_level.get(action_suggested, 1)
                if current_severity_level > highest_severity_level:
                    highest_severity_level = current_severity_level
                    final_action = action_suggested
                    final_severity_str = res.get("severity", "low").lower()
            final_score = min(final_score, res.get("score", 1.0))

        if final_is_valid:
            final_details_str = "All applicable rules passed."
        else:
            final_details_str = "; ".join(final_details)
            if final_severity_str == "none":
                failed_severities = [
                    severity_map_to_level.get(r.get("severity", "low").lower(), 1)
                    for r in rule_results
                    if not r.get("is_valid")
                ]
                max_sev = max(failed_severities) if failed_severities else 0
                final_severity_str = level_to_severity_str.get(max_sev, "low")

        affected_components = set(action_context.get("affected_components", []))

        consolidated_result = ValidationResult(
            is_valid=final_is_valid,
            action_taken=final_action,
            severity=final_severity_str,
            score=final_score,
            details=final_details_str,
            rule_results=rule_results,
            affected_components=list(affected_components),
            metadata=action_context.get("metadata", {}),
        )
        self.logger.debug(
            f"Consolidated Result: Valid={final_is_valid}, Action={final_action}, "
            f"Severity={final_severity_str}, Score={final_score:.2f}"
        )
        return consolidated_result

    def _process_validation_result(self, result: ValidationResult) -> None:
        """Processes a final validation result: logs it and adds it to history.

        Args:
            result: The final ValidationResult object.
        """
        self.validation_history.append(result)
        if len(self.validation_history) > self.max_history:
            try:
            self.validation_history.pop(0)
            except IndexError:
                pass

        log_level = logging.INFO if result.is_valid else logging.WARNING
        self.logger.log(
            log_level,
            f"Validation Outcome: Valid={result.is_valid}, Score={result.score:.2f}, "
            f"ActionTaken={result.action_taken}, Severity={result.severity}, "
            f"Details: {result.details}",
        )

    # --- Other Potential Methods (Placeholders/Examples) --- #

    def add_rule(self, rule_dict: Dict[str, Any]) -> bool:
        """Adds or updates a validation rule dynamically.

        Args:
            rule_dict: A dictionary representing the rule.

        Returns:
            True if the rule was added/updated successfully, False otherwise.
        """
        try:
            if "id" not in rule_dict:
                raise ValueError("Rule dictionary must contain an 'id' key.")
            rule_dict["last_updated"] = datetime.now(timezone.utc)
            if "created" in rule_dict and isinstance(rule_dict["created"], str):
                try:
                    rule_dict["created"] = datetime.fromisoformat(
                        rule_dict["created"].replace("Z", "+00:00")
                    )
                except ValueError:
                    self.logger.warning(
                        f"Invalid format for 'created' in rule {rule_dict['id']}, using current time."
                    )
                    rule_dict["created"] = datetime.now(timezone.utc)
            if isinstance(rule_dict.get("last_updated"), str):
                try:
                    rule_dict["last_updated"] = datetime.fromisoformat(
                        rule_dict["last_updated"].replace("Z", "+00:00")
                    )
                except ValueError:
                    self.logger.warning(
                        f"Invalid format for 'last_updated' in rule {rule_dict['id']}, using current time."
                    )
                    rule_dict["last_updated"] = datetime.now(timezone.utc)

            rule = ValidationRule(**rule_dict)
            self.rules[rule.id] = rule
            self.logger.info(f"Dynamically added/updated rule ID: {rule.id} ('{rule.name}')")
            return True
        except (TypeError, ValueError) as e:
            self.logger.error(
                f"Failed to add/update rule from dict: {e}. Data: {rule_dict}", exc_info=False
            )
            return False
        except Exception as e:
            self.logger.error(
                f"Unexpected error adding/updating rule {rule_dict.get('id', 'N/A')}: {e}",
                exc_info=True,
            )
            return False

    def remove_rule(self, rule_id: str) -> bool:
        """Removes a validation rule dynamically.

        Args:
            rule_id: The ID of the rule to remove.

        Returns:
            True if the rule was found and removed, False otherwise.
        """
        if rule_id in self.rules:
            removed_rule_name = self.rules[rule_id].name
            del self.rules[rule_id]
            self.logger.info(f"Dynamically removed rule ID: {rule_id} ('{removed_rule_name}')")
            return True
        else:
            self.logger.warning(f"Attempted to remove non-existent rule ID: {rule_id}")
            return False

    def get_validation_history(self, limit: Optional[int] = 100) -> List[ValidationResult]:
        """Retrieves recent validation history.

        Args:
            limit: The maximum number of history entries to return. If None or <=0, returns all.

        Returns:
            A list of ValidationResult objects (copy).
        """
        if limit is None or limit <= 0:
            return list(self.validation_history)
        return list(self.validation_history[-limit:])


# Final cleanup - remove the placeholder comment at the end if present
# Remove this line if it exists: # ... (Rest of the file needs standardization) ...

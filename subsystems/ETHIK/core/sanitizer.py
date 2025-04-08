#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - ETHIK Sanitizer
==============================

Automated ethical content sanitization system.
Ensures all content and actions meet ethical standards.

Version: 8.0.0
Ethical Awareness: 0.999
Love: 0.999
"""

import asyncio
import concurrent.futures
from dataclasses import asdict, dataclass, field
import datetime
import hashlib
import json
import logging
from pathlib import Path
from queue import PriorityQueue
import re
from typing import Any, Dict, List, Optional, Tuple

# Import Mycelium Interface (adjust path if necessary)
from subsystems.MYCELIUM.core.interface import MyceliumInterface


@dataclass
class SanitizationRule:
    """Defines an ethical sanitization rule"""

    id: str
    name: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    patterns: List[str]  # Regex patterns to match
    replacements: Dict[str, str]  # Pattern -> replacement mapping
    conditions: List[str]  # Additional conditions
    created: datetime.datetime = field(default_factory=datetime.datetime.now)
    last_updated: datetime.datetime = field(default_factory=datetime.datetime.now)


@dataclass
class SanitizationResult:
    """Result of content sanitization"""

    content_id: str
    timestamp: datetime.datetime
    original_content: str
    sanitized_content: str
    applied_rules: List[str]
    changes_made: List[Dict[str, Any]]
    ethical_score: float
    is_clean: bool
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EthikSanitizer:
    """Automated ethical content sanitization system - Adapted for Mycelium"""

    def __init__(
        self, config: Dict[str, Any], mycelium_interface: MyceliumInterface, logger: logging.Logger
    ):
        """Initialize the sanitizer with config, Mycelium interface, and a logger instance."""
        self.config = config  # Expect specific sanitizer_config section
        self.interface = mycelium_interface
        self.logger = logger  # Use the passed logger
        self.node_id = "ETHIK_SANITIZER"  # Or derive from config/ETHIK service
        self.rules: Dict[str, SanitizationRule] = {}
        self.sanitization_history: List[SanitizationResult] = []
        self.content_cache: Dict[str, SanitizationResult] = {}
        self.priority_queue = PriorityQueue()
        self.executor = None
        self.monitoring_active = False  # Added monitoring state

        # Load configuration (assuming config now contains sanitizer_config)
        # self.config already set from parameter

        # Initialize parallel processing
        if self.config.get("performance", {}).get("parallel_processing", {}).get("enabled", False):
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.config["performance"]["parallel_processing"].get("max_workers", 4)
            )

        # Load sanitization rules from external file
        self._load_rules()

        # Removed WebSocket initialization

        self.logger.info("ETHIK Sanitizer initialized using KoiosLogger.")  # Use self.logger

    # Removed _initialize_websocket, _handle_websocket_messages, _send_websocket_update

    async def start_monitoring(self):
        """Start listening for sanitization requests via Mycelium."""
        if self.monitoring_active:
            self.logger.warning("Sanitizer monitoring is already active")  # Use self.logger
            return

        self.logger.info(
            "ETHIK Sanitizer monitoring starting (Mycelium connection assumed active)..."
        )  # Use self.logger

        try:
            await self.interface.subscribe("request.ethik.sanitize", self.handle_sanitize_request)
            self.logger.info("Subscribed to 'request.ethik.sanitize' topic.")  # Use self.logger
            self.monitoring_active = True
            self.logger.info("ETHIK Sanitizer monitoring started.")  # Use self.logger
        except Exception as e:
            self.logger.error(
                f"Failed to subscribe to Mycelium topic: {e}", exc_info=True
            )  # Use self.logger
            return

    async def stop_monitoring(self):
        """Stop listening for Mycelium requests."""
        if not self.monitoring_active:
            return

        self.logger.info("Stopping ETHIK Sanitizer monitoring...")  # Use self.logger
        self.monitoring_active = False
        # Unsubscribe logic might be needed depending on MyceliumInterface implementation
        # await self.interface.unsubscribe("request.ethik.sanitize", self.handle_sanitize_request)
        self.logger.info("ETHIK Sanitizer monitoring stopped.")  # Use self.logger

    async def handle_sanitize_request(self, message: Dict[str, Any]):
        """Handle incoming sanitization requests from Mycelium."""
        request_id = message.get("id", "unknown")
        self.logger.info(f"Processing sanitization request: {request_id}")  # Use self.logger

        try:
            payload = message.get("payload", {})
            content_to_sanitize = payload.get("content")
            context = payload.get("context", {})

            if content_to_sanitize is None:
                raise ValueError("Missing 'content' in sanitization request payload")

            # Perform sanitization (can be sync or async)
            # Using async version if executor is configured
            if self.executor:
                result = await self.sanitize_content_async(content_to_sanitize, context)
            else:
                result = self.sanitize_content(content_to_sanitize, context)

            # Prepare response
            response_payload = asdict(result)  # Convert dataclass to dict
            response = {
                "type": "sanitization_response",
                "reference_id": request_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "payload": response_payload,
            }

            # Publish response
            await self.interface.publish(
                topic=f"response.sanitization.{request_id}", message=response
            )
            self.logger.info(
                f"Sanitization complete for request {request_id}. Result published."
            )  # Use self.logger

        except Exception as e:
            self.logger.error(
                f"Error handling sanitization request {request_id}: {e}", exc_info=True
            )  # Use self.logger
            # Send error response
            try:
                await self.interface.publish(
                    topic=f"response.sanitization.{request_id}",
                    message={
                        "type": "sanitization_error",
                        "reference_id": request_id,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "error": str(e),
                    },
                )
            except Exception as pub_e:
                self.logger.error(
                    f"Failed to publish error response for {request_id}: {pub_e}"
                )  # Use self.logger

    def _update_cache(self, result: SanitizationResult):
        """Update the sanitization cache using priority queue"""
        try:
            # Calculate priority based on usage and importance
            priority = self._calculate_cache_priority(result)

            # Add to priority queue
            self.priority_queue.put((priority, result.content_id))

            # Add to cache
            self.content_cache[result.content_id] = result

            # Clean cache if needed
            self._clean_cache_if_needed()
        except Exception as e:
            self.logger.error(f"Error updating cache: {e}")  # Use self.logger

    def _calculate_cache_priority(self, result: SanitizationResult) -> float:
        """Calculate cache priority for a result"""
        priority = 0.0

        # Factor 1: Ethical score (higher score = higher priority)
        priority += result.ethical_score * 0.4

        # Factor 2: Usage frequency (from metadata)
        usage_count = result.metadata.get("usage_count", 0)
        priority += min(usage_count / 100, 0.3)

        # Factor 3: Resource intensity (lower is better)
        resource_usage = result.resource_usage.get("cpu_usage", 0)
        priority += 1 - min(resource_usage / 100, 0.3)

        return priority

    def _clean_cache_if_needed(self):
        """Clean cache if it exceeds max size"""
        max_size = self.config.get("performance", {}).get("caching", {}).get("max_size", 500)
        while len(self.content_cache) > max_size:
            # Remove lowest priority item
            _, content_id = self.priority_queue.get()
            if content_id in self.content_cache:
                del self.content_cache[content_id]

    async def sanitize_content_async(
        self, content: str, context: Optional[Dict[str, Any]] = None
    ) -> SanitizationResult:
        """Asynchronous version of sanitize_content"""
        context = context or {}
        if self.executor:
            # Run sanitization in thread pool
            return await asyncio.get_event_loop().run_in_executor(
                self.executor, self.sanitize_content, content, context
            )
        # If no executor, run synchronously but maintain async signature
        return self.sanitize_content(content, context)

    def sanitize_content(
        self, content: str, context: Optional[Dict[str, Any]] = None
    ) -> SanitizationResult:
        """
        Sanitize content according to ethical rules

        Args:
            content: Content to sanitize
            context: Optional context information
        """
        context = context or {}
        start_time = datetime.datetime.now()
        content_id = hashlib.md5(content.encode()).hexdigest()

        # Check cache
        if self.config.get("performance", {}).get("caching", {}).get("enabled", False):
            if content_id in self.content_cache:
                cached_result = self.content_cache[content_id]
                # Update usage count in metadata (assuming it exists)
                cached_result.metadata["usage_count"] = (
                    cached_result.metadata.get("usage_count", 0) + 1
                )
                self._update_cache(cached_result)  # Update priority
                self.logger.info(f"Returning cached result for content ID: {content_id}")
                return cached_result

        # Start timer for performance measurement
        # process_start_time = datetime.datetime.now() # F841: Unused variable

        # Initialize variables
        sanitized = content
        applied_rules: List[str] = []
        changes_made: List[Dict[str, Any]] = []
        ethical_score = 1.0  # Start with perfect score

        try:
            # Apply each rule
            for _rule_id, rule in self.rules.items():
                if self._should_apply_rule(rule, context):
                    sanitized, rule_changes = self._apply_rule(rule, sanitized)
                    if rule_changes:
                        applied_rules.append(rule.id)
                        changes_made.extend(rule_changes)
                        # Adjust ethical score based on rule severity
                        if rule.severity == "critical":
                            ethical_score -= 0.5
                        elif rule.severity == "high":
                            ethical_score -= 0.2
                        elif rule.severity == "medium":
                            ethical_score -= 0.1
                        else:
                            ethical_score -= 0.05

            # Ensure score doesn't go below 0
            ethical_score = max(0.0, ethical_score)

        except Exception as e:
            self.logger.error(f"Error applying rules to content {content_id}: {e}", exc_info=True)
            # Create an error result
            return self._create_error_result(content_id, content, str(e))

        # Update resource usage
        end_time = datetime.datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        resource_usage = {
            "start_time": start_time.isoformat(),
            "cpu_usage": 0,  # Placeholder - actual measurement might need psutil or similar
            "memory_usage": 0,  # Placeholder
        }
        resource_usage.update(
            {"end_time": end_time.isoformat(), "processing_time": processing_time}
        )

        # Create result
        result = SanitizationResult(
            content_id=content_id,
            timestamp=end_time,
            original_content=content,
            sanitized_content=sanitized,
            applied_rules=applied_rules,
            changes_made=changes_made,
            ethical_score=ethical_score,
            is_clean=len(changes_made) == 0,
            performance_metrics={
                "processing_time": processing_time,
                "rules_applied": len(applied_rules),
                "cache_hit": False,  # Since we are past the cache check
            },
            resource_usage=resource_usage,
            metadata={"usage_count": 1, "context": context},  # Include context in metadata
        )

        # Update cache
        self._update_cache(result)

        # Add to history
        self.sanitization_history.append(result)
        self._clean_history()  # Clean history periodically

        # Removed direct WebSocket update call

        self.logger.debug(
            f"Sanitization finished for content_id: {content_id}. Score: {result.ethical_score:.2f}"
        )
        return result

    def _should_apply_rule(self, rule: SanitizationRule, context: Optional[Dict[str, Any]]) -> bool:
        """Determine if a rule should be applied based on conditions"""
        if not context or not rule.conditions:  # Apply if no context or no conditions specified
            return True

        try:
            # Evaluate conditions using a restricted environment
            allowed_builtins = {
                "True": True,
                "False": False,
                "None": None,
                "len": len,
                "in": lambda x, y: x in y,
            }
            eval_globals = {"__builtins__": allowed_builtins, "context": context}

            for condition in rule.conditions:
                # If any condition evaluates to False, rule should not apply
                if not eval(condition, eval_globals):
                    self.logger.debug(
                        f"Rule {rule.id} condition not met: '{condition}' with context: {context}"
                    )  # Use self.logger
                    return False
            # If all conditions evaluated to True (or list was empty)
            self.logger.debug(
                f"Rule {rule.id} conditions met for context: {context}"
            )  # Use self.logger
            return True
        except Exception as e:
            self.logger.error(
                f"Error evaluating rule {rule.id} conditions: {e}. Context: {context}",
                exc_info=True,
            )  # Use self.logger
            return False  # Default to not applying if condition evaluation fails

    def _apply_rule(self, rule: SanitizationRule, content: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Apply a sanitization rule to content"""
        changes = []
        # Use a temporary variable to accumulate changes for this rule
        current_content = content
        offset = 0  # Track offset due to replacements

        try:
            # Apply each pattern
            for pattern in rule.patterns:
                # Find all non-overlapping matches
                for match in re.finditer(pattern, current_content):
                    original = match.group(0)
                    # Use pattern-specific replacement or default
                    replacement = rule.replacements.get(pattern, "[REDACTED]")

                    # Calculate original position in the initial content string
                    start_pos = match.start() + offset
                    end_pos = match.end() + offset

                    # Apply replacement
                    current_content = (
                        current_content[: match.start()]
                        + replacement
                        + current_content[match.end() :]
                    )

                    # Record change with original positions
                    changes.append(
                        {
                            "rule_id": rule.id,
                            "pattern": pattern,
                            "original": original,
                            "replacement": replacement,
                            "position": (start_pos, end_pos),  # Position in original content
                        }
                    )

                    # Update offset for subsequent matches in this iteration
                    offset += len(replacement) - len(original)

            # Return the content modified by this rule and the changes made
            return current_content, changes
        except Exception as e:
            self.logger.error(
                f"Error applying rule {rule.id}: {e}", exc_info=True
            )  # Use self.logger
            # Return original content and no changes if error occurs
            return content, []

    def _create_empty_result(self) -> SanitizationResult:
        """Create an empty sanitization result for empty input"""
        return SanitizationResult(
            content_id="empty_input",
            timestamp=datetime.datetime.now(),
            original_content="",
            sanitized_content="",
            applied_rules=[],
            changes_made=[],
            ethical_score=1.0,
            is_clean=True,
        )

    def _create_error_result(
        self, content_id: str, original_content: str, error_message: str
    ) -> SanitizationResult:
        """Create a sanitization result indicating an error"""
        return SanitizationResult(
            content_id=content_id,
            timestamp=datetime.datetime.now(),
            original_content=original_content,
            sanitized_content=original_content,  # Return original on error
            applied_rules=[],
            changes_made=[],
            ethical_score=0.0,  # Indicate failure
            is_clean=False,
            metadata={"error": error_message},
        )

    def _load_rules(self):
        """Loads sanitization rules from the configured JSON file using the absolute path."""
        rules_file_abs_path_str = self.config.get("rules_file")

        if not rules_file_abs_path_str:
            self.logger.error(
                "Absolute path for sanitization rules file not found in configuration."
            )  # Use self.logger
            self.rules.clear()
            return

        rules_path = Path(rules_file_abs_path_str)

        self.logger.info(
            f"Attempting to load sanitization rules from: {rules_path}"
        )  # Use self.logger
        if rules_path.exists() and rules_path.is_file():
            try:
                with open(rules_path, "r", encoding="utf-8") as f:
                    rules_data = json.load(f)

                self.rules.clear()  # Clear existing rules before loading
                for rule_dict in rules_data.get("rules", []):
                    try:
                        # Use default_factory for datetimes
                        rule_args = {
                            k: v
                            for k, v in rule_dict.items()
                            if k not in ["created", "last_updated"]
                        }
                        rule = SanitizationRule(**rule_args)
                        self.rules[rule.id] = rule
                    except TypeError as te:
                        self.logger.error(
                            f"Error creating SanitizationRule instance for rule ID "
                            f"'{rule_dict.get('id')}': Missing or invalid arguments - {te}",
                            exc_info=True,
                        )
                    except Exception as item_e:
                        self.logger.error(
                            f"Error parsing sanitization rule item {rule_dict.get('id')}: {item_e}",
                            exc_info=True,
                        )  # Use self.logger
                self.logger.info(
                    f"Loaded {len(self.rules)} sanitization rules from {rules_path.name}"
                )  # Use self.logger
            except json.JSONDecodeError:
                self.logger.error(f"Invalid JSON in rules file: {rules_path}")  # Use self.logger
            except Exception as e:
                self.logger.error(
                    f"Error loading sanitization rules file {rules_path}: {e}", exc_info=True
                )  # Use self.logger
                self.rules.clear()  # Clear rules on error
        else:
            self.logger.warning(
                f"Sanitization rules file not found: {rules_path}. Sanitizer will have no rules."
            )  # Use self.logger
            self.rules.clear()  # Ensure rules are empty if file not found

    def add_rule(self, rule_dict: Dict[str, Any]):
        """Add or update a sanitization rule dynamically."""
        try:
            # Validate rule_dict structure before creating object?
            rule_args = {k: v for k, v in rule_dict.items() if k not in ["created", "last_updated"]}
            rule = SanitizationRule(**rule_args)
            rule.last_updated = datetime.datetime.now()  # Update timestamp
            self.rules[rule.id] = rule
            self.logger.info(
                f"Added/Updated sanitization rule: {rule.name} [{rule.id}]"
            )  # Use self.logger
            # Consider saving rules back to file if dynamic updates should persist
        except Exception as e:
            self.logger.error(
                f"Error adding/updating rule {rule_dict.get('id')}: {e}", exc_info=True
            )  # Use self.logger

    def remove_rule(self, rule_id: str):
        """Remove a sanitization rule dynamically."""
        if rule_id in self.rules:
            removed_rule_name = self.rules[rule_id].name
            del self.rules[rule_id]
            self.logger.info(
                f"Removed sanitization rule: {removed_rule_name} [{rule_id}]"
            )  # Use self.logger
            # Consider saving rules back to file if dynamic updates should persist
        else:
            self.logger.warning(
                f"Attempted to remove non-existent rule: {rule_id}"
            )  # Use self.logger

    def get_sanitization_history(
        self,
        limit: int = 100,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
    ) -> List[SanitizationResult]:
        """Get sanitization history with optional time filters and limit."""
        # Apply filtering first
        results = self.sanitization_history
        if start_time:
            results = [r for r in results if r.timestamp >= start_time]
        if end_time:
            results = [r for r in results if r.timestamp <= end_time]

        # Apply limit to the filtered results (most recent first)
        return results[-limit:]

    def _clean_history(self):
        """Clean sanitization history based on retention policy."""
        retention_days = self.config.get("history_retention_days", 30)
        if retention_days <= 0:  # 0 or negative means infinite retention
            return

        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)

        initial_count = len(self.sanitization_history)
        self.sanitization_history = [
            r for r in self.sanitization_history if r.timestamp > cutoff_date
        ]
        removed_count = initial_count - len(self.sanitization_history)
        if removed_count > 0:
            self.logger.debug(
                f"Cleaned {removed_count} old entries from sanitization history."
            )  # Use self.logger

    def clear_history(self, older_than: Optional[datetime.datetime] = None):
        """Clear sanitization history manually."""
        initial_count = len(self.sanitization_history)
        if older_than:
            self.sanitization_history = [
                r for r in self.sanitization_history if r.timestamp > older_than
            ]
            removed_count = initial_count - len(self.sanitization_history)
            self.logger.info(
                f"Cleared {removed_count} sanitization history entries older than {older_than}."
            )  # Use self.logger
        else:
            self.sanitization_history = []
            self.logger.info(
                f"Cleared all {initial_count} sanitization history entries."
            )  # Use self.logger


# Example usage (if run directly - requires mock MyceliumInterface)
if __name__ == "__main__":
    # This section is for basic testing/demonstration if needed
    # Requires creating a mock MyceliumInterface class
    # --- Setup Basic Logging for Example --- #
    # Re-add basic config here only for standalone run, using the original module logger name
    logger = logging.getLogger("ethik_sanitizer")
    handler = logging.StreamHandler()
    formatter = logging.Formatter("💫 %(asctime)s - [ETHIK Sanitizer] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    # --------------------------------------- #

    class MockMyceliumInterface:
        async def publish(self, topic, message):
            print(f"Mock Publish to {topic}: {message}")

        async def subscribe(self, topic, handler):
            print(f"Mock Subscribe to {topic}")

    mock_config = {
        "sanitizer_config": {"rules_file": "../config/sanitization_rules.json"},  # Adjust if needed
        "performance": {"caching": {"max_size": 10}},
        "history_retention_days": 1,
    }

    async def run_test():
        mock_interface = MockMyceliumInterface()
        # Pass the standalone logger to the constructor for this example run
        sanitizer = EthikSanitizer(mock_config, mock_interface, logger)
        await sanitizer.start_monitoring()  # To test subscription logging

        print("\n--- Testing Sanitization ---")
        test_content = "This content contains a sensitive_word and maybe a BAD_WORD."
        context = {"user_level": "admin"}
        result = sanitizer.sanitize_content(test_content, context)
        print(f"Original: '{result.original_content}'")
        print(f"Sanitized: '{result.sanitized_content}'")
        print(f"Is Clean: {result.is_clean}")
        print(f"Score: {result.ethical_score}")
        print(f"Applied Rules: {result.applied_rules}")
        print(f"Changes: {result.changes_made}")

        print("\n--- Testing Cache ---")
        # result_cached = sanitizer.sanitize_content(
        #     test_content, context
        # ) # Removed unused variable
        # Check performance metrics for cache hit (would require adding 'cache_hit' logic)

        print("\n--- Testing History ---")
        history = sanitizer.get_sanitization_history(limit=5)
        print(f"History Count: {len(history)}")

        await sanitizer.stop_monitoring()

    # Requires an event loop to run async functions
    asyncio.run(run_test())

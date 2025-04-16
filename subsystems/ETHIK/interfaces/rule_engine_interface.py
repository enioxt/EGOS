from abc import ABC, abstractmethod
from typing import Dict, Any

# Assuming ValidationRule is defined elsewhere (e.g., ETHIK core)
from ..core.validator import ValidationRule # Adjust import path as needed

class RuleEngineInterface(ABC):
    """Interface for different ethical rule evaluation engines."""

    @abstractmethod
    def evaluate(self, rule: ValidationRule, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates a single rule against a given context.

        Args:
            rule: The ValidationRule to evaluate.
            context: The context dictionary against which conditions are checked.

        Returns:
            A dictionary representing the evaluation result for this rule,
            typically including keys like 'is_valid', 'score', 'details'.
        """
        pass

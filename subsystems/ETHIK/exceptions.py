# subsystems/ETHIK/exceptions.py

"""Custom exceptions for the ETHIK subsystem."""


class EthikException(Exception):
    """Base exception for all ETHIK subsystem errors."""

    pass


class EthikConfigurationError(EthikException):
    """Error related to ETHIK configuration or setup."""

    pass


class EthikProcessingError(EthikException):
    """General error during ETHIK processing or checking."""

    pass


class EthikViolationError(EthikProcessingError):
    """Raised when an ethical guideline or policy is violated.

    Attributes:
        violation_type: A code or description of the violation
                        (e.g., 'PII_DETECTED', 'FORBIDDEN_TOPIC').
        details: Additional details about the violation.
    """

    def __init__(
        self,
        message: str,
        violation_type: str = "UNKNOWN",
        details: str = "No details provided.",
    ):
        """Initialize the EthikViolationError.

        Args:
            message: The main error message.
            violation_type: The type code for the violation.
            details: Specific details about the violation instance.
        """
        super().__init__(message)
        self.violation_type: str = violation_type
        self.details: str = details

    def __str__(self) -> str:
        """Return a string representation of the exception."""
        base_message = super().__str__()
        return f"{base_message} [Type: {self.violation_type}, Details: {self.details}]"

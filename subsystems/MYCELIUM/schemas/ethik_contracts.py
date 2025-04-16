"""
Pydantic models defining the data contracts for ETHIK subsystem interactions
via the Mycelium Network.

Version: 1.0
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional

# --- Validation Contracts ---

class EthikValidationRequestV1(BaseModel):
    """
    Payload for requesting ethical validation of an action or content.
    Published to `request.ethik.validate.v1`.
    """
    request_id: str = Field(..., description="Unique identifier for tracking this validation request.")
    action_context: Dict[str, Any] = Field(..., description="Dictionary describing the action/content being validated. Keys might include 'action_type', 'content_summary', 'user_id', 'target_resource', etc.")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Optional additional parameters relevant to the validation logic.")
    rule_ids: Optional[List[str]] = Field(default=None, description="Optional list of specific rule IDs to apply. If None, applies the default ruleset.")

    @validator('action_context')
    def action_context_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('action_context must not be empty')
        return v

class EthikValidationResponseV1(BaseModel):
    """
    Payload containing the result of an ethical validation.
    Published to `response.ethik.validate.v1.{request_id}`.
    """
    request_id: str = Field(..., description="The unique identifier of the original validation request.")
    is_valid: bool = Field(..., description="Boolean indicating if the action/content passed validation.")
    action_taken: str = Field(..., description="The action ETHIK took based on validation (e.g., 'allowed', 'blocked', 'logged', 'allowed_with_warning').")
    severity: Optional[str] = Field(default=None, description="Severity level if validation failed or generated warnings (e.g., 'low', 'medium', 'high', 'critical').")
    score: Optional[float] = Field(default=None, description="Optional numerical score representing the validation outcome.")
    details: List[str] = Field(default_factory=list, description="List of strings providing details about violations or warnings.")
    error: Optional[str] = Field(default=None, description="Indicates if an error occurred during the validation process itself.")


# --- Sanitization Contracts ---

class EthikSanitizationRequestV1(BaseModel):
    """
    Payload for requesting content sanitization.
    Published to `request.ethik.sanitize.v1`.
    """
    request_id: str = Field(..., description="Unique identifier for tracking this sanitization request.")
    content: str = Field(..., description="The text content to be sanitized.")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional dictionary providing context about the content's source or purpose.")
    rule_ids: Optional[List[str]] = Field(default=None, description="Optional list of specific sanitization rule IDs to apply. If None, applies the default ruleset.")

class EthikSanitizationResponseV1(BaseModel):
    """
    Payload containing the result of content sanitization.
    Published to `response.ethik.sanitize.v1.{request_id}`.
    """
    request_id: str = Field(..., description="The unique identifier of the original sanitization request.")
    sanitized_content: str = Field(..., description="The content after applying sanitization rules.")
    actions_taken: List[Dict[str, Any]] = Field(default_factory=list, description="List of dictionaries detailing the specific sanitization actions performed (e.g., {'rule_id': 'pii_removal', 'action': 'replaced', 'details': 'Replaced email address'}).")
    error: Optional[str] = Field(default=None, description="Indicates if an error occurred during the sanitization process itself.")
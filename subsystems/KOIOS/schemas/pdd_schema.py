# subsystems/KOIOS/schemas/pdd_schema.py
"""Defines the Pydantic schema for Prompt Design Documents (PDDs).

This schema enforces a standardized structure for AI prompts used across EGOS,
primarily validated and managed by the CORUJA.PromptManager. It ensures
prompt consistency, reusability, maintainability, and provides essential
context (like parameters, versioning, and ethical guidelines) for reliable
AI interactions.

Version: 1.1
Last Updated: 2025-07-27
"""

from datetime import date
import re
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# Define the PddParameter model
class PddParameter(BaseModel):
    """Schema for a single input parameter within a PDD template."""

    name: str = Field(
        ...,
        description="Parameter name used in the template (e.g., '{parameter_name}'). Matches template placeholders.",
    )
    description: str = Field(
        ..., description="Clear explanation of the parameter's purpose and expected content."
    )
    type: Literal["string", "integer", "number", "boolean", "list", "object"] = Field(
        ..., description="Expected data type. Use 'list' for arrays, 'object' for dicts/mappings."
    )
    required: bool = Field(
        ..., description="If True, this parameter must be provided when using the prompt."
    )
    default: Optional[Any] = Field(
        None,
        description="Default value used if the parameter is not required and not provided. Must be None if required=True.",
    )

    @model_validator(mode="after")
    def check_default_value_requires_optional(cls, model: "PddParameter") -> "PddParameter":
        """Validate that default is None if parameter is required."""
        if model.required and model.default is not None:
            raise ValueError("Default value cannot be set for required parameters.")
        return model


class PddMetadata(BaseModel):
    """Schema for optional metadata providing context about the PDD."""

    author: Optional[str] = Field(None, description="Person or team who authored the PDD.")
    created_date: Optional[str] = Field(
        None, description="Date PDD was created (YYYY-MM-DD format)."
    )
    last_updated: Optional[str] = Field(
        None, description="Date PDD was last updated (YYYY-MM-DD format)."
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Keywords for categorization (e.g., 'code-gen', 'summary', 'refactor').",
    )
    related_pdds: List[str] = Field(
        default_factory=list,
        description="List of IDs (typically PDD filenames/stems) of related or dependent PDDs.",
    )

    @field_validator("created_date", "last_updated")
    @classmethod
    def check_date_format(cls, value: Optional[str]) -> Optional[str]:
        """Validate that dates, if provided, are in YYYY-MM-DD format."""
        if value is None:
            return value
        if not re.match(r"^\\d{4}-\\d{2}-\\d{2}$", value):
            raise ValueError("Date must be in YYYY-MM-DD format")
        try:
            # Further check if the date is valid (e.g., not 2023-02-30)
            year, month, day = map(int, value.split("-"))
            date(year, month, day)  # Will raise ValueError for invalid dates
        except ValueError:
            raise ValueError("Date must be a valid calendar date in YYYY-MM-DD format")
        return value


class PddEthikGuidelines(BaseModel):
    """Schema for ethical considerations and constraints for the prompt."""

    pii_handling: Literal["none", "redact", "error", "allow"] = Field(
        "error",  # Default to erroring if PII is detected
        description=(
            "Strategy for handling PII: 'none' (assume no PII), "
            "'redact' (attempt removal), 'error' (fail if detected), 'allow' (permit PII)."
        ),
    )
    bias_mitigation_ref: Optional[str] = Field(
        None, description="Reference ID or link to specific bias mitigation techniques applied."
    )
    forbidden_topics: List[str] = Field(
        default_factory=list,
        description="List of topics this prompt must strictly avoid generating content about.",
    )
    output_tone: Optional[str] = Field(
        None,
        description="Guidance on the desired tone for AI output (e.g., 'neutral', 'formal', 'empathetic').",
    )


class PromptDesignDocument(BaseModel):
    """
    The definitive schema for a Prompt Design Document (PDD).

    This structure defines the content, parameters, metadata, and ethical guidelines
    for an AI prompt within the EGOS ecosystem. It is the standard format used
    and validated by CORUJA's PromptManager.
    """

    id: str = Field(
        ...,
        description="Unique identifier (lowercase snake_case). Convention: Use filename stem (e.g., 'code_generation_basic').",
        pattern=r"^[a-z0-9_]+$",  # Ensure snake_case
    )
    name: str = Field(..., description="Human-readable name/title for the prompt.", min_length=5)
    description: str = Field(
        ...,
        description="Clear description of the prompt's purpose, use case, and expected outcome.",
        min_length=20,
    )
    version: str = Field(
        "1.0.0",  # Use SemVer standard
        description="Semantic version for this PDD (e.g., '1.0.0', '1.1.0').",
        pattern=r"^\\d+\\.\\d+\\.\\d+$",  # Validate SemVer basic format XXX.YYY.ZZZ
    )

    parameters: List[PddParameter] = Field(
        default_factory=list,
        description="Defines the input parameters expected by the template string.",
    )

    template: str = Field(
        ...,
        description="The core prompt template string. Use braces {} for parameter substitution (e.g., '{user_request}').",
        min_length=10,
    )

    metadata: PddMetadata = Field(
        default_factory=PddMetadata,  # Auto-create default metadata if not provided
        description="Contextual metadata (author, dates, tags, relations).",
    )
    ethik_guidelines: PddEthikGuidelines = Field(
        default_factory=PddEthikGuidelines,  # Auto-create default guidelines if not provided
        description="Ethical guidelines and operational constraints for the prompt.",
    )

    # Configuration specific to the AI model call for this prompt
    model_configuration: Optional[Dict[str, Any]] = Field(
        None,
        description=(
            "Optional dictionary of parameters (e.g., temperature, max_tokens, safety_settings) "
            "to override CORUJA's default model settings for this specific prompt."
        ),
    )

    # --- Validation ---
    @model_validator(mode="after")
    def check_template_parameters_match(
        cls, model: "PromptDesignDocument"
    ) -> "PromptDesignDocument":
        """Validate that all parameters defined are present in the template (basic check)."""
        template_vars = set(re.findall(r"\\{([^{}]+)\\}", model.template))
        defined_params = {p.name for p in model.parameters}

        missing_in_template = defined_params - template_vars
        if missing_in_template:
            # Warning rather than error, as parameters might be used indirectly
            print(
                f"Warning: PDD '{model.id}' defines parameters not found in template: {missing_in_template}"
            )
            # Consider raising ValueError if strict matching is required:
            # raise ValueError(f"Parameters defined but not found in template: {missing_in_template}")

        # Optional: Check if template uses vars not defined in parameters
        # extra_in_template = template_vars - defined_params
        # if extra_in_template:
        #     raise ValueError(f"Template uses parameters not defined: {extra_in_template}")

        return model

    # --- Future Fields Placeholder ---
    # ... (existing commented out fields remain for future consideration)

    class Config:
        extra = "forbid"  # Disallow fields not explicitly defined
        validate_assignment = True  # Re-validate on attribute assignment


# ✧༺❀༻∞ EGOS ∞༺❀༻✧

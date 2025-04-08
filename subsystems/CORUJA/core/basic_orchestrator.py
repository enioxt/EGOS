# subsystems/CORUJA/core/basic_orchestrator.py

"""Implements the Basic Orchestrator for handling PDD-based AI requests."""

from typing import Any, Dict, List, Optional

# Core dependencies - Adjust paths if needed based on final structure
from subsystems.CORUJA.core.prompt_manager import PddNotFoundError, PromptManager
from subsystems.CORUJA.interfaces.model_interface import (
    CorujaException,
    ModelApiException,
    ModelConfigurationError,
    ModelInterface,
    ModelRateLimitError,
    ModelResponse,
    ModelSafetyError,
    ModelTimeoutError,
)
from subsystems.ETHIK.exceptions import EthikProcessingError, EthikViolationError

# Import ETHIK interface and exceptions
from subsystems.ETHIK.interfaces.ethik_checker_interface import EthikCheckerInterface

# Using standard logging for now until KoiosLogger is fully integrated
# import logging # Remove standard logging import
from subsystems.KOIOS.core.logging import KoiosLogger  # Import KoiosLogger
from subsystems.KOIOS.schemas.pdd_schema import (
    PddEthikGuidelines,
    PddParameter,
    PromptDesignDocument,
)


class BasicOrchestrator:
    """
    Handles the basic workflow of executing an AI task defined by a PDD.

    Takes a request, retrieves the appropriate prompt using PromptManager,
    formats the prompt, executes it using a ModelInterface, applies
    ETHIK checks via an optional EthikCheckerInterface, and returns the result.
    This version treats each request independently without complex state management.
    """

    def __init__(
        self,
        prompt_manager: PromptManager,
        model_interface: ModelInterface,
        ethik_checker: Optional[EthikCheckerInterface] = None,
    ):
        """
        Initializes the BasicOrchestrator.

        Args:
            prompt_manager: An initialized instance of PromptManager.
            model_interface: A concrete, initialized instance of ModelInterface.
            ethik_checker: An optional initialized instance of EthikCheckerInterface.

        Raises:
            ValueError: If prompt_manager or model_interface is None.
        """
        # Replace with KoiosLogger once available and configured
        # self.logger = logging.getLogger("CORUJA.BasicOrchestrator")
        # Remove old logger instantiation
        self.logger = KoiosLogger.get_logger("CORUJA.BasicOrchestrator")  # Use KoiosLogger

        if not prompt_manager:
            self.logger.critical("Initialization failed: PromptManager instance is required.")
            raise ValueError("PromptManager instance is required.")
        if not model_interface:
            self.logger.critical("Initialization failed: ModelInterface instance is required.")
            raise ValueError("ModelInterface instance is required.")

        self.prompt_manager = prompt_manager
        self.model_interface = model_interface
        self.ethik_checker = ethik_checker  # Store the checker

        log_msg = (
            f"BasicOrchestrator initialized with PromptManager and "
            f"ModelInterface: {type(model_interface).__name__}"
        )
        if self.ethik_checker:
            log_msg += f", EthikChecker: {type(self.ethik_checker).__name__}"
        self.logger.info(log_msg)

    async def process_request(
        self,
        pdd_id: str,
        input_data: Dict[str, Any],
        model_params: Optional[Dict[str, Any]] = None,
        request_context: Optional[Dict[str, Any]] = None,
    ) -> ModelResponse:
        """
        Processes a request to execute an AI task defined by a PDD.

        Args:
            pdd_id: The unique identifier of the Prompt Design Document to use.
            input_data: Dictionary containing key-value pairs for prompt parameters.
            model_params: Optional dictionary of parameters for the model execution
                          (e.g., temperature, max_output_tokens). Defaults may be applied.
            request_context: Optional dictionary containing metadata about the request
                             (e.g., user_id, session_id, trace_id) for logging/ETHIK.

        Returns:
            A ModelResponse object containing the result from the language model.
            The response object's 'error' field will be populated if processing failed
            due to handled exceptions (e.g., PDD not found, safety error, ETHIK violation).
        """
        self.logger.info(f"Processing request for PDD ID: '{pdd_id}'")
        # Ensure context and params dicts exist for easier handling
        context = request_context or {}
        # Renamed from exec_params for clarity before merging
        runtime_model_params = model_params or {}

        try:
            # --- 1. Retrieve PDD ---
            pdd = self.prompt_manager.get_pdd(pdd_id)
            self.logger.debug(f"Retrieved PDD '{pdd_id}' version {pdd.version}")
            context["pdd_version"] = pdd.version
            context["pdd_id"] = pdd_id

            # --- 2. Validate Input Parameters ---
            # Pass the detailed PddParameter list from the schema
            validated_data = self._validate_parameters(pdd.parameters, input_data)
            self.logger.debug("Input parameters validated.")

            # --- 3. Apply Pre-Prompt ETHIK Checks ---
            # This also applies before branching to ensure input is sanitized regardless of handler.
            processed_data = self._apply_pre_prompt_ethik(
                validated_data, pdd.ethik_guidelines, context
            )

            # --- 4. Determine Handling Strategy ---
            # Check PDD for specialized handler fields (Task COR-ADV-01/02)
            handler_type = "standard_llm"  # Default
            handler_reference = None
            if pdd.metadata:
                handler_type = getattr(pdd.metadata, "handler_type", "standard_llm")
                handler_reference = getattr(pdd.metadata, "handler_reference", None)

            final_response: ModelResponse
            # --- Parameter Merging (Applies mainly to standard_llm path) ---
            # Start with defaults, override with PDD config, then runtime params
            merged_exec_params = self._get_default_model_params()
            # Ensure model_configuration exists and is a dict before updating
            if pdd.model_configuration and isinstance(pdd.model_configuration, dict):
                merged_exec_params.update(pdd.model_configuration)
            if runtime_model_params:  # Use the renamed variable
                merged_exec_params.update(runtime_model_params)
            self.logger.debug(f"Final execution parameters: {merged_exec_params}")

            # --- 5a. Specialized Handler Path ---
            if handler_type == "specialized_crew" and handler_reference:
                self.logger.info(
                    f"Routing PDD '{pdd_id}' to specialized handler: {handler_reference}"
                )
                try:
                    # TODO (Task COR-ADV-03): Implement dynamic handler loading
                    # For now, directly use the placeholder if reference matches
                    if handler_reference == "zendesk_analysis_crew_v1":
                        from subsystems.CORUJA.handlers.zendesk_analyzer_handler import (
                            ZendeskAnalysisHandler,
                        )

                        # Pass PDD's model_config to handler for its specific settings
                        specialized_handler = ZendeskAnalysisHandler(config=pdd.model_config)
                        # Note: Pass 'processed_data' from pre-ETHIK step
                        final_response = await specialized_handler.process(
                            processed_data, pdd, context
                        )
                    else:
                        self.logger.error(
                            f"Specialized handler '{handler_reference}' not found or not "
                            f"implemented for PDD '{pdd_id}'."
                        )
                        # Create an error response manually
                        final_response = ModelResponse(
                            text="",
                            error=f"Handler not found: {handler_reference}",
                            finish_reason="handler_not_found",
                        )
                    # Post-ETHIK check is still needed after handler execution
                    final_response = self._apply_post_response_ethik(
                        final_response, pdd.ethik_guidelines, context
                    )

                except ImportError as ie:
                    self.logger.exception(
                        f"Failed to import handler module for '{handler_reference}': {ie}"
                    )
                    final_response = ModelResponse(
                        text="",
                        error=f"Handler Import Error: Failed to load {handler_reference}.",
                        finish_reason="handler_import_error",
                    )
                except Exception as handler_ex:
                    # Catch unexpected errors during handler instantiation or processing
                    self.logger.exception(
                        f"Unexpected error during specialized handler execution "
                        f"('{handler_reference}'): {handler_ex}"
                    )
                    final_response = ModelResponse(
                        text="",
                        error=f"Handler Execution Error: {type(handler_ex).__name__}",
                        finish_reason="handler_execution_error",
                    )

            # --- 5b. Standard LLM Path ---
            elif handler_type == "standard_llm":
                self.logger.debug(f"Routing PDD '{pdd_id}' to standard ModelInterface.")

                # Render prompt (Only needed for standard path)
                rendered_prompt = self._render_prompt(pdd.template, processed_data)
                self.logger.debug("Prompt template rendered.")

                # Execute via standard ModelInterface using MERGED params
                self.logger.info(
                    f"Executing prompt using model interface: {type(self.model_interface).__name__}"
                )
                execution_context = context
                model_response = await self.model_interface.execute_prompt(
                    prompt=rendered_prompt,
                    params=merged_exec_params,  # Use merged parameters
                    context=execution_context,
                )
                self.logger.info(
                    f"Received response from model. Finish reason: "
                    f"{model_response.finish_reason}, Error: {model_response.error}"
                )

                # Apply Post-Response ETHIK Checks
                final_response = self._apply_post_response_ethik(
                    model_response, pdd.ethik_guidelines, context
                )

            # --- 5c. Unknown Handler Type ---
            else:
                self.logger.error(
                    f"Unknown handler_type '{handler_type}' specified in PDD '{pdd_id}'."
                )
                final_response = ModelResponse(
                    text="",
                    error=f"Unknown handler type: {handler_type}",
                    finish_reason="unknown_handler_type",
                )

            # --- 6. Log Interaction ---
            # Logging now happens after either path completes
            # Use 'processed_data' as input, 'exec_params' might need adjustment depending on path
            # TODO: Revisit what 'exec_params' means for specialized handlers
            self._log_interaction(pdd, processed_data, merged_exec_params, final_response, context)

            return final_response

        # --- Error Handling ---
        except PddNotFoundError:
            self.logger.error(f"Failed to process request: PDD '{pdd_id}' not found.")
            return ModelResponse(text="", error=f"PDD not found: {pdd_id}")
        except ValueError as e:  # Catches parameter validation or rendering errors
            self.logger.error(
                f"Input validation or rendering error for PDD '{pdd_id}': {e}", exc_info=True
            )
            return ModelResponse(text="", error=f"Input/Template error: {e}")
        except EthikViolationError as e:  # Catch ETHIK input violations
            self.logger.warning(f"ETHIK input violation processing PDD '{pdd_id}': {e}")
            return ModelResponse(
                text="",
                error=f"ETHIK input violation: {e}",
                finish_reason="ethik_violation_input",
            )
        except ModelSafetyError as e:
            self.logger.warning(f"Model safety error processing PDD '{pdd_id}': {e}")
            return ModelResponse(
                text="",
                error=f"Content safety issue: {e}",
                finish_reason="content_filter",
            )
        except ModelRateLimitError as e:
            self.logger.error(
                f"Model rate limit error processing PDD '{pdd_id}': {e}", exc_info=False
            )
            return ModelResponse(
                text="",
                error=f"Model rate limit exceeded: {e}",
            )
        except ModelTimeoutError as e:
            self.logger.error(f"Model timeout error processing PDD '{pdd_id}': {e}", exc_info=False)
            return ModelResponse(text="", error=f"Model timeout: {e}")
        except ModelConfigurationError as e:
            self.logger.critical(
                f"Model configuration error processing PDD '{pdd_id}': {e}", exc_info=True
            )
            return ModelResponse(text="", error=f"Model configuration error: {e}")
        except ModelApiException as e:
            self.logger.error(f"Model API error processing PDD '{pdd_id}': {e}", exc_info=True)
            return ModelResponse(
                text="",
                error=f"Model API error: {e}",
            )
        except Exception as e:
            self.logger.exception(f"Unexpected error processing PDD '{pdd_id}': {e}")
            return ModelResponse(text="", error=f"Unexpected orchestrator error: {e}")

    def _validate_parameters(
        self, pdd_params: List[PddParameter], input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validates input data against the PDD's parameter definitions.

        Checks for required parameters and basic type consistency.
        Applies default values if defined and parameter is missing.

        Args:
            pdd_params: The list of PddParameter definitions from the PDD schema.
            input_data: The dictionary of input data provided in the request.

        Returns:
            A dictionary containing the validated and potentially defaulted data.

        Raises:
            ValueError: If a required parameter is missing or if a parameter's type
                        does not match the expected type.
        """
        validated_output = {}
        provided_keys = set(input_data.keys())

        for param_def in pdd_params:
            param_name = param_def.name
            expected_type = param_def.type
            is_required = param_def.required
            default_value = param_def.default

            if param_name in provided_keys:
                value = input_data[param_name]
                # Basic Type Checking
                type_match = False
                if expected_type == "string" and isinstance(value, str):
                    type_match = True
                elif expected_type == "integer" and isinstance(value, int):
                    type_match = True
                elif expected_type == "number" and isinstance(value, (int, float)):
                    type_match = True
                elif expected_type == "boolean" and isinstance(value, bool):
                    type_match = True
                elif expected_type == "list" and isinstance(value, list):
                    type_match = True
                elif expected_type == "object" and isinstance(value, dict):
                    type_match = True
                # Allow None if not required (even if type specified)
                elif value is None and not is_required:
                    type_match = True

                if not type_match:
                    raise ValueError(
                        f"Type mismatch for parameter '{param_name}'. "
                        f"Expected {expected_type}, got {type(value).__name__}."
                    )
                validated_output[param_name] = value
                provided_keys.remove(param_name)  # Mark as processed
            elif is_required:
                # Parameter is required but not provided
                raise ValueError(f"Missing required parameter: '{param_name}'")
            elif default_value is not None:
                # Not required, not provided, but has a default
                self.logger.debug(f"Applying default value for optional parameter '{param_name}'")
                validated_output[param_name] = default_value
            # Else: Not required, not provided, no default - parameter is simply omitted

        # Check for any extra parameters provided that are not defined in the PDD
        # Depending on strictness, this could raise an error or just be logged.
        if provided_keys:  # Keys remaining were not defined in pdd_params
            self.logger.warning(
                f"Ignoring extra input parameters not defined in PDD: {provided_keys}"
            )
            # Optionally raise error for strict validation:
            # raise ValueError(f"Unexpected parameters provided: {provided_keys}")

        return validated_output

    def _render_prompt(self, template: str, data: Dict[str, Any]) -> str:
        """Renders the prompt template using basic string formatting.

        Raises:
            ValueError: If a parameter in the template is missing from the data.
            CorujaException: For other rendering errors.
        """
        try:
            return template.format(**data)
        except KeyError as e:
            msg = (
                f"Template rendering error: Parameter {e} defined in PDD template "
                f"was not found in the provided input data."
            )
            self.logger.error(msg)
            raise ValueError(msg) from e
        except Exception as e:
            msg = f"Unexpected template rendering error: {type(e).__name__}"
            self.logger.exception(msg)  # Log with traceback
            raise CorujaException(f"Failed to render prompt template: {e}") from e

    def _apply_pre_prompt_ethik(
        self, data: Dict[str, Any], guidelines: Optional[PddEthikGuidelines], context: Dict
    ) -> Dict[str, Any]:
        """Applies pre-prompt ETHIK checks using the configured EthikCheckerInterface.

        Args:
            data: The validated input data for the prompt.
            guidelines: The ethik_guidelines object from the PDD (if any).
            context: Request context metadata.

        Returns:
            The potentially modified data after checks/sanitization.

        Raises:
            EthikViolationError: If the input violates critical ETHIK guidelines as determined
                                 by the checker.
            EthikProcessingError: If the checker encounters an error during processing.
        """
        if self.ethik_checker:
            self.logger.debug(
                f"Applying pre-prompt ETHIK checks. Guidelines present: "
                f"{guidelines is not None}). Checker: {type(self.ethik_checker).__name__}"
            )
            try:
                # The checker might modify data (e.g., redaction) or raise an error
                processed_data = self.ethik_checker.check_and_sanitize_input(
                    data=data, guidelines=guidelines, context=context
                )
                self.logger.info("Pre-prompt ETHIK checks passed/applied.")
                return processed_data
            except EthikViolationError as e:
                # Log and re-raise for the main process_request loop to handle
                self.logger.warning(f"Pre-prompt ETHIK violation detected: {e}")
                raise e
            except EthikProcessingError as e:
                # Log but potentially allow continuation depending on severity?
                # For now, treat processing errors seriously too. Re-raise.
                # Or wrap in a CorujaException? Let's re-raise EthikProcessingError for now.
                self.logger.error(f"Error during pre-prompt ETHIK processing: {e}", exc_info=True)
                raise e
            except Exception as e:
                self.logger.exception("Unexpected error during pre-prompt ETHIK check.")
                raise CorujaException("Unexpected error during ETHIK input check") from e
        else:
            self.logger.debug("No ETHIK checker configured. Skipping pre-prompt checks.")
            return data  # Return original data if no checker

    def _apply_post_response_ethik(
        self, response: ModelResponse, guidelines: Optional[PddEthikGuidelines], context: Dict
    ) -> ModelResponse:
        """Applies post-response ETHIK checks using the configured EthikCheckerInterface.

        Args:
            response: The ModelResponse received from the ModelInterface.
            guidelines: The ethik_guidelines object from the PDD (if any).
            context: Request context metadata.

        Returns:
            The potentially modified ModelResponse after checks.
            The checker might modify response content, set the error field,
            or change the finish_reason.
        """
        if self.ethik_checker:
            self.logger.debug(
                f"Applying post-response ETHIK checks. Response error: {response.error}. "
                f"Guidelines present: {guidelines is not None}). "
                f"Checker: {type(self.ethik_checker).__name__}"
            )
            try:
                # The checker might modify the response object
                filtered_response = self.ethik_checker.check_and_filter_output(
                    response=response, guidelines=guidelines, context=context
                )
                self.logger.info("Post-response ETHIK checks passed/applied.")
                return filtered_response
            # Post-response violations might modify the response
            # rather than raising a blocking error
            # except EthikViolationError as e:
            except EthikProcessingError as e:
                self.logger.error(
                    f"Error during post-response ETHIK processing: {e}", exc_info=True
                )
                # Modify response to indicate error?
                response.error = f"ETHIK output processing error: {e}"
                response.finish_reason = "ethik_processing_error"
                return response  # Return response with error flagged
            except Exception:
                self.logger.exception("Unexpected error during post-response ETHIK check.")
                response.error = "Unexpected error during ETHIK output check"
                response.finish_reason = "internal_error"
                return response  # Return response with error flagged
        else:
            self.logger.debug("No ETHIK checker configured. Skipping post-response checks.")
            return response  # Return original response if no checker

    def _log_interaction(
        self,
        pdd: PromptDesignDocument,
        input_data: Dict,
        model_params: Dict,
        response: ModelResponse,
        context: Dict,
    ):
        """Logs the details of the interaction (placeholder for KoiosLogger structured logging)."""
        # Basic logging for now
        status = "SUCCESS" if not response.error else "FAILURE"
        log_msg = (
            f"INTERACTION LOG: Status=[{status}], PDD_ID=['{pdd.id}'], Version=['{pdd.version}'], "
            f"Model=['{response.model_name}'], FinishReason=['{response.finish_reason}'], "
            f"Error=['{response.error}']"
            # Avoid logging full input_data or response.text by default for privacy/verbosity
        )
        if status == "SUCCESS":
            self.logger.info(log_msg)
        else:
            self.logger.warning(log_msg)

        # --- TODO: Replace with KoiosLogger structured logging ---
        # koios_payload = {
        #      "interaction_type": "coruja_request",
        #      "pdd_id": pdd.id,
        #      "pdd_version": pdd.version,
        #      # "input_params_keys": list(input_data.keys()), # Log keys, not values
        #      "model_params": model_params,
        #      "model_name": response.model_name,
        #      "finish_reason": response.finish_reason,
        #      "token_usage": response.token_usage.model_dump() if response.token_usage else None,
        #      "response_error": response.error,
        #      "request_context": context,
        #      "status": status
        # }
        # self.logger.info("CORUJA interaction processed.", extra=koios_payload)
        # ----------------------------------------------------------

    def _get_default_model_params(self) -> Dict[str, Any]:
        """Returns default parameters for model execution."""
        # Define sensible defaults here
        return {
            "temperature": 0.7,
            "max_output_tokens": 1024,  # Example default
            # Add other potential defaults like top_p, top_k if needed
            # Consider default safety settings if not handled by the model interface itself
            # "safety_threshold": "BLOCK_MEDIUM_AND_ABOVE" # Example
        }

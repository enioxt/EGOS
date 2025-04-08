"""Concrete implementation of ModelInterface for Google's Gemini models."""

# Use standard logging until KoiosLogger is integrated
from abc import ABC, abstractmethod  # Added for mock interface
import os
import sys
from typing import Any, Dict, List, Optional

# Attempt to import the library, handle if not installed
try:
    import google.generativeai as genai
    from google.generativeai.types import (
        GenerationConfig,
        HarmBlockThreshold,
        HarmCategory,
    )

    # Try importing SafetySetting from its potential location
    try:
        from google.generativeai.types import SafetySetting
    except ImportError:
        from google.generativeai.types.safety_types import SafetySetting

    from google.api_core import exceptions as google_exceptions

    GOOGLE_AI_AVAILABLE = True
except ImportError:
    print("WARNING: google-generativeai library not found. Using mock objects.")
    GOOGLE_AI_AVAILABLE = False
    genai = None
    google_exceptions = None

    # Define mock classes needed for type checking and basic functionality
    class MockGoogleExceptions:
        GoogleAPIError = type("GoogleAPIError", (Exception,), {})
        PermissionDenied = type("PermissionDenied", (GoogleAPIError,), {})
        ResourceExhausted = type("ResourceExhausted", (GoogleAPIError,), {})
        InvalidArgument = type("InvalidArgument", (GoogleAPIError,), {})
        DeadlineExceeded = type("DeadlineExceeded", (GoogleAPIError,), {})

    google_exceptions = MockGoogleExceptions()

    class GenerationConfig:
        pass

    class HarmBlockThreshold:
        BLOCK_NONE = "BLOCK_NONE"
        BLOCK_ONLY_HIGH = "BLOCK_ONLY_HIGH"
        BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE"
        BLOCK_LOW_AND_ABOVE = "BLOCK_LOW_AND_ABOVE"

    class HarmCategory:
        HARM_CATEGORY_HARASSMENT = "HARM_CATEGORY_HARASSMENT"
        HARM_CATEGORY_HATE_SPEECH = "HARM_CATEGORY_HATE_SPEECH"
        HARM_CATEGORY_SEXUALLY_EXPLICIT = "HARM_CATEGORY_SEXUALLY_EXPLICIT"
        HARM_CATEGORY_DANGEROUS_CONTENT = "HARM_CATEGORY_DANGEROUS_CONTENT"

    class SafetySetting:
        def __init__(self, category=None, threshold=None):
            self.category = category
            self.threshold = threshold


# Adicionar diretório raiz ao PYTHONPATH para imports do projeto
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import necessary components from the interface definition
# Use try-except here as well in case tests run without full project structure
try:
    from subsystems.CORUJA.interfaces.model_interface import (
        AICommunicationError,
        AIConfigurationError,
        AIError,  # Keep other AIError types if used
        AIResponseError,
        CorujaException,
        ModelApiException,
        ModelConfigurationError,
        ModelInterface,  # Corrected import
        ModelRateLimitError,
        ModelResponse,
        ModelSafetyError,
        ModelTimeoutError,
    )
except ImportError:
    print("WARNING: Failed to import CORUJA interfaces. Using mock objects.")

    # Define mock interface and exceptions if import fails
    class ModelInterface(ABC):
        @abstractmethod
        async def execute_prompt(
            self, prompt: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None
        ) -> Any:
            pass

        @abstractmethod
        async def generate_response(self, prompt: str, **kwargs) -> str:
            pass

        @abstractmethod
        def count_tokens(self, text: str) -> int:
            pass

    class CorujaException(Exception):
        pass

    class AIConfigurationError(CorujaException):
        pass

    class ModelApiException(CorujaException):
        pass

    class ModelConfigurationError(AIConfigurationError):
        pass

    class ModelRateLimitError(ModelApiException):
        pass

    class ModelSafetyError(ModelApiException):
        pass

    class ModelTimeoutError(ModelApiException):
        pass

    class ModelResponse:  # Mock response object
        def __init__(self, text="", error=None, finish_reason=None, **kwargs):
            self.text = text
            self.error = error
            self.finish_reason = finish_reason

    class AIError(CorujaException):
        pass

    class AICommunicationError(AIError):
        pass

    class AIResponseError(AIError):
        pass


# Attempt to load GOOGLE_API_KEY from .env for local dev, if python-dotenv is installed
# In production, environment variables should be set directly.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, rely on system environment variables

# Mapping from generic HarmBlockThreshold names to genai constants
# Allow PDDs/params to specify thresholds like "BLOCK_MEDIUM_AND_ABOVE"
# Ensure HarmBlockThreshold exists before using it
SAFETY_THRESHOLD_MAP = (
    {
        "BLOCK_NONE": HarmBlockThreshold.BLOCK_NONE if GOOGLE_AI_AVAILABLE else "BLOCK_NONE",
        "BLOCK_ONLY_HIGH": HarmBlockThreshold.BLOCK_ONLY_HIGH
        if GOOGLE_AI_AVAILABLE
        else "BLOCK_ONLY_HIGH",
        "BLOCK_MEDIUM_AND_ABOVE": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        if GOOGLE_AI_AVAILABLE
        else "BLOCK_MEDIUM_AND_ABOVE",
        "BLOCK_LOW_AND_ABOVE": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
        if GOOGLE_AI_AVAILABLE
        else "BLOCK_LOW_AND_ABOVE",
    }
    if HarmBlockThreshold
    else {}
)

# Mapping for HarmCategory if needed, though usually applied universally
HARM_CATEGORY_MAP = (
    {
        "HARM_CATEGORY_HARASSMENT": HarmCategory.HARM_CATEGORY_HARASSMENT
        if GOOGLE_AI_AVAILABLE
        else "HARM_CATEGORY_HARASSMENT",
        "HARM_CATEGORY_HATE_SPEECH": HarmCategory.HARM_CATEGORY_HATE_SPEECH
        if GOOGLE_AI_AVAILABLE
        else "HARM_CATEGORY_HATE_SPEECH",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT
        if GOOGLE_AI_AVAILABLE
        else "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "HARM_CATEGORY_DANGEROUS_CONTENT": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT
        if GOOGLE_AI_AVAILABLE
        else "HARM_CATEGORY_DANGEROUS_CONTENT",
    }
    if HarmCategory
    else {}
)


from subsystems.KOIOS.core.logging import KoiosLogger

logger = KoiosLogger.get_logger("CORUJA.GeminiInterface")


# Ensure only one class definition exists
class GeminiModelInterface(ModelInterface):  # Use correct base class
    """Provides interaction with Google Gemini models via the google-generativeai library."""

    DEFAULT_MODEL_NAME = "gemini-1.5-flash"  # A sensible default

    # Map generic param names to Gemini GenerationConfig field names
    GENERATION_PARAM_MAP = {
        "temperature": "temperature",
        "max_output_tokens": "max_output_tokens",
        "top_p": "top_p",
        "top_k": "top_k",
        "stop_sequences": "stop_sequences",  # Expects List[str]
        # Add other mappings as needed
    }

    # Map generic safety param names to structure expected by SafetySetting
    SAFETY_PARAM_MAP = {
        # Example: params might contain {"safety_threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        # Or detailed: {"safety_settings": {"HARM_CATEGORY_HARASSMENT": "BLOCK_LOW_AND_ABOVE", ...}}
        "safety_threshold": "threshold",  # Applies threshold to all categories if set
        "safety_settings": "detailed_settings",  # Allows per-category settings
    }

    # Ensure SafetySetting, HarmCategory, HarmBlockThreshold exist before using them
    DEFAULT_SAFETY_SETTINGS = (
        [
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
        ]
        if SafetySetting and HarmCategory and HarmBlockThreshold
        else []
    )

    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        """Initializes the Gemini Model Interface.

        Args:
            model_name: The specific Gemini model to use (e.g., 'gemini-1.5-pro').
                        Defaults to DEFAULT_MODEL_NAME.
            api_key: The Google AI API key. If None, attempts to read from the
                     GOOGLE_API_KEY environment variable.

        Raises:
            AIConfigurationError: If the google-generativeai library is not installed,
                                  if the API key is not provided and cannot be found
                                  in the environment, or if configuration fails.
        """
        if not GOOGLE_AI_AVAILABLE:
            msg = "google-generativeai library not found. Please install it (`pip install google-generativeai`)."
            logger.error(msg)
            raise AIConfigurationError(msg)

        # Now we know GOOGLE_AI_AVAILABLE is True, so genai and google_exceptions are not None
        assert genai is not None
        assert google_exceptions is not None

        # Use KoiosLogger instead of standard logging
        self.logger = logger  # Use the module-level KoiosLogger

        resolved_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not resolved_key:
            error_msg = (
                "Google API key not provided and not found in GOOGLE_API_KEY environment variable."
            )
            self.logger.critical(error_msg)
            raise AIConfigurationError(error_msg)

        try:
            genai.configure(api_key=resolved_key)
            self.logger.info("Google Generative AI SDK configured.")
        except Exception as e:
            error_msg = f"Failed to configure Google Generative AI SDK: {e}"
            self.logger.critical(error_msg, exc_info=True)
            raise AIConfigurationError(error_msg) from e

        self.model_name = model_name or self.DEFAULT_MODEL_NAME

        try:
            # Initialize the model to potentially catch configuration errors early
            self.model = genai.GenerativeModel(self.model_name)
            self.logger.info(f"Initialized Gemini model: {self.model_name}")
        except Exception as e:
            error_msg = f"Failed to initialize Gemini model '{self.model_name}': {e}"
            self.logger.critical(error_msg, exc_info=True)
            # This could be due to invalid model name, permissions, etc.
            raise AIConfigurationError(error_msg) from e

    def _parse_generation_config(self, params: Dict[str, Any]) -> GenerationConfig:
        """Parses generic parameters into a Gemini GenerationConfig object."""
        gen_config_dict = {}
        for generic_name, gemini_name in self.GENERATION_PARAM_MAP.items():
            if generic_name in params:
                gen_config_dict[gemini_name] = params[generic_name]

        # Handle potential type issues (e.g., ensuring stop_sequences is a list)
        if "stop_sequences" in gen_config_dict and not isinstance(
            gen_config_dict["stop_sequences"], list
        ):
            self.logger.warning(
                f"'stop_sequences' parameter should be a list, "
                f"received {type(gen_config_dict['stop_sequences'])}. "
                f"Attempting to use as single item list."
            )
            if isinstance(gen_config_dict["stop_sequences"], str):
                gen_config_dict["stop_sequences"] = [gen_config_dict["stop_sequences"]]
            else:
                del gen_config_dict["stop_sequences"]  # Or raise error?
                self.logger.error(
                    "Could not interpret non-list 'stop_sequences', ignoring parameter."
                )

        try:
            # Ensure GenerationConfig exists before calling it
            if GenerationConfig:
                return GenerationConfig(**gen_config_dict)
            else:
                # Should not happen if GOOGLE_AI_AVAILABLE check passed, but safety check
                raise AIConfigurationError("GenerationConfig class is not available.")
        except Exception as e:
            self.logger.error(
                f"Failed to create GenerationConfig from params: {gen_config_dict}. Error: {e}",
                exc_info=True,
            )
            # Fallback to default or raise? Raising might be better.
            raise AIConfigurationError(f"Invalid generation parameters: {e}") from e

    def _parse_safety_settings(self, params: Dict[str, Any]) -> List[SafetySetting]:
        """Parses generic safety parameters into a list of Gemini SafetySetting objects."""
        # Ensure SafetySetting exists before proceeding
        if not SafetySetting:
            raise AIConfigurationError("SafetySetting class is not available.")

        # Priority: Detailed settings > Global threshold > Defaults
        if self.SAFETY_PARAM_MAP["safety_settings"] in params:
            detailed_settings = params[self.SAFETY_PARAM_MAP["safety_settings"]]
            if isinstance(detailed_settings, dict):
                settings = []
                for cat_str, threshold_str in detailed_settings.items():
                    category = HARM_CATEGORY_MAP.get(cat_str.upper())
                    threshold = SAFETY_THRESHOLD_MAP.get(threshold_str.upper())
                    if category and threshold:
                        # Use the potentially mocked or real SafetySetting class
                        settings.append(SafetySetting(category=category, threshold=threshold))
                    else:
                        self.logger.warning(
                            f"Invalid safety category '{cat_str}' or threshold "
                            f"'{threshold_str}' in detailed settings. Ignoring."
                        )
                if settings:
                    self.logger.debug(f"Using detailed safety settings: {settings}")
                    return settings
            else:
                self.logger.warning(
                    "'safety_settings' parameter provided but is not a dictionary. Ignoring."
                )

        if self.SAFETY_PARAM_MAP["safety_threshold"] in params:
            threshold_str = params[self.SAFETY_PARAM_MAP["safety_threshold"]]
            threshold = SAFETY_THRESHOLD_MAP.get(str(threshold_str).upper())
            if threshold:
                self.logger.debug(f"Using global safety threshold: {threshold_str}")
                # Apply to all known categories
                # Ensure HARM_CATEGORY_MAP and SafetySetting are available
                if HARM_CATEGORY_MAP and SafetySetting:
                    return [
                        SafetySetting(category=cat, threshold=threshold)
                        for cat in HARM_CATEGORY_MAP.values()
                    ]
                else:
                    raise AIConfigurationError(
                        "HarmCategory or SafetySetting not available for global threshold."
                    )
            else:
                self.logger.warning(
                    f"Invalid global 'safety_threshold' value: '{threshold_str}'. Using defaults."
                )

        self.logger.debug("Using default safety settings.")
        return self.DEFAULT_SAFETY_SETTINGS

    async def execute_prompt(
        self, prompt: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        """Executes the prompt against the configured Gemini model."""
        if not GOOGLE_AI_AVAILABLE:
            # Should have been caught in __init__, but double check
            raise AIConfigurationError("google-generativeai library is not available.")
        assert genai is not None
        assert google_exceptions is not None

        self.logger.info(f"Executing prompt with Gemini model: {self.model_name}")
        self.logger.debug(f"Received params: {params}")
        context = context or {}
        if context:
            self.logger.debug(f"Received context: {context}")

        # 1. Prepare GenerationConfig and SafetySettings
        try:
            generation_config = self._parse_generation_config(params)
            safety_settings = self._parse_safety_settings(params)
        except AIConfigurationError as e:
            # Error parsing params, return error response
            return ModelResponse(
                text="",
                error=str(e),
                model_name=self.model_name,
                finish_reason="ERROR",
            )

        # 2. Execute API Call (async)
        raw_response = None
        try:
            self.logger.debug(f"Calling generate_content_async for model '{self.model_name}'")
            # Ensure self.model exists
            if not hasattr(self, "model") or self.model is None:
                raise AIConfigurationError("Gemini model is not initialized.")

            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings,
            )
            raw_response = response  # Store for potential inclusion in ModelResponse
            self.logger.debug("Received response from generate_content_async")

            # 3. Parse Response
            text_output = ""
            finish_reason = None
            token_count = None
            safety_ratings = None  # Initialize safety_ratings

            # Extract safety ratings (might be None if not blocked)
            prompt_feedback = (
                response.prompt_feedback if hasattr(response, "prompt_feedback") else None
            )
            if prompt_feedback and prompt_feedback.safety_ratings:
                safety_ratings = prompt_feedback.safety_ratings

            # Determine finish reason and text output
            candidate = response.candidates[0] if response.candidates else None
            if candidate:
                finish_reason = (
                    candidate.finish_reason.name if candidate.finish_reason else "unknown"
                )
                if candidate.safety_ratings:
                    safety_ratings = (
                        candidate.safety_ratings
                    )  # Candidate ratings override prompt feedback

                if finish_reason == "SAFETY":
                    self.logger.warning(
                        f"Gemini response blocked due to safety. "
                        f"Reason: {finish_reason}, Ratings: {safety_ratings}"
                    )
                    raise ModelSafetyError(
                        f"Response blocked by Gemini safety filters. Ratings: {safety_ratings}"
                    )
                elif candidate.content and candidate.content.parts:
                    text_output = "".join(
                        part.text for part in candidate.content.parts if hasattr(part, "text")
                    )
                else:
                    self.logger.warning(
                        "Gemini response candidate had no processable content parts."
                    )
                    text_output = ""  # Ensure empty if no parts

            elif prompt_feedback and prompt_feedback.block_reason:
                # Prompt itself was blocked
                finish_reason = "SAFETY"  # Treat prompt block as safety finish reason
                self.logger.warning(
                    f"Gemini prompt blocked due to safety. "
                    f"Reason: {prompt_feedback.block_reason}, "
                    f"Ratings: {safety_ratings}"
                )
                raise ModelSafetyError(
                    f"Prompt blocked by Gemini safety filters. Reason: "
                    f"{prompt_feedback.block_reason}"
                )
            else:
                # No valid candidate or prompt feedback block - potentially an issue or unexpected structure
                self.logger.warning(
                    "Gemini response structure unexpected or no candidates/feedback block. Finish reason might be unknown."
                )
                # Try to get finish reason from response directly if available (might be older API structure)
                if hasattr(response, "finish_reason") and response.finish_reason:
                    finish_reason = response.finish_reason.name
                else:
                    finish_reason = finish_reason or "unknown"  # Use 'unknown' if still None
                text_output = ""

            # Token usage extraction (Placeholder - requires inspecting actual response object)
            # try:
            #     if hasattr(response, 'usage_metadata'):
            #         token_count = TokenUsage(
            #             prompt_tokens=response.usage_metadata.prompt_token_count,
            #             completion_tokens=response.usage_metadata.candidates_token_count,
            #             total_tokens=response.usage_metadata.total_token_count
            #         )
            # except Exception as token_err:
            #     self.logger.warning(f"Could not parse token usage: {token_err}")
            #     token_count = None

            self.logger.info(f"Successfully executed prompt. Finish reason: {finish_reason}")
            return ModelResponse(
                text=text_output,
                finish_reason=finish_reason,
                token_usage=token_count,  # Assign parsed token_count here
                safety_ratings=safety_ratings,
                model_name=self.model_name,
                raw_response=raw_response,  # Optional: include for debugging
                error=None,
            )

        # 4. Handle Specific Google API Exceptions
        except google_exceptions.PermissionDenied as e:
            self.logger.error(f"Gemini API permission error: {e}", exc_info=True)
            raise AIConfigurationError(f"Permission denied for Gemini API: {e}") from e
        except google_exceptions.ResourceExhausted as e:
            self.logger.error(f"Gemini API resource exhausted (rate limit?): {e}", exc_info=True)
            raise ModelRateLimitError(f"Gemini API rate limit likely exceeded: {e}") from e
        except google_exceptions.InvalidArgument as e:
            self.logger.error(f"Gemini API invalid argument error: {e}", exc_info=True)
            raise ModelApiException(f"Invalid argument for Gemini API: {e}") from e
        except google_exceptions.DeadlineExceeded as e:
            self.logger.error(f"Gemini API deadline exceeded (timeout): {e}", exc_info=True)
            raise ModelTimeoutError(f"Gemini API call timed out: {e}") from e
        except google_exceptions.GoogleAPIError as e:
            self.logger.error(f"Gemini API error: {e}", exc_info=True)
            raise ModelApiException(f"Gemini API error: {e}") from e
        # Handle our specific safety error raised during parsing
        except ModelSafetyError as e:
            return ModelResponse(
                text="",
                error=str(e),
                finish_reason="SAFETY",
                safety_ratings=e.args[0]
                if e.args and isinstance(e.args[0], list)
                else None,  # Pass ratings if available
                model_name=self.model_name,
                raw_response=raw_response,
                token_usage=None,
            )
        # Handle configuration errors during execution
        except AIConfigurationError as e:
            self.logger.error(f"Configuration error during execution: {e}", exc_info=True)
            raise  # Re-raise configuration errors
        # Handle other unexpected errors
        except Exception as e:
            self.logger.exception(f"Unexpected error during Gemini API call or processing: {e}")
            raise CorujaException(f"Unexpected error in Gemini interface: {e}") from e

    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generates a response from the Gemini model (implements ModelInterface).

        This method primarily wraps the execute_prompt method for compatibility,
        extracting just the text response.

        Args:
            prompt: The input prompt string.
            **kwargs: Parameters for generation (temperature, safety_settings, etc.)
                     which will be parsed by helper methods.

        Returns:
            The generated text content as a string.

        Raises:
            AICommunicationError: If there was an issue communicating with the API.
            AIResponseError: If the response indicates an error (e.g., safety block).
            AIConfigurationError: If there is a configuration problem.
            AIError: For other model-related errors.
        """
        try:
            model_response = await self.execute_prompt(prompt, params=kwargs)

            if model_response.error:
                self.logger.error(f"Error received from execute_prompt: {model_response.error}")
                # Map specific errors if possible, otherwise raise generic AIResponseError
                if model_response.finish_reason == "SAFETY":
                    raise AIResponseError(f"Response blocked due to safety: {model_response.error}")
                else:
                    raise AIResponseError(f"Model execution failed: {model_response.error}")

            return model_response.text

        # Catch specific exceptions raised by execute_prompt and map them
        except ModelConfigurationError as e:
            raise AIConfigurationError(str(e)) from e
        except ModelRateLimitError as e:
            raise AIResponseError(f"Rate limit exceeded: {e}") from e  # Map to AIResponseError
        except ModelSafetyError as e:
            raise AIResponseError(f"Safety error: {e}") from e  # Map to AIResponseError
        except ModelTimeoutError as e:
            raise AICommunicationError(f"Timeout error: {e}") from e
        except ModelApiException as e:
            raise AICommunicationError(f"API communication error: {e}") from e
        except CorujaException as e:
            raise AIError(f"CORUJA system error: {e}") from e
        except Exception as e:
            self.logger.exception("Unexpected error in generate_response wrapper")
            raise AIError(f"Unexpected error: {e}") from e

    def count_tokens(self, text: str) -> int:
        """Counts the number of tokens in the given text using the Gemini model.

        Args:
            text: The text to count tokens for.

        Returns:
            The total number of tokens.

        Raises:
            AIConfigurationError: If the library is not available or model not initialized.
            AICommunicationError: If there is an API communication error.
        """
        if not GOOGLE_AI_AVAILABLE:
            raise AIConfigurationError("google-generativeai library is not available.")
        assert genai is not None
        assert google_exceptions is not None
        if not hasattr(self, "model") or self.model is None:
            raise AIConfigurationError("Gemini model is not initialized.")

        try:
            self.logger.debug(f"Calling count_tokens for model '{self.model_name}'")
            response = self.model.count_tokens(text)
            token_count = response.total_tokens
            self.logger.info(f"Successfully counted tokens: {token_count}")
            return token_count
        except google_exceptions.GoogleAPIError as e:
            self.logger.error(f"Gemini API error during token count: {e}", exc_info=True)
            raise AICommunicationError(f"API communication failed during token count: {e}") from e
        except Exception as e:
            self.logger.exception(f"Unexpected error during token count: {e}")
            raise AICommunicationError(f"Unexpected error during token count: {e}") from e

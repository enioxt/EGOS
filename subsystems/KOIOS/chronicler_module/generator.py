# koios/chronicler_module/generator.py

"""Handles AI interaction via CORUJA/OpenRouter to generate documentation content."""

import os
import yaml # Required for reading config
from openai import OpenAI
from pathlib import Path
import logging

# --- Logger Setup ---
logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent / "chronicler_config.yaml"

# --- Load Configuration ---
def load_config():
    """Loads configuration from chronicler_config.yaml, providing defaults."""
    default_config = {
        'exclude': ['.git', '__pycache__', 'node_modules', 'venv', '*.log'], # Used by analyzer
        'model': 'mistralai/mistral-7b-instruct', # Default free model
        'max_tokens': 150,
        'temperature': 0.5,
    }
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    # Deep merge might be better later, simple update for now
                    default_config.update(user_config)
                    logger.info(f"[INFO] Loaded configuration from {CONFIG_PATH}")
        except Exception as e:
            logger.warning(f"[WARNING] Failed to load or parse {CONFIG_PATH}: {e}. Using defaults.")
    else:
        logger.info(f"[INFO] Configuration file not found at {CONFIG_PATH}. Using defaults.")
    return default_config

config = load_config()

# --- OpenRouter Client Setup ---
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"

# List of known free models (update as needed based on OpenRouter)
KNOWN_FREE_MODELS = [
    "mistralai/mistral-7b-instruct",
    "nousresearch/nous-hermes-llama2-13b",
    "google/gemma-7b-it",
    "huggingfaceh4/zephyr-7b-beta",
    # Add more recognized free models here
]

client = None
if API_KEY:
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
else:
    # Clear instructions if API key is missing
    logger.error("\n" + "*" * 60)
    logger.error("[ERROR] OPENROUTER_API_KEY environment variable not set!")
    logger.error("Chronicler needs this key to generate AI summaries.")
    logger.error("\nHow to set the environment variable in Windows:")
    logger.error("1. Search for 'Environment Variables' in the Start Menu.")
    logger.error("2. Click on 'Edit the system environment variables'.")
    logger.error("3. In the 'System Properties' window, click 'Environment Variables...'.")
    logger.error("4. Under 'User variables', click 'New...'.")
    logger.error("   - Variable name: OPENROUTER_API_KEY")
    logger.error("   - Variable value: YOUR_OPENROUTER_API_KEY_HERE")
    logger.error("5. Click OK on all windows.")
    logger.error("6. IMPORTANT: Restart VS Code or your terminal for the change to take effect.")
    logger.error("" * 60 + "\n")

def list_known_free_models():
    """Returns the list of known free models."""
    # In future, this could potentially fetch from OpenRouter API if available
    return KNOWN_FREE_MODELS

def build_prompt(analysis_data: dict) -> str:
    """Constructs a detailed prompt for the AI model."""
    project_name = analysis_data.get('project_name', 'Unknown Project')
    languages = analysis_data.get('detected_languages', [])
    key_items = analysis_data.get('key_items', [])
    readme_content = ""
    for k, v in analysis_data.get('files_for_summary', {}).items():
        if 'readme.md' in k.lower():
            readme_content = v
            break

    prompt_lines = [
        f"As an AI documentation assistant (EGOS Chronicler), generate a concise, high-level technical summary for the software project named '{project_name}'.",
        "Analyze the following data extracted from the codebase:",
        f"- Primary Languages/Technologies Detected: {', '.join(languages) if languages else 'N/A'}",
        f"- Key Files/Directories Identified: {', '.join(key_items) if key_items else 'N/A'}"
    ]

    if readme_content:
        readme_snippet = readme_content[:1000] # Limit snippet length
        prompt_lines.append(f"\n- Relevant README.md Content Snippet:\n---\n{readme_snippet}\n---")

    prompt_lines.extend([
        "\nBased *only* on the information provided, describe:",
        "1. The likely **purpose** or **main goal** of this project.",
        "2. Its **key characteristics** or **distinguishing features**.",
        "\nFormat the summary as a short paragraph (2-4 sentences) suitable for a technical audience.",
        "Focus on clarity and accuracy based on the input."
    ])

    return "\n".join(prompt_lines)

def select_model() -> str:
    """Selects the model based on config, falling back to a known free default."""
    configured_model = config.get('model', KNOWN_FREE_MODELS[0])
    free_models = list_known_free_models()

    if configured_model in free_models:
        logger.info(f"[INFO] Using configured model: {configured_model}")
        return configured_model
    else:
        # If the configured model isn't in our known free list, use the default free one
        default_free = KNOWN_FREE_MODELS[0]
        logger.warning(f"[WARNING] Model '{configured_model}' from config is not in the known free list {free_models}. ")
        logger.info(f"[INFO] Falling back to default free model: {default_free}")
        return default_free

def generate_project_summary(analysis_data: dict) -> str:
    """Generates a project summary using OpenRouter API based on analysis data."""
    logger.debug(">>> Entering Generator: generate_project_summary") # Debug

    config = load_config()
    if not config:
        return "[ERROR] Failed to load configuration."

    # --- API Key Handling --- 
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        logger.error('\n--- OpenRouter API Key Not Found ---')
        logger.error('Please enter your OpenRouter API key to generate the summary.')
        logger.error('You can obtain a key from https://openrouter.ai')
        logger.error('Alternatively, set the OPENROUTER_API_KEY environment variable.')
        try:
            api_key = input('Enter API Key: ').strip()
            if not api_key:
                 logger.error('No API key entered. Cannot generate summary.')
                 return "[ERROR] API Key not provided by user."
        except EOFError: # Handle cases where input is not possible (e.g., non-interactive script run)
             logger.error('\nInput stream closed. Cannot prompt for API key.')
             return "[ERROR] Cannot prompt for API Key in non-interactive mode."
        logger.info('--- API Key Received ---') # Confirmation

    # --- Client Initialization --- 
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
    except Exception as e:
        logger.error(f"Error during client initialization: {e}")
        return f"[ERROR] Failed to initialize OpenRouter client: {e}"

    prompt = build_prompt(analysis_data)
    model_to_use = select_model()
    max_tokens = config.get('max_tokens', 150)
    temperature = config.get('temperature', 0.5)

    # logger.debug(f"\nDEBUG: Sending Prompt to {model_to_use}:\n{prompt}\n") # Uncomment for debugging

    try:
        logger.info(f"Attempting API call to OpenRouter using model: {model_to_use}...")
        response = client.chat.completions.create(
            model=model_to_use,
            messages=[
                {"role": "system", "content": "You are an expert technical writer summarizing software projects based on file analysis."}, # System prompt
                {"role": "user", "content": prompt} # User prompt with data
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        summary = response.choices[0].message.content.strip()
        logger.info("API call successful.")
        logger.debug(">>> Exiting Generator: generate_project_summary (AI Generated)")
        return summary

    except Exception as e:
        error_message = f"[ERROR] During OpenRouter API call to model '{model_to_use}': {e}"
        logger.error(error_message)
        logger.debug(">>> Exiting Generator: generate_project_summary (Error)")
        # Provide more context in the returned error message
        return f"{error_message}\nCheck your API key, network connection, and OpenRouter model status."

# TODO: Add functions for other document types (e.g., detailed module analysis) in later phases.

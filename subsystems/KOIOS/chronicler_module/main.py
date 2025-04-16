# koios/chronicler_module/main.py

"""Main entry point for the Chronicler Module (MVP - CLI)."""

import argparse
import os
import sys
import logging
from pathlib import Path

# Adjust sys.path to allow importing sibling modules if run directly
def add_project_root_to_path():
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent.parent # Assumes structure EGOS/subsystems/KOIOS
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str) # Insert at the beginning

add_project_root_to_path()

# --- Logger Setup --- 
# Moved logger setup into a function to access args
def setup_logging(log_level=logging.INFO, output_dir=None):
    """Configures the logging system."""
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    root_logger = logging.getLogger() # Get the root logger
    root_logger.setLevel(log_level) # Set the minimum level for the root logger

    # Clear existing handlers to avoid duplicates if run multiple times
    # Be cautious if other parts of a larger application configure logging
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console Handler (always add)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    # Set console level explicitly, might be different from file level if needed
    # For now, let it inherit from root_logger level
    # console_handler.setLevel(logging.INFO) 
    root_logger.addHandler(console_handler)

    # File Handler (only if output_dir is valid)
    log_file_path = None
    if output_dir:
        try:
            log_dir = Path(output_dir).resolve()
            log_dir.mkdir(parents=True, exist_ok=True) # Ensure directory exists
            log_file_path = log_dir / "chronicler.log"
            
            file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8') # 'w' to overwrite log each run
            file_handler.setFormatter(log_formatter)
            # file_handler.setLevel(logging.DEBUG) # Optionally set different level for file
            root_logger.addHandler(file_handler)
            print(f"[INFO] Logging detailed output to: {log_file_path}") # Use print here as logging might not be fully set up
        except Exception as e:
            print(f"[ERROR] Failed to configure file logging to {output_dir}: {e}. Logging to console only.") # Use print
            log_file_path = None # Ensure it's None if setup failed
    else:
        print("[INFO] No output directory specified, logging to console only.") # Use print

    # Get the logger for this specific module after setup
    logger = logging.getLogger(__name__)
    if log_file_path:
        logger.info(f"Logging initialized. Log file: {log_file_path}")
    else:
        logger.info("Logging initialized (console only).")
    return logger # Return the specific logger for main.py

# --- Argument Parsing ---
def parse_arguments():
    parser = argparse.ArgumentParser(description="EGOS Chronicler: Analyze a project directory and generate an AI summary.")
    parser.add_argument("directory", help="Path to the project directory to analyze.")
    parser.add_argument("-o", "--output", help="Optional directory to save the HTML report. If not provided, prints to console (if possible) or saves in current directory.")
    # parser.add_argument("--model", help="Specify the OpenRouter model to use (overrides config).") # Add later if needed
    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()
    logger = setup_logging(logging.INFO, args.output) # Pass output dir here

    target_directory = Path(args.directory)
    output_destination = args.output

    if not target_directory.is_dir():
        logger.error(f"Error: Provided path '{args.directory}' is not a valid directory.")
        sys.exit(1)

    logger.info(f"--- Starting Chronicler Analysis for: {target_directory.resolve()} ---")

    # --- Analysis Phase ---
    logger.info("--- Phase 1: Analyzing Directory Structure & Content ---")
    try:
        from KOIOS.chronicler_module import analyzer, generator, renderer
    except ImportError as e:
        logger.error(f"ERROR: Could not import Chronicler modules ({e}). Ensure EGOS project structure is correct and accessible.")
        sys.exit(1)

    analysis_results = analyzer.analyze_directory(str(target_directory))
    if not analysis_results:
        logger.error("Error: Analysis phase failed. Exiting.")
        sys.exit(1)
    logger.info(f"Analysis complete. Found {analysis_results.get('total_files_scanned', 0)} files.")
    if analysis_results.get('errors'):
        logger.warning("Analysis encountered errors:")
        for error in analysis_results['errors']:
            logger.warning(f"- {error}")

    # Add project name to results if not already present
    if 'project_name' not in analysis_results:
        analysis_results['project_name'] = target_directory.name

    # --- Generation Phase ---
    logger.info("--- Phase 2: Generating AI Summary --- ")
    ai_summary = generator.generate_project_summary(analysis_results)
    # logger.debug(f"Generated Summary:\n{ai_summary}") # Debug print summary

    # --- Rendering Phase ---
    logger.info("--- Phase 3: Rendering Output --- ")
    output_location = output_destination if output_destination else str(Path.cwd()) # Default to current dir if -o not specified
    html_output_path = renderer.render_to_html(analysis_results, ai_summary, output_dir=output_location)

    if html_output_path:
        logger.info(f"\n--- Chronicler Finished --- ")
        logger.info(f"Successfully generated summary report at: {html_output_path}")
    else:
        logger.error("\n--- Chronicler Finished with Errors --- ")
        logger.error("Failed to generate the final HTML report.")
        # Consider printing basic analysis results to console as fallback?
        # logger.info("\nAnalysis Data:")
        # import json
        # logger.info(json.dumps(analysis_results, indent=2))
        # logger.info("\nGenerator Output:")
        # logger.info(ai_summary)

if __name__ == "__main__":
    main()

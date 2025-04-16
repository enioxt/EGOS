# koios/chronicler_module/analyzer.py

"""Core analysis functions for the Chronicler Module.

Handles directory scanning, file filtering, and basic code property detection.
"""

import os
import fnmatch
from pathlib import Path
import yaml
import logging

# --- Logger Setup ---
# Get logger for this module. It will inherit the config from main.py if run via main.
# If run standalone, it might need its own basicConfig.
logger = logging.getLogger(__name__)

# Basic list of common directories/files to ignore by default
# TODO: Make this configurable
DEFAULT_EXCLUSIONS = [
    '.git',
    '.vscode',
    '.idea',
    'node_modules',
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '*.log',
    '*.tmp',
    '*.swp',
    'dist',
    'build',
    'target',
    '*.egg-info',
    'venv',
    '.env'
]

# --- Configuration Loading ---
CONFIG_PATH = Path(__file__).parent / "chronicler_config.yaml"

def load_config():
    """Loads configuration from chronicler_config.yaml, providing defaults."""
    default_config = {
        'exclude': DEFAULT_EXCLUSIONS,
    }
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    logger.debug(f"Loaded user config: {user_config}")
                    default_config.update(user_config)
                else:
                    logger.debug(f"Config file {CONFIG_PATH} is empty or invalid YAML.")
        except Exception as e:
            # Use logger.warning for config loading issues
            logger.warning(f"Failed to load or parse {CONFIG_PATH}: {e}. Using defaults.")
    else:
        logger.info(f"Config file {CONFIG_PATH} not found. Using default exclusions.")
    return default_config

# TODO: Implement more robust language detection
LANGUAGE_EXTENSIONS = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.java': 'Java',
    '.cs': 'C#',
    '.go': 'Go',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.rs': 'Rust',
    '.md': 'Markdown',
    '.html': 'HTML',
    '.css': 'CSS',
    '.json': 'JSON',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.xml': 'XML',
    'Dockerfile': 'Docker'
    # Add more as needed
}

def load_gitignore(project_root: Path) -> list[str]:
    """Loads patterns from .gitignore file if it exists."""
    gitignore_path = project_root / '.gitignore'
    patterns = []
    if gitignore_path.is_file():
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
            logger.debug(f"Loaded {len(patterns)} patterns from {gitignore_path}")
        except Exception as e:
            # Use logger.warning
            logger.warning(f"Could not read .gitignore file at {gitignore_path}: {e}")
    else:
        logger.debug(f".gitignore file not found at {gitignore_path}")
    return patterns

def is_excluded(path: Path, name: str, relative_path_str: str | None, project_root: Path, gitignore_patterns: list[str], default_exclusions: list[str], config_exclusions: list[str]) -> bool:
    """Checks if a path should be excluded based on default, gitignore, and config patterns."""

    # Use relative path for matching if available, otherwise fall back
    match_path_str = relative_path_str if relative_path_str is not None else name

    # Check default exclusions
    for pattern in default_exclusions:
        try:
            if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(match_path_str, pattern):
                logger.debug(f"Excluding '{match_path_str}' (name: {name}) due to default pattern '{pattern}'")
                return True
        except Exception as e:
            # Keep this specific warning print for fnmatch errors
            print(f"[WARNING] Analyzer: Error during default exclusion matching: path='{match_path_str}', name='{name}', pattern='{pattern}'. Error: {e}")
            continue

    # Check gitignore patterns
    for pattern in gitignore_patterns:
        try:
            # Handle directory patterns (ending with /)
            if pattern.endswith('/'):
                pattern_no_slash = pattern.rstrip('/')
                should_exclude_dir = False
                try:
                    if path.is_dir() and (fnmatch.fnmatch(name, pattern_no_slash) or (relative_path_str and fnmatch.fnmatch(relative_path_str, pattern_no_slash))):
                        should_exclude_dir = True
                except Exception as inner_e:
                     # Keep this specific warning print for fnmatch errors
                    print(f"[WARNING] Analyzer: Error matching directory pattern: relative_path='{relative_path_str}', name='{name}', pattern='{pattern}'. Error: {inner_e}")
                
                if should_exclude_dir:
                    logger.debug(f"Excluding directory '{relative_path_str}' due to gitignore pattern '{pattern}'")
                    return True
                
                # Match if any PARENT directory matches (only if relative path exists)
                if relative_path_str:
                    current_parent_rel_path_str = ""
                    parts = relative_path_str.split('/')
                    for part in parts[:-1]: # Iterate through parent parts
                        current_parent_rel_path_str += part + "/"
                        try:
                             if fnmatch.fnmatch(current_parent_rel_path_str.rstrip('/'), pattern_no_slash):
                                 logger.debug(f"Excluding '{relative_path_str}' due to parent '{current_parent_rel_path_str}' matching gitignore pattern '{pattern}'")
                                 return True
                        except Exception as parent_e:
                             # Keep this specific warning print for fnmatch errors
                            print(f"[WARNING] Analyzer: Error matching parent directory pattern: parent_path='{current_parent_rel_path_str.rstrip('/')}', pattern='{pattern_no_slash}'. Error: {parent_e}")
            
            # Handle file/general patterns
            else:
                match_name = False
                try:
                    match_name = fnmatch.fnmatch(name, pattern)
                except Exception as name_e:
                     # Keep this specific warning print for fnmatch errors
                    print(f"[WARNING] Analyzer: Error matching name pattern: name='{name}', pattern='{pattern}'. Error: {name_e}")
                
                match_relative = False
                if relative_path_str:
                    try:
                        match_relative = fnmatch.fnmatch(relative_path_str, pattern)
                    except Exception as rel_e:
                         # Keep this specific warning print for fnmatch errors
                        print(f"[WARNING] Analyzer: Error matching relative path pattern: relative_path='{relative_path_str}', pattern='{pattern}'. Error: {rel_e}")
                
                if match_name or match_relative:
                    logger.debug(f"Excluding '{match_path_str}' (name: {name}) due to gitignore pattern '{pattern}'")
                    return True

        except Exception as e:
            # Keep this specific warning print for fnmatch errors
            print(f"[WARNING] Analyzer: Error processing gitignore pattern: pattern='{pattern}'. Error: {e}")
            continue

    # Check config exclusions
    for pattern in config_exclusions:
        try:
            if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(match_path_str, pattern):
                logger.debug(f"Excluding '{match_path_str}' (name: {name}) due to config pattern '{pattern}'")
                return True
        except Exception as e:
             # Keep this specific warning print for fnmatch errors
            print(f"[WARNING] Analyzer: Error during config exclusion matching: path='{match_path_str}', name='{name}', pattern='{pattern}'. Error: {e}")
            continue

    return False

def analyze_directory(directory_path: str) -> dict:
    """Analyzes the specified directory for the MVP scope."""
    root_path = Path(directory_path).resolve()
    if not root_path.is_dir():
        # Use logger.error
        logger.error(f"Path is not a valid directory: {directory_path}")
        return {
            'project_name': Path(directory_path).name,
            'errors': [f"Path is not a valid directory: {directory_path}"],
            'detected_languages': {},
            'key_items': [],
            'total_files_scanned': 0,
            'files_for_summary': {}
        }

    project_name = root_path.name
    # Use logger.info
    logger.info(f"Starting analysis of: {root_path}")

    # --- Load configurations once --- 
    config = load_config()
    config_exclude_patterns = config.get('exclude', []) 
    gitignore_patterns = load_gitignore(root_path)
    # Use logger.info for loading counts
    logger.info(f"Loaded {len(config_exclude_patterns)} config exclude patterns.")
    logger.info(f"Loaded {len(gitignore_patterns)} gitignore patterns.")

    # --- Initialize results --- 
    analysis_results = {
        'project_name': project_name,
        'detected_languages': {},
        'key_items': [],
        'total_files_scanned': 0,
        'total_dirs_scanned': 0,
        'files_for_summary': {},
        'errors': []
    }
    lang_counts = {}
    # Use logger.debug for detailed initialization
    logger.debug(f"Initialized analysis_results for {project_name}")

    # --- Walk through the directory --- 
    for item in root_path.rglob('*'):
        item_name = item.name
        relative_path_str: str | None = None
        try:
            relative_path = item.relative_to(root_path)
            relative_path_str = str(relative_path).replace('\\', '/')
        except ValueError:
            # Use logger.warning
            logger.warning(f"Could not determine relative path for {item}. Skipping.")
            analysis_results['errors'].append(f"Could not determine relative path for {item}. Skipping.")
            continue

        # Check exclusions using the calculated relative path string
        if is_excluded(item, item_name, relative_path_str, root_path, gitignore_patterns, DEFAULT_EXCLUSIONS, config_exclude_patterns):
            logger.debug(f"Skipping excluded item: {relative_path_str or item_name}")
            continue

        # Process the item if not excluded
        if item.is_file():
            analysis_results['total_files_scanned'] += 1
            logger.debug(f"Processing file: {relative_path_str}")

            # --- Key File Identification (Basic) ---
            if item_name.lower() == 'readme.md':
                logger.debug(f"Found key file (README): {relative_path_str}")
                analysis_results['key_items'].append(relative_path_str)
                try:
                    # Limit size read for summary
                    file_content = item.read_text(encoding='utf-8', errors='ignore')[:5000]
                    analysis_results['files_for_summary'][relative_path_str] = file_content
                    logger.debug(f"Read {len(file_content)} bytes from {relative_path_str} for summary.")
                except Exception as e:
                    # Use logger.warning
                     logger.warning(f"Could not read {relative_path_str} for summary: {e}")
                     analysis_results['errors'].append(f"Could not read {relative_path_str}: {e}")
                     analysis_results['files_for_summary'][relative_path_str] = f"Error reading file: {e}"
            
            # --- Language Detection (Basic) ---
            ext = item.suffix.lower()
            lang = LANGUAGE_EXTENSIONS.get(ext)
            if not lang and item_name.lower() == 'dockerfile':
                 lang = LANGUAGE_EXTENSIONS.get('Dockerfile')
            elif not lang and item_name.lower() == 'makefile':
                 lang = 'Makefile'
            
            if lang:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
                logger.debug(f"Detected language '{lang}' for file: {relative_path_str}")

        elif item.is_dir():
            analysis_results['total_dirs_scanned'] += 1
            logger.debug(f"Processing directory: {relative_path_str}")
            # Add key directories (e.g., src, app, docs) - refine this logic
            if relative_path_str and len(relative_path_str.split('/')) == 1 and item_name.lower() in ['src', 'app', 'lib', 'docs', 'core', 'include', 'tests', 'examples']:
                 logger.debug(f"Found key directory: {relative_path_str}/")
                 analysis_results['key_items'].append(relative_path_str + '/')

    analysis_results['detected_languages'] = lang_counts
    # Use logger.info for completion message
    logger.info(f"Analysis complete. Scanned {analysis_results['total_files_scanned']} files and {analysis_results['total_dirs_scanned']} directories.")
    if analysis_results['errors']:
        logger.warning(f"Analysis finished with {len(analysis_results['errors'])} errors/warnings.")
    return analysis_results

# Example Usage (for testing)
if __name__ == '__main__':
    # Configure logging for standalone testing
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logger.info("Running analyzer.py standalone for testing.")
    # test_dir = '.' # Analyze current directory
    test_dir = 'C:\\Eva Guarani EGOS' # Replace with a valid path for testing
    if not Path(test_dir).exists():
        logger.error(f"Test directory '{test_dir}' does not exist. Skipping standalone test.")
    else:
        try:
            results = analyze_directory(test_dir)
            logger.info("Standalone Analysis Results:")
            import json
            # Use logger.info for printing results neatly
            logger.info(json.dumps(results, indent=2))
        except Exception as e:
            logger.critical(f"Error during standalone test: {e}", exc_info=True)

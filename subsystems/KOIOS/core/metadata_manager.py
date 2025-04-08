"""
KOIOS Metadata Manager
=====================

Handles the generation, loading, and saving of metadata for EGOS files,
using sidecar JSON files.

Version: 1.1
Last Updated: 2025-04-07
"""

import datetime
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import logger
# Assuming KoiosLogger is correctly set up in this path
from subsystems.KOIOS.core.logging import KoiosLogger

logger = KoiosLogger.get_logger(__name__)

METADATA_SUFFIX = ".meta.json"  # Define the suffix for sidecar files


class MetadataError(Exception):
    """Custom exception raised for errors during metadata processing.

    Used to signal issues specifically related to metadata handling,
    such as validation errors or unexpected structural problems.
    """

    pass


class MetadataManager:
    """
    Manages metadata for EGOS files using sidecar JSON files.

    Provides functionalities to generate initial metadata based on file path
    and type, save it to a `.meta.json` sidecar file, load metadata from
    existing sidecar files, and perform basic validation.
    """

    # Define a basic expected schema structure (can be expanded/formalized)
    EXPECTED_TOP_LEVEL_KEYS = {
        "schema_version",  # Added
        "file_path_relative",  # Added
        "last_generated_utc",  # Added
        "quantum_identity",
        "quantum_connections",
        "quantum_state",
        "quantum_evolution",
        "quantum_integration",
    }

    def __init__(self, root_dir: str):
        """
        Initialize the metadata manager.

        Args:
            root_dir: The root directory of the EGOS project.
                      Used to determine relative paths and subsystem context.
        """
        self.root_dir = Path(root_dir).resolve()  # Ensure absolute path
        # Define directories to ignore during scans or processing
        self.ignored_dirs = {".git", "__pycache__", "venv", ".metadata", "logs", "backups"}
        self.supported_encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252"]
        logger.info(f"Initialized MetadataManager with root directory: {self.root_dir}")

    def _get_sidecar_path(self, source_file_path: Path) -> Path:
        """Determines the path for the metadata sidecar file.

        Appends `.meta.json` to the original file's name.

        Args:
            source_file_path: The Path object of the original source file.

        Returns:
            The Path object for the corresponding sidecar metadata file.
        """
        # Example: /path/to/file.py -> /path/to/file.py.meta.json
        return source_file_path.with_suffix(source_file_path.suffix + METADATA_SUFFIX)

    def generate_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Generate the initial metadata dictionary for a given file.

        Derives basic information like type, category, subsystem, and purpose
        from the file path. Populates other fields with default or placeholder
        values that are expected to be updated by other EGOS subsystems or processes.

        Args:
            file_path: Path to the source file.

        Returns:
            A dictionary containing the generated metadata.

        Raises:
            FileNotFoundError: If the source file does not exist.
        """
        if not file_path.is_file():
            raise FileNotFoundError(f"Source file not found: {file_path}")

        file_type = file_path.suffix.lower()
        subsystem = self._detect_subsystem(file_path)
        purpose = self._detect_purpose(file_path)
        category = self._detect_category(file_type)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # --- Placeholder Values --- #
        # These are examples; actual values should be determined or updated by relevant subsystems.
        consciousness_level = 0.85  # Placeholder: Potentially from analysis?
        dependencies: List[str] = []  # Placeholder: Updated by NEXUS
        # Placeholder values - these should ideally be updated by other processes
        # (e.g., NEXUS for dependencies, HARMONY for test coverage)
        consciousness_level = 0.85  # Example placeholder
        dependencies: List[str] = []
        related_components: List[str] = []
        api_endpoints: List[str] = []
        mycelial_links: List[str] = []
        status = "active"  # Example placeholder
        ethical_validation = 0.9  # Example placeholder
        security_level = 0.8  # Example placeholder
        test_coverage = 0.0  # Placeholder - updated by tests
        documentation_quality = 0.7  # Placeholder - updated by analysis?
        version = "1.0.0"  # Placeholder - could come from git tags or config
        changelog: List[str] = []  # Placeholder
        backup_required = True  # Example policy
        preservation_priority = 0.5  # Example policy
        encoding = self._detect_encoding(file_path) or "utf-8"  # Default to utf-8
        translation_status = "required"  # Example placeholder
        simulation_capable = False  # Example placeholder
        cross_platform_support = ["windows", "linux"]  # Example

        metadata = {
            "schema_version": "1.1",  # Add schema versioning
            "file_path_relative": self._get_relative_path(file_path),
            "last_generated_utc": timestamp,
            "quantum_identity": {
                "type": file_type,
                "category": category,
                "subsystem": subsystem,
                "purpose": purpose,
                "consciousness_level": consciousness_level,
            },
            "quantum_connections": {
                "dependencies": dependencies,
                "related_components": related_components,
                "api_endpoints": api_endpoints,
                "mycelial_links": mycelial_links,
            },
            "quantum_state": {
                "status": status,
                "ethical_validation": ethical_validation,
                "security_level": security_level,
                "test_coverage": test_coverage,
                "documentation_quality": documentation_quality,
            },
            "quantum_evolution": {
                "version": version,
                "last_updated_source_utc": self._get_last_modified_time(file_path),
                "changelog": changelog,
                "backup_required": backup_required,
                "preservation_priority": preservation_priority,
            },
            "quantum_integration": {
                "windows_compatibility": 1.0,  # Example
                "encoding": encoding,
                "translation_status": translation_status,
                "simulation_capable": simulation_capable,
                "cross_platform_support": cross_platform_support,
            },
        }

        return metadata

    # Renamed and Rewritten Method
    def generate_and_save_metadata(self, source_file_path: Path) -> bool:
        """
        Generates metadata for the source file and saves it to a sidecar JSON file.
        Does NOT modify the original source file.

        Args:
            source_file_path: Path to the source file.

        Returns:
            True if metadata was successfully generated and saved, False otherwise.
        """
        if not isinstance(source_file_path, Path):
            logger.error(f"Invalid path type received: {type(source_file_path)}")
            return False
        if not source_file_path.is_file():
            logger.error(f"Source file does not exist or is not a file: {source_file_path}")
            return False

        sidecar_path = self._get_sidecar_path(source_file_path)

        try:
            # Generate metadata
            metadata_dict = self.generate_metadata(source_file_path)

            # Write metadata to the sidecar file
            with open(sidecar_path, "w", encoding="utf-8") as f:
                json.dump(metadata_dict, f, indent=2)

            logger.info(f"Metadata saved to sidecar file: {sidecar_path.name}")
            return True

        except FileNotFoundError as e:
            logger.error(f"Error generating metadata (source file missing?): {e}")
            return False
        except IOError as e:
            logger.error(f"Error writing metadata sidecar file {sidecar_path}: {e}")
            return False
        except Exception as e:
            # Catch unexpected errors during generation or saving
            logger.error(
                f"Unexpected error processing metadata for {source_file_path}: {e}", exc_info=True
            )
            return False

    # New Method
    def load_metadata(self, source_file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Loads metadata from the sidecar JSON file associated with the source file.

        Args:
            source_file_path: Path to the source file.

        Returns:
            A dictionary containing the metadata, or None if loading fails.
        """
        if not isinstance(source_file_path, Path):
            logger.error(f"Invalid path type received for loading: {type(source_file_path)}")
            return None

        sidecar_path = self._get_sidecar_path(source_file_path)

        if not sidecar_path.is_file():
            # It's not necessarily an error if metadata doesn't exist yet.
            logger.debug(f"Metadata sidecar file not found: {sidecar_path}")
            return None

        try:
            with open(sidecar_path, "r", encoding="utf-8") as f:
                # json.load returns Any, so we need to check the type
                loaded_data = json.load(f)

            # Ensure the loaded data is actually a dictionary
            if not isinstance(loaded_data, dict):
                error_msg = (
                    f"Metadata file {sidecar_path.name} does not contain a valid "
                    f"JSON object (dictionary). Found type: {type(loaded_data)}"
                )
                logger.error(error_msg)
                return None

            # Cast to the expected type for the type checker
            metadata_dict: Dict[str, Any] = loaded_data

            # Basic validation (optional but recommended)
            if not self.EXPECTED_TOP_LEVEL_KEYS.issubset(metadata_dict.keys()):
                missing_keys = self.EXPECTED_TOP_LEVEL_KEYS - metadata_dict.keys()
                warn_msg = (
                    f"Metadata file {sidecar_path.name} has unexpected structure. "
                    f"Missing keys: {missing_keys}"
                )
                logger.warning(warn_msg)
                # Decide whether to return None or the potentially invalid data
                # return None # Returning the data despite missing keys for now

            return metadata_dict

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from metadata file {sidecar_path.name}: {e}")
            return None
        except IOError as e:
            logger.error(f"Error reading metadata sidecar file {sidecar_path.name}: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error loading metadata from {sidecar_path.name}: {e}", exc_info=True
            )
            return None

    def _get_relative_path(self, file_path: Path) -> str:
        """
        Get the path relative to the root directory, using forward slashes.
        Ensures consistency regardless of OS.

        Args:
            file_path: Path to the file (absolute).

        Returns:
            Relative path as string with forward slashes, or the original string if error.
        """
        try:
            # Ensure file_path is absolute before making relative
            abs_file_path = file_path.resolve()
            relative_p = abs_file_path.relative_to(self.root_dir)
            # Convert to string using forward slashes for consistency
            return str(relative_p).replace(os.sep, "/")
        except ValueError:
            # If the path is not relative to root_dir, return its string representation
            warn_msg = (
                f"File path {file_path} is not relative to root {self.root_dir}. "
                f"Returning original path string."
            )
            logger.warning(warn_msg)
            return str(file_path).replace(os.sep, "/")
        except Exception as e:
            logger.error(f"Error getting relative path for {file_path}: {e}", exc_info=True)
            return str(file_path).replace(os.sep, "/")  # Fallback

    def _get_last_modified_time(self, file_path: Path) -> Optional[str]:
        """Gets the last modified time of the file in UTC ISO format."""
        try:
            mtime_timestamp = file_path.stat().st_mtime
            mtime_dt_utc = datetime.datetime.fromtimestamp(mtime_timestamp, datetime.timezone.utc)
            return mtime_dt_utc.isoformat()
        except (OSError, FileNotFoundError) as e:
            logger.warning(f"Could not get last modified time for {file_path}: {e}")
            return None

    # --- Detection Helper Functions ---
    # (Largely unchanged, but ensure they handle edge cases gracefully)

    def _detect_subsystem(self, file_path: Path) -> str:
        """Detect the subsystem based on the file path relative to root."""
        try:
            relative_path = file_path.resolve().relative_to(self.root_dir)
            path_parts = relative_path.parts

            # Check if the first part is 'subsystems' and the second part is a known subsystem
            if len(path_parts) > 1 and path_parts[0].lower() == "subsystems":
                subsystem_name = path_parts[1].upper()  # Standardize to upper
                # Add all known subsystem names here
                known_subsystems = [
                    "ETHIK",
                    "ATLAS",
                    "NEXUS",
                    "CRONOS",
                    "KOIOS",
                    "MYCELIUM",
                    "HARMONY",
                    "TRANSLATOR",
                    "CORUJA",
                    "MCP",
                ]
                if subsystem_name in known_subsystems:
                    return subsystem_name

            # Fallback or alternative detection logic if needed
            # Maybe check for other top-level dirs like 'docs', 'tests'?
            if path_parts[0].lower() == "docs":
                return "DOCUMENTATION"
            if path_parts[0].lower() == "tests":
                return "TESTING"

        except ValueError:
            # Path not relative to root, cannot determine subsystem reliably this way
            debug_msg = (
                f"Path {file_path} not in project root {self.root_dir}. "
                f"Cannot reliably detect subsystem."
            )
            logger.debug(debug_msg)
        except Exception as e:
            logger.error(f"Error detecting subsystem for {file_path}: {e}", exc_info=True)

        return "UNKNOWN"

    def _detect_purpose(self, file_path: Path) -> str:
        """Detect the purpose of the file based on its type and name."""
        file_name = file_path.name
        file_ext = file_path.suffix.lower()
        parent_dir = file_path.parent.name.lower()

        if parent_dir == "tests" or file_name.startswith("test_") or file_name.endswith("_test.py"):
            return "TESTING"
        elif parent_dir == "config":
            return "CONFIGURATION"
        elif parent_dir == "docs":
            return "DOCUMENTATION"
        elif file_name.lower() in ["readme.md", "contributing.md", "license", "changelog.md"]:
            return "DOCUMENTATION"
        elif file_ext == ".py":
            if file_name == "__init__.py":
                return "PACKAGE_INIT"
            if parent_dir == "core":
                return "CORE_LOGIC"
            if parent_dir == "services":
                return "SERVICE"
            if parent_dir == "utils":
                return "UTILITY"
            if parent_dir == "interfaces":
                return "INTERFACE"
            return "PYTHON_MODULE"  # General fallback
        elif file_ext == ".md":
            return "DOCUMENTATION"
        elif file_ext in [".json", ".yaml", ".yml", ".toml"]:
            return "CONFIGURATION"
        elif file_ext in [".sh", ".bat", ".ps1"]:
            return "SCRIPT"
        # Add more rules as needed
        else:
            return "GENERAL_ASSET"

    def _detect_category(self, file_type: str) -> str:
        """Detect the category of the file based on its type."""
        if file_type == ".py":
            return "code"
        elif file_type == ".md":
            return "documentation"
        elif file_type in [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"]:
            return "configuration"
        elif file_type in [".sh", ".bat", ".ps1", ".bash"]:
            return "script"
        elif file_type in [".txt", ".log", ".csv"]:
            return "data"
        elif file_type in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"]:
            return "image"
        else:
            return "other"

    def _detect_encoding(self, file_path: Path) -> Optional[str]:
        """Attempt to detect the file encoding."""
        # Basic check for common encodings. Could use a library like `chardet`
        # for more robust detection, but adds a dependency.
        # For simplicity, we'll try utf-8 first.
        try:
            with open(file_path, "rb") as f:
                f.read().decode("utf-8")
            return "utf-8"
        except UnicodeDecodeError:
            # Try other common encodings if utf-8 fails
            for enc in self.supported_encodings[1:]:  # Skip utf-8 as already tried
                try:
                    with open(file_path, "rb") as f:
                        f.read().decode(enc)
                    return enc
                except UnicodeDecodeError:
                    continue
            logger.warning(f"Could not detect encoding for {file_path} using common types.")
            return None  # Indicate failure or fallback needed
        except (IOError, OSError) as e:
            logger.error(f"Error reading file {file_path} for encoding detection: {e}")
            return None

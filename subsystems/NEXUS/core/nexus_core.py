#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NEXUS (Neural Evolution and Xenial Unified System) Core Logic
=============================================================

Core implementation of the modular analysis system for EGOS.
Provides capabilities for code analysis, dependency mapping, and improvement suggestions.

Version: 1.0.0 (Migrated)
"""

# import numpy as np  # Removed unused import
# import pandas as pd # Removed unused import
# from sklearn.feature_extraction.text import TfidfVectorizer # Removed unused import
# from sklearn.metrics.pairwise import cosine_similarity # Removed unused import
import ast
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from koios.logger import KoiosLogger

from .ast_visitor import analyze_code as ast_analyze_code

# Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)
# Removed unused module-level logger
# logger = KoiosLogger.get_logger("NEXUS.Core")


class NEXUSCore:
    """Core class for NEXUS analysis and cartography.

    Provides functionalities to analyze Python code files, map dependencies
    within a workspace, suggest improvements based on metrics, and export
    analysis results.
    """

    def __init__(
        self,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None,
        project_root: Optional[Path] = None,
    ):
        """Initialize NEXUS core.

        Args:
            config (Dict[str, Any]): Configuration dictionary, potentially including
                                     thresholds for suggestions.
            logger (Optional[logging.Logger]): Logger instance for logging messages.
                                         If None, will use KoiosLogger.get_logger("NEXUS.Core").
            project_root (Optional[Path]): The absolute path to the root of the project
                                             being analyzed. If None, will try to
                                             determine from current dir.
        """
        self.config = config

        # Use provided logger or get a KoiosLogger
        self.logger = logger or KoiosLogger.get_logger("NEXUS.Core")

        # Set or determine project_root
        if project_root is None:
            # Try to determine from current directory (may not be reliable)
            # This is a fallback if no project_root is provided
            try:
                # Start from current directory and go up looking for a .git folder or similar
                self.project_root = Path.cwd()
                self.logger.warning(
                    f"No project_root provided, using current directory: {self.project_root}"
                )
            except Exception as e:
                self.logger.error(f"Failed to determine project root: {e}")
                self.project_root = Path.cwd()  # Default to current directory
        else:
            self.project_root = project_root

        self.logger.info("NEXUS Core initialized.")

    def analyze_code(self, file_path: str) -> Optional[Dict]:
        """Analyze a single Python code file using AST.

        Extracts metrics like line count, complexity, imports, functions, and classes.

        Args:
            file_path (str): The absolute or relative path to the Python file.

        Returns:
            Optional[Dict]: A dictionary containing analysis metrics, or None if the
                            file is not found. Returns a dict with an 'error' key
                            if analysis fails.
        """
        self.logger.debug(f"Analyzing file: {file_path}")
        try:
            # Basic check if file exists
            if not Path(file_path).is_file():
                self.logger.error(f"File not found for analysis: {file_path}")
                return None

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Use AST-based analysis
            ast_metrics = ast_analyze_code(content, self.logger)
            if "error" in ast_metrics:
                self.logger.error(f"AST analysis error for {file_path}: {ast_metrics['error']}")
                return ast_metrics

            metrics = {
                "lines": len(content.splitlines()),
                "chars": len(content),
                "complexity": {"cognitive_load": ast_metrics["cognitive_load"]},
                # Store raw import details for later categorization
                "_raw_imports": ast_metrics["imports"],
                # 'imports': [ # Remove direct formatting here
                #     f"{'from ' + imp['module'] + ' ' if imp['is_from_import'] else ''}"
                #     f"import {', '.join(imp['names']) if imp['names'] else imp['module']}"
                #     f"{' as ' + imp['alias'] if imp['alias'] else ''}"
                #     for imp in ast_metrics['imports']
                # ],
                "functions": [
                    {
                        "name": func["name"],
                        "params": func["args"],
                        "doc": func["docstring"] or "No docstring",
                        "line": func["start_line"],
                        "end_line": func["end_line"],
                        "is_async": func["is_async"],
                        "decorators": func["decorators"],
                    }
                    for func in ast_metrics["functions"]
                ],
                "classes": [
                    {
                        "name": cls["name"],
                        "inheritance": ", ".join(cls["bases"]),
                        "doc": cls["docstring"] or "No docstring",
                        "line": cls["start_line"],
                        "end_line": cls["end_line"],
                        "decorators": cls["decorators"],
                        "methods": [
                            {
                                "name": method["name"],
                                "params": method["args"],
                                "doc": method["docstring"] or "No docstring",
                                "line": method["start_line"],
                                "end_line": method["end_line"],
                                "is_async": method["is_async"],
                                "decorators": method["decorators"],
                            }
                            for method in cls["methods"]
                        ],
                    }
                    for cls in ast_metrics["classes"]
                ],
            }

            self.logger.info(f"Analyzed file: {file_path} - {metrics['lines']} lines")
            return metrics
        except FileNotFoundError:
            self.logger.error(f"File not found during analysis: {file_path}")
            return None
        except Exception as e:
            self.logger.exception(f"Error analyzing file {file_path}: {e}")
            return {"error": f"Failed to analyze {file_path}: {e}"}

    def analyze_dependencies(self, python_files: List[str]) -> Dict:
        """Analyze dependencies between a list of Python files.

        Parses import statements using AST, resolves relative/absolute paths,
        and builds a map of which files import others, categorized into internal,
        external, and unresolved imports.

        Args:
            python_files (List[str]): A list of absolute or relative paths to Python
                                      files within the project.

        Returns:
            Dict: A dictionary where keys are file paths. Each value is a dict with:
                  - 'internal_imports' (List[str]): Imports resolved within the project.
                  - 'external_imports' (List[str]): Imports assumed to be from external packages.
                  - 'unresolved_imports' (List[str]): Imports that could not be resolved locally.
                  - 'imported_by' (List[str]): List of files importing this key file.
                  An 'error' key may be present if AST parsing failed for a file.
        """
        self.logger.info("Analyzing dependencies...")

        dependencies: Dict[str, Dict[str, List[str]]] = {}
        module_to_path: Dict[str, str] = {}
        all_import_details: Dict[
            str, List[Dict[str, Any]]
        ] = {}  # file_path -> list of import details

        # Heuristic set of likely external/standard library top-level modules
        # TODO: Make this configurable or more robust
        known_external_modules = {
            "os",
            "sys",
            "logging",
            "json",
            "re",
            "collections",
            "math",
            "datetime",
            "pathlib",
            "asyncio",
            "typing",
            "abc",
            "unittest",
            "pytest",
            "requests",
            "numpy",
            "pandas",
            "sklearn",
            "fastapi",
            "uvicorn",
            "pydantic",
            "koios",
            "mycelium",  # Consider EGOS subsystems external for now
            # if imported directly? Maybe not.
            # Add other common libraries used in the project here
        }
        # Also consider EGOS subsystems if imported absolutely
        egos_subsystems = {
            "subsystems." + d
            for d in os.listdir(self.project_root / "subsystems")
            if os.path.isdir(self.project_root / "subsystems" / d) and not d.startswith("_")
        }

        # First pass: Initialize dictionary, map module names to paths,
        # and parse AST for import details
        for file_path_str in python_files:
            file_path = Path(file_path_str).resolve()  # Ensure absolute paths
            relative_path_str = str(file_path.relative_to(self.project_root))  # For display/keys

            dependencies[relative_path_str] = {
                "internal_imports": [],
                "external_imports": [],
                "unresolved_imports": [],
                "imported_by": [],
            }
            all_import_details[relative_path_str] = []
            module_name = self._path_to_module_str(str(file_path))
            if module_name:
                module_to_path[module_name] = relative_path_str  # Store relative path as value

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                tree = ast.parse(content, filename=str(file_path))

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            import_info = {
                                "module": alias.name,
                                "names": [],
                                "alias": alias.asname,
                                "is_from_import": False,
                                "level": 0,  # Absolute import
                                "lineno": node.lineno,
                            }
                            all_import_details[relative_path_str].append(import_info)
                            # Don't add to dependencies['imports'] here anymore

                    elif isinstance(node, ast.ImportFrom):
                        module = node.module if node.module else ""  # Handle 'from . import ...'
                        level = node.level  # Relative import level

                        # Handle cases like 'from .submodule import *' -
                        # less precise but capture intent
                        imported_names = [alias.name for alias in node.names if alias.name != "*"]
                        has_wildcard = any(alias.name == "*" for alias in node.names)
                        if has_wildcard:
                            imported_names.append("*")  # Represent wildcard if present

                        # If names are specified, record them. If not
                        # If names are specified, record them.
                        # If not (e.g. from . import submodule),
                        # module itself is the key part.
                        import_info = {
                            "module": module,
                            "names": imported_names,
                            # 'as' not applicable here directly for names,
                            # handled per name if needed
                            "alias": None,
                            "is_from_import": True,
                            "level": level,
                            "lineno": node.lineno,
                        }
                        all_import_details[relative_path_str].append(import_info)
                        # Don't add to dependencies['imports'] here anymore

            except FileNotFoundError:
                self.logger.error(
                    f"File not found during dependency analysis first pass: {file_path_str}"
                )
                dependencies[relative_path_str]["error"] = f"File not found: {file_path_str}"
            except SyntaxError as e:
                self.logger.error(f"Syntax error parsing {file_path_str} for dependencies: {e}")
                dependencies[relative_path_str]["error"] = f"Syntax error: {e}"
            except Exception as e:
                self.logger.exception(
                    f"Error in first pass analyzing {file_path_str} for dependencies: {e}"
                )
                dependencies[relative_path_str]["error"] = f"Analysis error: {e}"

        # Second pass: Resolve imports and categorize
        for importing_file_rel, imports in all_import_details.items():
            if "error" in dependencies[importing_file_rel]:
                continue  # Skip files that failed initial parsing

            importing_file_abs = self.project_root / importing_file_rel

            for imp in imports:
                resolved_module_str: Optional[str] = None
                import_display_str = self._format_import_display(
                    imp
                )  # Helper to format for output lists

                try:
                    if imp["level"] > 0:  # Relative import
                        # Attempt to resolve relative path
                        current_dir = importing_file_abs.parent
                        # Go up 'level' directories (minus 1 since level 1 is current dir)
                        for _ in range(imp["level"] - 1):
                            current_dir = current_dir.parent

                        if imp["module"]:  # e.g., from ..submodule import name
                            resolved_module_path_base = current_dir / imp["module"].replace(
                                ".", os.sep
                            )
                        else:  # e.g., from . import name
                            resolved_module_path_base = current_dir

                        # Check if it's a package (directory with __init__.py)
                        # or a module (.py file)
                        potential_module_path = resolved_module_path_base.with_suffix(".py")
                        potential_package_path = resolved_module_path_base / "__init__.py"

                        if potential_module_path.exists() and potential_module_path.is_file():
                            resolved_module_str = self._path_to_module_str(
                                str(potential_module_path)
                            )
                        elif potential_package_path.exists() and potential_package_path.is_file():
                            resolved_module_str = self._path_to_module_str(
                                str(resolved_module_path_base)
                            )  # Use dir path for package

                    else:  # Absolute import
                        resolved_module_str = imp["module"]

                    # --- Categorization Logic ---
                    if resolved_module_str:
                        # Check if it resolves to a known internal module
                        if resolved_module_str in module_to_path:
                            imported_file_rel = module_to_path[resolved_module_str]
                            dependencies[importing_file_rel]["internal_imports"].append(
                                import_display_str
                            )
                            if (
                                imported_file_rel in dependencies
                                and importing_file_rel != importing_file_rel
                            ):  # Avoid self-imports in list
                                dependencies[imported_file_rel]["imported_by"].append(
                                    importing_file_rel
                                )
                        # Check if it looks like an EGOS subsystem absolute import
                        elif (
                            resolved_module_str.startswith("subsystems.")
                            and resolved_module_str in egos_subsystems
                        ):
                            # Treat absolute subsystem imports as internal? Or special category?
                            # Let's say internal for now.
                            # Need to find the actual file path it corresponds to if possible.

                            potential_path_str = str(
                                self.project_root / resolved_module_str.replace(".", os.sep)
                            )
                            potential_module_path = Path(potential_path_str + ".py")
                            potential_package_path = Path(potential_path_str) / "__init__.py"
                            found_internal = False
                            if potential_module_path.exists() and potential_module_path.is_file():
                                target_rel_path = str(
                                    potential_module_path.relative_to(self.project_root)
                                )
                                if target_rel_path in dependencies:
                                    dependencies[importing_file_rel]["internal_imports"].append(
                                        import_display_str
                                    )
                                    dependencies[target_rel_path]["imported_by"].append(
                                        importing_file_rel
                                    )
                                    found_internal = True
                            elif (
                                potential_package_path.exists() and potential_package_path.is_file()
                            ):
                                target_rel_path = str(
                                    Path(potential_path_str).relative_to(self.project_root)
                                )  # Use dir path
                                # Check if the *directory* corresponds to a mapped module key
                                # (e.g., subsystems.NEXUS)
                                mapped_module_key = self._path_to_module_str(potential_path_str)
                                if mapped_module_key in module_to_path:
                                    target_rel_path_key = module_to_path[mapped_module_key]
                                    if target_rel_path_key in dependencies:
                                        dependencies[importing_file_rel]["internal_imports"].append(
                                            import_display_str
                                        )
                                        dependencies[target_rel_path_key]["imported_by"].append(
                                            importing_file_rel
                                        )
                                        found_internal = True
                            if not found_internal:
                                # It looked like a subsystem but wasn't found/mapped? Unresolved.
                                dependencies[importing_file_rel]["unresolved_imports"].append(
                                    f"{import_display_str} # Attempted subsystem import"
                                )

                        # Check if top-level module is known external/stdlib
                        elif resolved_module_str.split(".")[0] in known_external_modules:
                            dependencies[importing_file_rel]["external_imports"].append(
                                import_display_str
                            )
                        else:
                            # Not resolved internally, not obviously external -> Unresolved
                            dependencies[importing_file_rel]["unresolved_imports"].append(
                                import_display_str
                            )
                    else:
                        # Could not resolve module string (e.g., complex relative path issue)
                        dependencies[importing_file_rel]["unresolved_imports"].append(
                            f"{import_display_str} # Resolution failed"
                        )

                except Exception as e:
                    self.logger.warning(
                        f"Error resolving/categorizing import '{import_display_str}' "
                        f"in {importing_file_rel}: {e}"
                    )
                    # Add to unresolved if resolution fails unexpectedly
                    dependencies[importing_file_rel]["unresolved_imports"].append(
                        f"{import_display_str} # Categorization error: {e}"
                    )

        self.logger.info(f"Dependency analysis complete for {len(python_files)} files.")
        return dependencies

    def _path_to_module_str(self, file_path_str: str) -> Optional[str]:
        """Converts an absolute file path within the project to a Python module string."""
        try:
            file_path = Path(file_path_str).resolve()
            # Ensure it's within the project root before proceeding
            if not file_path_str.startswith(str(self.project_root)):
                self.logger.warning(
                    f"{file_path_str} is outside project root {self.project_root}. "
                    "Cannot determine module string."
                )
                return None  # Couldn't determine module string

            relative_path = file_path.relative_to(self.project_root)

            # Handle __init__.py -> package name
            if relative_path.name == "__init__.py":
                parts = list(relative_path.parent.parts)
            else:
                parts = list(relative_path.with_suffix("").parts)

            # Handle case where file is directly in project root (shouldn't be common for modules)
            if not parts:
                return None  # Or handle filename as module name if needed

            # Check if starts with 'subsystems' explicitly
            # if parts[0] != 'subsystems':
            # Decide how to handle modules not in 'subsystems'
            # For now, assume they follow standard Python path conversion
            # pass

            return ".".join(parts)
        except ValueError:  # Not relative to project root
            self.logger.warning(
                f"Could not determine module string for {file_path_str} "
                f"relative to {self.project_root}."
            )
            return None
        except Exception as e:
            self.logger.exception(f"Error converting path {file_path_str} to module string: {e}")
            return None

    def _format_import_display(self, imp: Dict[str, Any]) -> str:
        """Formats the raw import dictionary into a display string."""
        if imp["is_from_import"]:
            relative_dots = "." * imp["level"]
            module_part = imp["module"] if imp["module"] else ""
            from_part = (
                f"from {relative_dots}{module_part} " if (relative_dots or module_part) else "from "
            )  # Handle 'from . import X' edge case
            # Handle imported names
            if "*" in imp["names"]:
                names_part = "*"
            else:
                # For simplicity, just join names. Handling individual aliases here adds complexity.
                names_part = ", ".join(imp["names"])
            return f"{from_part}import {names_part}"
        else:
            # Handle simple import with potential alias
            alias_part = f" as {imp['alias']}" if imp["alias"] else ""
            return f"import {imp['module']}{alias_part}"

    def analyze_workspace(self, exclude_dirs: Optional[List[str]] = None) -> Dict:
        """Analyze all Python files in the workspace root directory.

        Collects all .py files (excluding .venv, __pycache__), analyzes each one,
        calculates aggregate metrics, and analyzes inter-file dependencies.

        Returns:
            Dict: A nested dictionary containing:
                  - 'metrics': Aggregated workspace metrics (file count, lines, etc.).
                  - 'files': Analysis dictionary for each file (from analyze_code).
                  - 'dependencies': Dependency map (from analyze_dependencies).
        """
        self.logger.info("Starting workspace analysis...")

        # Collect Python files
        python_files = []
        for root, _, files in os.walk(self.project_root):
            if ".venv" in root or "__pycache__" in root:
                continue
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))

        # Analyze each file
        analysis = {
            "metrics": {
                "total_files": len(python_files),
                "total_lines": 0,
                "total_functions": 0,
                "total_classes": 0,
                "avg_complexity": 0.0,
            },
            "files": {},
            "dependencies": None,
        }

        complexities = []

        for file_path in python_files:
            file_analysis = self.analyze_code(file_path)
            if file_analysis and "error" not in file_analysis:
                analysis["files"][file_path] = file_analysis
                analysis["metrics"]["total_lines"] += file_analysis["lines"]
                analysis["metrics"]["total_functions"] += len(file_analysis["functions"])
                analysis["metrics"]["total_classes"] += len(file_analysis["classes"])
                complexities.append(file_analysis["complexity"]["cognitive_load"])

        if complexities:
            analysis["metrics"]["avg_complexity"] = sum(complexities) / len(complexities)

        # Analyze dependencies
        analysis["dependencies"] = self.analyze_dependencies(python_files)

        self.logger.info("Workspace analysis complete.")
        return analysis

    def suggest_improvements(self, workspace_analysis: Dict) -> List[Dict]:
        """Generate improvement suggestions based on workspace analysis.

        Checks metrics like cognitive load, import count, dependency count,
        and docstring coverage against configurable thresholds.

        Args:
            workspace_analysis (Dict): The dictionary returned by analyze_workspace().

        Returns:
            List[Dict]: A list of suggestion dictionaries, each containing 'type',
                        'file', 'severity', and 'message'.
        """
        suggestions = []
        thresholds = self.config.get("analysis", {}).get("suggestions", {})

        for file_path, analysis in workspace_analysis.get("files", {}).items():
            # Check cognitive load
            cognitive_load = analysis.get("complexity", {}).get("cognitive_load", 0)
            if cognitive_load > thresholds.get("cognitive_load_threshold_high", 50):
                suggestions.append(
                    {
                        "type": "complexity",
                        "file": file_path,
                        "severity": "high",
                        "message": (
                            f"High cognitive load ({cognitive_load:.1f}). "
                            "Consider breaking down into smaller functions."
                        ),
                    }
                )

            # Check import count
            import_count = len(analysis.get("imports", []))
            if import_count > thresholds.get("imports_threshold", 15):
                suggestions.append(
                    {
                        "type": "imports",
                        "file": file_path,
                        "severity": "medium",
                        "message": (
                            f"High number of imports ({import_count}). "
                            "Consider modularizing or using composition."
                        ),
                    }
                )

            # Check dependency count
            if workspace_analysis.get("dependencies"):
                imported_by = (
                    workspace_analysis["dependencies"].get(file_path, {}).get("imported_by", [])
                )
                if len(imported_by) > thresholds.get("imported_by_threshold", 10):
                    suggestions.append(
                        {
                            "type": "dependencies",
                            "file": file_path,
                            "severity": "medium",
                            "message": (
                                f"Module {file_path} is imported by {len(imported_by)} files. "
                                "Consider if it should be split into smaller, more focused modules."
                            ),
                        }
                    )

            # Check docstring coverage
            for func in analysis.get("functions", []):
                if func.get("doc") in ["No docstring", None, ""]:
                    suggestions.append(
                        {
                            "type": "documentation",
                            "file": file_path,
                            "severity": "low",
                            "message": f"Function {func['name']} lacks a docstring.",
                        }
                    )

            for cls in analysis.get("classes", []):
                if cls.get("doc") in ["No docstring", None, ""]:
                    suggestions.append(
                        {
                            "type": "documentation",
                            "file": file_path,
                            "severity": "low",
                            "message": f"Class {cls['name']} lacks a docstring.",
                        }
                    )
                for method in cls.get("methods", []):
                    if method.get("doc") in ["No docstring", None, ""]:
                        suggestions.append(
                            {
                                "type": "documentation",
                                "file": file_path,
                                "severity": "low",
                                "message": (
                                    f"Method {cls['name']}.{method['name']} lacks a docstring."
                                ),
                            }
                        )

        return suggestions

    def export_analysis(self, data: Dict, format: str = "json") -> Optional[str]:
        """Export analysis results in the specified format (JSON or Markdown).

        Args:
            data (Dict): The analysis data dictionary (e.g., from analyze_workspace).
            format (str, optional): The desired output format ('json' or 'md').
                                     Defaults to 'json'.

        Returns:
            Optional[str]: A string containing the exported data in the specified format,
                           or None if an error occurs or format is unsupported.
        """
        self.logger.debug(f"Exporting analysis data in format: {format}")
        try:
            if format == "json":
                return json.dumps(data, indent=2, default=str)
            elif format == "md":
                return self._convert_to_markdown(data)
            else:
                self.logger.error(f"Unsupported export format requested: {format}")
                raise ValueError(f"Unsupported export format: {format}")
        except Exception as e:
            self.logger.exception(f"Error exporting analysis: {e}")
            return None

    def _convert_to_markdown(self, data: Dict) -> str:
        """Convert analysis data dictionary to a Markdown formatted string.

        Args:
            data (Dict): The analysis data dictionary.

        Returns:
            str: A Markdown formatted report string.
        """
        md = ["# NEXUS Analysis Report\n"]
        # Debug line removed for brevity and line length compliance

        if "metrics" in data:
            md.append("## Overall Metrics\n")
            for key, value in data.get("metrics", {}).items():
                md.append(f"- **{key.replace('_', ' ').title()}**: {value}\n")

        if "files" in data:
            md.append("\n## File Analysis\n")
            for file_path, analysis in data["files"].items():
                # Use basename for File Analysis headers too for consistency
                filename = os.path.basename(file_path)
                md.append(f"\n### `{filename}`\n")
                md.append(f"- Full Path: `{file_path}`\n")  # Optionally add full path
                md.append(f"- Lines: {analysis['lines']}\n")
                md.append(f"- Cognitive Load: {analysis['complexity']['cognitive_load']:.1f}\n")

                if analysis.get("imports"):
                    md.append("\n#### Imports\n")
                    for imp in analysis["imports"]:
                        md.append(f"- `{imp}`\n")

                if analysis.get("classes"):
                    md.append("\n#### Classes\n")
                    for cls in analysis["classes"]:
                        md.append(f"\n##### `{cls['name']}`\n")
                        if cls["inheritance"]:
                            md.append(f"Inherits from: `{cls['inheritance']}`\n")
                        if cls["doc"] != "No docstring":
                            md.append(f"\n{cls['doc']}\n")
                        if cls["methods"]:
                            md.append("\nMethods:\n")
                            for method in cls["methods"]:
                                md.append(f"- `{method['name']}({', '.join(method['params'])})`\n")

                if analysis.get("functions"):
                    md.append("\n#### Functions\n")
                    for func in analysis["functions"]:
                        md.append(f"\n##### `{func['name']}`\n")
                        md.append(
                            f"```python\ndef {func['name']}({', '.join(func['params'])})\n```\n"
                        )
                        if func["doc"] != "No docstring":
                            md.append(f"\n{func['doc']}\n")

        if "dependencies" in data and data["dependencies"]:
            md.append("\n## Dependencies\n")
            # Debug line removed for brevity and line length compliance
            for file_path, deps in data["dependencies"].items():
                # Use basename for Dependencies headers
                filename = os.path.basename(file_path)
                # Debug logging removed for brevity
                md.append(f"\n### `{filename}`\n")
                md.append(f"- Full Path: `{file_path}`\n")  # Optionally add full path
                if deps.get("imports"):
                    md.append("\nImports:\n")
                    for imp in deps["imports"]:
                        md.append(f"- `{imp}`\n")
                if deps.get("imported_by"):
                    md.append("\nImported by:\n")
                    for imp_by_path in deps["imported_by"]:
                        imp_by_filename = os.path.basename(imp_by_path)
                        md.append(f"- `{imp_by_filename}` (`{imp_by_path}`)\n")

        # Debug line removed for brevity and line length compliance
        # self.logger.debug("Finished Markdown conversion.") # REMOVED DEBUG
        return "".join(md)

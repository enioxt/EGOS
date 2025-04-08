#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - NEXUS Core Tests
===============================

Test suite for the NEXUS Core logic.

Version: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Dict

import pytest

# Use absolute import now that project is installed editably
from subsystems.NEXUS.core.nexus_core import NEXUSCore


# Fixture for basic config
@pytest.fixture
def nexus_config() -> Dict:
    return {
        "analysis": {
            "suggestions": {
                "cognitive_load_threshold_high": 50,
                "imports_threshold": 15,
                "imported_by_threshold": 10,
            }
        },
        # Add a default empty list for external modules if needed by tests
        # Or rely on the hardcoded list in NEXUSCore for now
        # "known_external_modules": []
    }


# Fixture for a logger
@pytest.fixture
def test_logger() -> logging.Logger:
    logger = logging.getLogger("TestNEXUSCore")
    logger.setLevel(logging.DEBUG)  # Keep DEBUG for detailed test output
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False  # Prevent duplicate logging if root logger has handler
    return logger


# Fixture for the project root using pytest's tmp_path
@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    # Create dummy structure for testing workspace analysis
    # src/module_a.py
    (tmp_path / "src").mkdir()
    module_a_content = """
import os
import logging
from typing import List, Optional

def func_a(x: int, y: Optional[str] = None) -> List[str]:
    \"\"\"Example function with docstring.\"\"\"
    if x > 0:
        # logging.info('Test log') # Add external lib usage
        return [y or 'default'] * x
    return []

class ClassA:
    \"\"\"Example class with docstring.\"\"\"
    pass
"""
    (tmp_path / "src" / "module_a.py").write_text(module_a_content)

    # src/module_b.py
    module_b_content = """
from .module_a import ClassA, func_a # Relative import
import datetime as dt # External/Stdlib import
from pathlib import Path # External/Stdlib import
import non_existent_module # Unresolved import
from .. import outside_src # Unresolved relative import (goes outside src)

class B(ClassA):
    def run(self) -> None:
        func_a(5)
"""
    (tmp_path / "src" / "module_b.py").write_text(module_b_content)

    # tests/test_a.py
    (tmp_path / "tests").mkdir()
    test_a_content = """
from src.module_a import func_a # Internal absolute import (using src prefix)
import pytest # External import
from . import utils # Unresolved relative import (no tests/utils.py)

def test_func_a():
    pass
"""
    (tmp_path / "tests" / "test_a.py").write_text(test_a_content)

    # Create __init__.py files to make them packages
    (tmp_path / "src" / "__init__.py").touch()
    (tmp_path / "tests" / "__init__.py").touch()

    # Create ignored files
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "ignored.py").write_text("print('ignored')")

    return tmp_path


# Fixture for NEXUSCore instance
@pytest.fixture
def nexus(nexus_config, test_logger, project_root) -> NEXUSCore:
    # Pass the actual project root determined by the fixture
    return NEXUSCore(config=nexus_config, logger=test_logger, project_root=project_root)


# --- Test Cases --- #


def test_nexus_initialization(nexus, nexus_config, test_logger, project_root):
    """Test basic initialization of NEXUSCore."""
    assert nexus.config == nexus_config
    assert nexus.logger == test_logger
    assert nexus.project_root == project_root


def test_analyze_code_success(nexus, project_root):
    """Test analyzing a valid Python file."""
    file_to_analyze = project_root / "src" / "module_a.py"
    analysis = nexus.analyze_code(str(file_to_analyze))

    assert analysis is not None
    assert "error" not in analysis
    assert analysis["lines"] > 0
    assert analysis["chars"] > 0
    assert "complexity" in analysis
    assert analysis["complexity"]["cognitive_load"] > 0

    # Check raw imports extracted (used by analyze_dependencies)
    assert "_raw_imports" in analysis
    raw_imports = analysis["_raw_imports"]
    assert len(raw_imports) == 3
    assert any(imp["module"] == "os" for imp in raw_imports)
    assert any(imp["module"] == "logging" for imp in raw_imports)
    assert any(imp["module"] == "typing" and "List" in imp["names"] for imp in raw_imports)

    assert len(analysis["functions"]) == 1
    assert analysis["functions"][0]["name"] == "func_a"
    assert len(analysis["classes"]) == 1
    assert analysis["classes"][0]["name"] == "ClassA"


def test_analyze_code_file_not_found(nexus, project_root):
    """Test analyzing a non-existent file."""
    non_existent_file = project_root / "src" / "no_such_file.py"
    analysis = nexus.analyze_code(str(non_existent_file))
    assert analysis is None


def test_analyze_dependencies_categorization(nexus: NEXUSCore, project_root: Path):
    """Test dependency analysis with categorization."""
    # Use relative paths for keys as expected by the modified function
    module_a_rel = "src/module_a.py"
    module_b_rel = "src/module_b.py"
    test_a_rel = "tests/test_a.py"

    # Get absolute paths for analysis input
    py_files_abs = [
        str(project_root / module_a_rel),
        str(project_root / module_b_rel),
        str(project_root / test_a_rel),
    ]

    dependencies = nexus.analyze_dependencies(py_files_abs)

    assert dependencies is not None
    assert module_a_rel in dependencies
    assert module_b_rel in dependencies
    assert test_a_rel in dependencies

    # --- Check module_a.py imports ---
    deps_a = dependencies[module_a_rel]
    assert not deps_a["internal_imports"]  # No internal imports
    assert len(deps_a["external_imports"]) == 3
    assert any("import os" in imp for imp in deps_a["external_imports"])
    assert any("import logging" in imp for imp in deps_a["external_imports"])
    assert any("from typing import List, Optional" in imp for imp in deps_a["external_imports"])
    assert not deps_a["unresolved_imports"]
    assert module_b_rel in deps_a["imported_by"]
    assert test_a_rel in deps_a["imported_by"]  # Note: imports 'src.module_a'

    # --- Check module_b.py imports ---
    deps_b = dependencies[module_b_rel]
    assert len(deps_b["internal_imports"]) == 1
    assert any("from .module_a import ClassA, func_a" in imp for imp in deps_b["internal_imports"])
    assert len(deps_b["external_imports"]) == 2
    assert any("import datetime as dt" in imp for imp in deps_b["external_imports"])
    assert any("from pathlib import Path" in imp for imp in deps_b["external_imports"])
    assert len(deps_b["unresolved_imports"]) == 2
    assert any("import non_existent_module" in imp for imp in deps_b["unresolved_imports"])
    # Note: 'from .. import outside_src' might fail resolution or be marked unresolved
    assert any("from .. import outside_src" in imp for imp in deps_b["unresolved_imports"])
    assert not deps_b["imported_by"]

    # --- Check test_a.py imports ---
    deps_test_a = dependencies[test_a_rel]
    assert len(deps_test_a["internal_imports"]) == 1
    # Module path conversion might make this 'src.module_a'
    assert any("from src.module_a import func_a" in imp for imp in deps_test_a["internal_imports"])
    assert len(deps_test_a["external_imports"]) == 1
    assert any("import pytest" in imp for imp in deps_test_a["external_imports"])
    assert len(deps_test_a["unresolved_imports"]) == 1
    assert any("from . import utils" in imp for imp in deps_test_a["unresolved_imports"])
    assert not deps_test_a["imported_by"]


def test_analyze_workspace(nexus, project_root):
    """Test analyzing the entire dummy workspace."""
    # Define expected relative paths based on the fixture
    expected_files_rel = {
        "src/module_a.py",
        "src/module_b.py",
        "tests/test_a.py",
        "src/__init__.py",
        "tests/__init__.py",
    }

    workspace_analysis = nexus.analyze_workspace()

    assert workspace_analysis is not None
    assert workspace_analysis["metrics"]["total_files"] == len(expected_files_rel)

    # Check that the keys in 'files' and 'dependencies' are the relative paths
    file_keys = {str(Path(p).relative_to(project_root)) for p in workspace_analysis["files"].keys()}
    dep_keys = set(workspace_analysis["dependencies"].keys())

    assert file_keys == expected_files_rel
    assert dep_keys == expected_files_rel

    # Check a dependency link based on relative paths
    assert (
        "src/module_a.py"
        in workspace_analysis["dependencies"]["src/module_b.py"]["internal_imports"]
    )
    assert "src/module_b.py" in workspace_analysis["dependencies"]["src/module_a.py"]["imported_by"]


def test_suggest_improvements(nexus, project_root):
    """Test improvement suggestions (basic checks)."""
    # Modify config for testing suggestions
    nexus.config["analysis"]["suggestions"]["cognitive_load_threshold_high"] = 1
    nexus.config["analysis"]["suggestions"]["imports_threshold"] = 1
    nexus.config["analysis"]["suggestions"]["imported_by_threshold"] = 1

    workspace_analysis = nexus.analyze_workspace()
    suggestions = nexus.suggest_improvements(workspace_analysis)

    assert isinstance(suggestions, list)
    # Check if *some* suggestions are generated based on low thresholds
    assert len(suggestions) > 0

    # Example check for specific types (adapt based on actual dummy code metrics)
    has_complexity_suggestion = any(s["type"] == "complexity" for s in suggestions)
    has_import_suggestion = any(s["type"] == "imports" for s in suggestions)
    has_dependency_suggestion = any(s["type"] == "dependencies" for s in suggestions)
    has_doc_suggestion = any(s["type"] == "documentation" for s in suggestions)

    # Based on dummy code:
    assert has_complexity_suggestion  # func_a likely > 1
    assert has_import_suggestion  # module_a and module_b likely > 1 import
    assert has_dependency_suggestion  # module_a imported by module_b and test_a
    assert has_doc_suggestion  # ClassA methods might be missing docstrings now


def test_export_analysis_json(nexus, project_root):
    """Test exporting analysis results to JSON."""
    workspace_analysis = nexus.analyze_workspace()
    json_output = nexus.export_analysis(workspace_analysis, format="json")

    assert json_output is not None
    assert isinstance(json_output, str)
    try:
        data = json.loads(json_output)
        assert "metrics" in data
        assert "files" in data
        assert "dependencies" in data
    except json.JSONDecodeError:
        pytest.fail("Exported JSON is not valid.")


def test_export_analysis_markdown(nexus, project_root):
    """Test exporting analysis results to Markdown."""
    workspace_analysis = nexus.analyze_workspace()
    md_output = nexus.export_analysis(workspace_analysis, format="md")

    assert md_output is not None
    assert isinstance(md_output, str)
    assert md_output.startswith("# NEXUS Analysis Report")
    # Check for presence of key sections
    assert "## Overall Metrics" in md_output
    assert "## File Analysis" in md_output
    assert "## Dependencies" in md_output
    # Check if relative paths are used in headers/output
    assert "`src/module_a.py`" in md_output
    assert "`src/module_b.py`" in md_output


# TODO: Add more specific tests for edge cases in dependency resolution
# - Different levels of relative imports (.., ...)
# - Imports within functions/classes (should be ignored by current AST walk)
# - Imports involving complex aliases
# - Files outside the main project structure (if analyze_dependencies is ever used that way)
# - Handling of SyntaxErrors during parsing more gracefully in dependency analysis
# - Test the known_external_modules heuristic more thoroughly

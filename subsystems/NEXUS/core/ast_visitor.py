#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - NEXUS AST Visitor
================================

AST-based code analysis for NEXUS.

Version: 1.0.0
"""

import ast
from dataclasses import dataclass, field
import logging
from typing import Dict, List, Optional, Union


@dataclass
class ImportInfo:
    module: str
    names: List[str] = field(default_factory=list)
    alias: Optional[str] = None
    is_from_import: bool = False
    level: int = 0  # For relative imports
    lineno: int = 0
    col_offset: int = 0
    end_lineno: Optional[int] = None
    end_col_offset: Optional[int] = None


@dataclass
class FunctionInfo:
    name: str
    args: List[str]
    decorators: List[str]
    docstring: Optional[str]
    is_async: bool = False
    start_line: int = 0
    end_line: int = 0
    complexity: int = 0


@dataclass
class ClassInfo:
    name: str
    bases: List[str]
    methods: List[FunctionInfo]
    decorators: List[str]
    docstring: Optional[str]
    start_line: int = 0
    end_line: int = 0


class CodeVisitor(ast.NodeVisitor):
    """AST visitor for analyzing Python code structure."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.imports: List[ImportInfo] = []
        self.functions: List[FunctionInfo] = []
        self.classes: List[ClassInfo] = []
        self.current_class: Optional[ClassInfo] = None
        self.cognitive_load: int = 0
        self._nesting_level: int = 0  # Track nesting for complexity boost

    def _get_docstring(self, node: ast.AST) -> Optional[str]:
        """Extract docstring from an AST node."""
        if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ) and ast.get_docstring(node):
            return ast.get_docstring(node)
        return None

    def _get_decorators(self, node: ast.AST) -> List[str]:
        """Extract decorator names from an AST node."""
        if not hasattr(node, "decorator_list"):
            return []
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    decorators.append(decorator.func.id)
            elif isinstance(decorator, ast.Attribute):
                decorators.append(f"{decorator.value.id}.{decorator.attr}")
        return decorators

    def visit_Import(self, node: ast.Import):
        """Process Import nodes."""
        for name in node.names:
            self.imports.append(
                ImportInfo(module=name.name, alias=name.asname, is_from_import=False)
            )
        # Do not call generic_visit here for imports to avoid redundant processing

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Process ImportFrom nodes."""
        # module = node.module or "" # Removed unused variable
        # Aggregate all names from a single 'from ... import ...'
        imported_names = [name.name for name in node.names]
        # Note: aliases are not currently used but might be needed in the future
        # aliases = {name.name: name.asname for name in node.names if name.asname}
        self.imports.append(
            ImportInfo(
                module=node.module,
                names=imported_names,
                level=node.level,
                lineno=node.lineno,
                col_offset=node.col_offset,
                end_lineno=node.end_lineno,
                end_col_offset=node.end_col_offset,
            )
        )
        # Do not call generic_visit here

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Process function definitions."""
        self._process_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Process async function definitions."""
        self._process_function(node, is_async=True)

    def _process_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], is_async: bool):
        """Common processing for both sync and async functions."""
        args = [arg.arg for arg in node.args.args]
        func_info = FunctionInfo(
            name=node.name,
            args=args,
            decorators=self._get_decorators(node),
            docstring=self._get_docstring(node),
            is_async=is_async,
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
        )

        if self.current_class:
            self.current_class.methods.append(func_info)
        else:
            self.functions.append(func_info)

        # --- Complexity: Increment for function definition itself and increase nesting ---
        self.cognitive_load += 1 + self._nesting_level
        self._nesting_level += 1
        self.generic_visit(node)  # Visit children
        self._nesting_level -= 1  # Decrease nesting after visiting children
        # ------------------------------------------------------------------------------

    def visit_ClassDef(self, node: ast.ClassDef):
        """Process class definitions."""
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                # Crude representation, might need refinement for complex bases
                try:
                    base_name = f"{base.value.id}.{base.attr}"
                except AttributeError:
                    base_name = "<complex_base>"
                bases.append(base_name)

        class_info = ClassInfo(
            name=node.name,
            bases=bases,
            methods=[],
            decorators=self._get_decorators(node),
            docstring=self._get_docstring(node),
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
        )

        # Set as current class for method collection
        prev_class = self.current_class
        self.current_class = class_info
        # --- Complexity: Increase nesting for visiting class body ---
        self._nesting_level += 1
        self.generic_visit(node)
        self._nesting_level -= 1
        # ---------------------------------------------------------
        self.current_class = prev_class

        self.classes.append(class_info)

    # --- Complexity Calculation Methods ---

    def visit_If(self, node: ast.If):
        """Complexity: +1 for if, +1 for each elif, +nesting penalty."""
        self.cognitive_load += 1 + self._nesting_level
        self._nesting_level += 1
        self.generic_visit(node)
        self._nesting_level -= 1

    def visit_For(self, node: ast.For):
        """Complexity: +1 for loop, +nesting penalty."""
        self.cognitive_load += 1 + self._nesting_level
        self._nesting_level += 1
        self.generic_visit(node)
        self._nesting_level -= 1

    def visit_AsyncFor(self, node: ast.AsyncFor):
        """Complexity: +1 for loop, +nesting penalty."""
        self.cognitive_load += 1 + self._nesting_level
        self._nesting_level += 1
        self.generic_visit(node)
        self._nesting_level -= 1

    def visit_While(self, node: ast.While):
        """Complexity: +1 for loop, +nesting penalty."""
        self.cognitive_load += 1 + self._nesting_level
        self._nesting_level += 1
        self.generic_visit(node)
        self._nesting_level -= 1

    def visit_Try(self, node: ast.Try):
        """Complexity: +1 for try block, +nesting penalty."""
        # Note: Except handlers are visited separately
        self.cognitive_load += 1 + self._nesting_level
        self._nesting_level += 1
        self.generic_visit(node)
        self._nesting_level -= 1

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        """Complexity: +1 for except block, +nesting penalty."""
        # This starts a new block, increasing complexity and nesting
        self.cognitive_load += 1 + self._nesting_level
        self._nesting_level += 1
        self.generic_visit(node)
        self._nesting_level -= 1

    def visit_BoolOp(self, node: ast.BoolOp):
        """Complexity: +1 for each 'and'/'or'."""
        # An op like (a and b and c) has two 'and's
        if len(node.values) > 1:
            self.cognitive_load += len(node.values) - 1
        self.generic_visit(node)

    def visit_Break(self, node: ast.Break):
        """Complexity: +1 for break."""
        self.cognitive_load += 1
        self.generic_visit(node)

    def visit_Continue(self, node: ast.Continue):
        """Complexity: +1 for continue."""
        self.cognitive_load += 1
        self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda):
        """Complexity: +1 for lambda definition, +nesting."""
        self.cognitive_load += 1 + self._nesting_level
        self._nesting_level += 1
        self.generic_visit(node)
        self._nesting_level -= 1


def analyze_code(content: str, logger: logging.Logger) -> Dict:
    """
    Analyze Python code content using AST.

    Args:
        content: The Python code to analyze
        logger: Logger instance for recording issues

    Returns:
        Dict containing analysis results
    """
    try:
        tree = ast.parse(content)
        visitor = CodeVisitor(logger)
        visitor.visit(tree)

        return {
            "imports": [
                {
                    "module": imp.module,
                    "names": imp.names,
                    "alias": imp.alias,
                    "is_from_import": imp.is_from_import,
                    "level": imp.level,
                    "lineno": imp.lineno,
                    "col_offset": imp.col_offset,
                    "end_lineno": imp.end_lineno,
                    "end_col_offset": imp.end_col_offset,
                }
                for imp in visitor.imports
            ],
            "functions": [
                {
                    "name": func.name,
                    "args": func.args,
                    "decorators": func.decorators,
                    "docstring": func.docstring,
                    "is_async": func.is_async,
                    "start_line": func.start_line,
                    "end_line": func.end_line,
                }
                for func in visitor.functions
            ],
            "classes": [
                {
                    "name": cls.name,
                    "bases": cls.bases,
                    "methods": [
                        {
                            "name": method.name,
                            "args": method.args,
                            "decorators": method.decorators,
                            "docstring": method.docstring,
                            "is_async": method.is_async,
                            "start_line": method.start_line,
                            "end_line": method.end_line,
                        }
                        for method in cls.methods
                    ],
                    "decorators": cls.decorators,
                    "docstring": cls.docstring,
                    "start_line": cls.start_line,
                    "end_line": cls.end_line,
                }
                for cls in visitor.classes
            ],
            "cognitive_load": visitor.cognitive_load,
        }

    except SyntaxError as e:
        logger.error(f"Syntax error in code: {str(e)}")
        return {
            "error": f"Syntax error: {str(e)}",
            "imports": [],
            "functions": [],
            "classes": [],
            "cognitive_load": 0,  # Return 0 complexity on syntax error
        }
    except Exception as e:
        logger.error(f"Unexpected error during AST analysis: {str(e)}", exc_info=True)
        return {
            "error": f"AST analysis failed: {str(e)}",
            "imports": [],
            "functions": [],
            "classes": [],
            "cognitive_load": 0,
        }

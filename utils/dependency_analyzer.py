# utils/dependency_analyzer.py

import ast
import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Union
from utils.project_manager import ProjectManager  # Import ProjectManager
class DependencyAnalyzer:
    def __init__(self, project_manager: ProjectManager, excluded_dirs: set = None, max_depth: int = None):
        self.project_manager = project_manager
        print(f"DependencyAnalyzer initiated")
        self.project_path = self.project_manager.get_project_folder()
        self.excluded_dirs = excluded_dirs or {
            'dist', 'build', 'node_modules', '__pycache__', '.git',
            '.svn', '.hg', '.idea', '.vscode', 'venv', 'env'
        }
        self.project_data = {}
        self.max_depth = max_depth  # For performance optimization
        self.standard_modules = self.get_standard_modules()
        self.items_missing_docstrings = []

    def get_standard_modules(self) -> set:
        """
        Get a set of standard library module names to exclude from imports.
        """
        standard_modules = set(sys.builtin_module_names)
        # Optionally, add more standard modules if needed
        return standard_modules

    def analyze_project(self):
        print(f"In analyze: {self.project_path}")
        for py_file in self.project_path.rglob("*.py"):
            print(f"File: {py_file}")
            if any(excluded_dir in py_file.parts for excluded_dir in self.excluded_dirs):
                continue  # Skip excluded directories
            relative_depth = len(py_file.relative_to(self.project_path).parts)
            if self.max_depth and relative_depth > self.max_depth:
                continue  # Skip files deeper than max_depth
            self.analyze_file(py_file)

    def analyze_file(self, file_path: Path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                
                file_content = f.read()
            tree = ast.parse(file_content, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"Failed to parse {file_path}: {e}")
            return

        try:
            visitor = DependencyVisitor(file_path, self.standard_modules, self.project_path)
            visitor.analyze_source_code(file_content)
            self.project_data[str(file_path.relative_to(self.project_path))] = visitor.file_info
            # Collect missing docstrings
            if visitor.items_missing_docstrings:
                self.collect_missing_docstrings(visitor.items_missing_docstrings, file_path)
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")


    def write_to_json(self, output_file: Path):
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.project_data, f, indent=2)
        print(f"Project structure written to {output_file.resolve()}")
    def collect_missing_docstrings(self, items, file_path):
        for item in items:
            item['file_path'] = str(file_path.relative_to(self.project_path))
            self.items_missing_docstrings.append(item)

class DependencyVisitor(ast.NodeVisitor):
    def __init__(self, file_path: Path, standard_modules: set, project_path: Path):
        self.file_path = str(file_path)
        self.standard_modules = standard_modules
        self.project_path = project_path
        self.file_info = {
            "classes": {},
            "functions": {},
            "imports": [],
        }
        self.current_class = None
        self.current_function = None
        self.scope_stack = []
        self.items_missing_docstrings = []

    def visit_Import(self, node):
        for alias in node.names:
            module_name = alias.name.split('.')[0]
            if module_name not in self.standard_modules:
                self.file_info["imports"].append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module if node.module else ""
        module_name = module.split('.')[0]
        if module_name not in self.standard_modules:
            imported_names = [alias.name for alias in node.names]
            for name in imported_names:
                self.file_info["imports"].append(f"{module}.{name}")
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        class_info = {
            "name": node.name,
            "type": "class",
            "start_line": node.lineno,
            "end_line": getattr(node, 'end_lineno', None),
            "docstring": ast.get_docstring(node),
            "methods": {},
            "bases": [self._get_name(base) for base in node.bases],
        }
        if not class_info["docstring"]:
            self.items_missing_docstrings.append({
                "type": "class",
                "name": node.name,
                "start_line": node.lineno,
                "end_line": getattr(node, 'end_lineno', None),
                "code": ast.get_source_segment(self.source_code, node)
            })
        self.file_info["classes"][node.name] = class_info
        self.current_class = node.name
        self.scope_stack.append(node.name)
        self.generic_visit(node)
        self.scope_stack.pop()
        self.current_class = None

    def visit_FunctionDef(self, node):
        # Decide the level of detail based on function size
        function_size = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
        if function_size < 10:
            variable_limit = 2
        elif function_size < 50:
            variable_limit = 5
        else:
            variable_limit = 10

        function_info = {
            "name": node.name,
            "type": "method" if self.current_class else "function",
            "start_line": node.lineno,
            "end_line": getattr(node, 'end_lineno', None),
            "docstring": ast.get_docstring(node),
            "calls": [],
            "variables": {"used": [], "assigned": []},
            "decorators": [self._get_full_name(dec) for dec in node.decorator_list],
            "returns": self._get_annotation(node.returns),
            "parameters": self._get_parameters(node.args),
        }
        if not function_info["docstring"]:
            self.items_missing_docstrings.append({
                "type": "function",
                "name": node.name,
                "start_line": node.lineno,
                "end_line": getattr(node, 'end_lineno', None),
                "code": ast.get_source_segment(self.source_code, node)
            })
        if self.current_class:
            self.file_info["classes"][self.current_class]["methods"][node.name] = function_info
        else:
            self.file_info["functions"][node.name] = function_info

        self.current_function = function_info
        self.scope_stack.append(node.name)
        self.variable_limit = variable_limit
        self.generic_visit(node)
        self.scope_stack.pop()
        self.current_function = None
    def analyze_source_code(self, source_code: str):
        self.source_code = source_code
        tree = ast.parse(source_code)
        self.visit(tree)
    def visit_Call(self, node):
        func_name = self._get_full_name(node.func)
        if self.current_function:
            if func_name.startswith('builtins.'):
                # Exclude built-in functions
                pass
            else:
                self.current_function["calls"].append(func_name)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if self.current_function and node.id not in self.current_function["variables"]["used"]:
                if not self._is_standard_name(node.id):
                    if len(self.current_function["variables"]["used"]) < self.variable_limit:
                        self.current_function["variables"]["used"].append(node.id)
        elif isinstance(node.ctx, ast.Store):
            if self.current_function and node.id not in self.current_function["variables"]["assigned"]:
                if not self._is_standard_name(node.id):
                    if len(self.current_function["variables"]["assigned"]) < self.variable_limit:
                        self.current_function["variables"]["assigned"].append(node.id)
        self.generic_visit(node)

    def _is_standard_name(self, name: str) -> bool:
        """
        Determine if a name is from the standard library or built-in types.
        """
        standard_types = {'int', 'str', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 'None'}
        return name in standard_types or name in self.standard_modules

    def _get_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_full_name(node)
        else:
            return ""

    def _get_full_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value_name = self._get_full_name(node.value)
            return f"{value_name}.{node.attr}" if value_name else node.attr
        elif isinstance(node, ast.Call):
            return self._get_full_name(node.func)
        elif isinstance(node, ast.Subscript):
            return self._get_full_name(node.value)
        else:
            return ""

    def _get_annotation(self, node):
        if node is None:
            return None
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            return self._get_full_name(node)
        else:
            return ast.dump(node)

    def _get_parameters(self, args):
        parameters = []
        for arg in args.args:
            param = {
                "name": arg.arg,
                "annotation": self._get_annotation(arg.annotation)
            }
            parameters.append(param)
        return parameters

    def generic_visit(self, node):
        super().generic_visit(node)

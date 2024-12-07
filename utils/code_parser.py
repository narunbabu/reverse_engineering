# utils/code_parser.py

import ast
from pathlib import Path
from typing import List, Dict, Union

# utils/code_parser.py

import ast
from pathlib import Path
from typing import List, Dict, Union


class CodeParser:
    def __init__(self, project_path: Path, project_type: str = None):
        self.project_path = project_path
        print(f"[DEBUG] Initialized CodeParser with project_path: {self.project_path.resolve()}")
        self.project_type = project_type
        self.excluded_dirs = {
            'dist', 'build', 'node_modules', '__pycache__', '.git', 
            '.svn', '.hg', '.idea', '.vscode', 'venv', 'env'
        }

    def extract_symbols(self) -> Dict[str, Union[Dict, List]]:
        if not self.project_type:
            self.project_type = self.detect_project_type()

        print(f"[DEBUG] Detected project_type: {self.project_type}")

        if self.project_type == 'python':
            return self._parse_python_project()
        elif self.project_type == 'javascript':
            return self._parse_javascript_project()
        # Add more project types as needed
        else:
            print(f"Unsupported or unknown project type: {self.project_type}")
            return {}

    def detect_project_type(self) -> str:
        # Attempt to detect the project type based on files in the root directory
        try:
            project_files = [f.name for f in self.project_path.iterdir() if f.is_file()]
            print(f"[DEBUG] Project root files: {project_files}")
        except Exception as e:
            print(f"[ERROR] Failed to list files in {self.project_path}: {e}")
            return 'unknown'

        if 'setup.py' in project_files or 'requirements.txt' in project_files:
            return 'python'
        elif 'package.json' in project_files:
            return 'javascript'
        elif 'composer.json' in project_files:
            return 'php'
        else:
            # Enhanced detection: Check for presence of .py files anywhere in the project
            python_files = list(self.project_path.rglob("*.py"))
            print(f"[DEBUG] Found {len(python_files)} .py files in the project.")
            if python_files:
                return 'python'
            # Similarly, you can add checks for other project types
            return 'unknown'

    def _parse_python_project(self) -> Dict[str, Dict]:
        code_symbols = {}
        for py_file in self.project_path.rglob("*.py"):
            print(f"[DEBUG] Processing Python file: {py_file}")
            if any(excluded_dir in py_file.parts for excluded_dir in self.excluded_dirs):
                print(f"[DEBUG] Skipping excluded directory: {py_file}")
                continue  # Skip excluded directories
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    file_content = f.read()
                tree = ast.parse(file_content)
                symbols = self._extract_python_symbols_from_tree(tree)
                relative_path = str(py_file.relative_to(self.project_path))
                code_symbols[relative_path] = symbols
                print(f"[DEBUG] Extracted symbols from {relative_path}: {symbols}")
            except Exception as e:
                print(f"Failed to parse {py_file}: {e}")
        return code_symbols

    def _extract_python_symbols_from_tree(self, tree) -> Dict[str, Union[Dict[str, List[str]], List[str]]]:
        symbols = {
            "classes": {},  # Dict[class_name, List[function_names]]
            "functions": []  # List of top-level function names
        }
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                methods = [
                    n.name for n in node.body 
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                symbols["classes"][class_name] = methods
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbols["functions"].append(node.name)
        return symbols

    def _parse_javascript_project(self) -> dict:
        code_symbols = {}
        for js_file in self.project_path.rglob("*.js"):
            if any(excluded_dir in js_file.parts for excluded_dir in self.excluded_dirs):
                continue  # Skip excluded directories
            # Implement JavaScript parsing logic here
            # For simplicity, we'll collect file names
            print(f"Found JavaScript file {js_file}")
            code_symbols[str(js_file.relative_to(self.project_path))] = ["JavaScript file parsed"]
        return code_symbols

    # Implement other project types as needed

    def write_symbols_to_file(self, symbols: Dict[str, Dict], output_file: Path):
        with open(output_file, "w", encoding="utf-8") as f:
            for file_path, content in symbols.items():
                f.write(f"File: {file_path}\n")
                classes = content.get("classes", {})
                functions = content.get("functions", [])
                
                if classes:
                    for class_name, methods in classes.items():
                        f.write(f"  Class: {class_name}\n")
                        if methods:
                            f.write(f"    Functions:\n")
                            for method in methods:
                                f.write(f"      {method}\n")
                        else:
                            f.write(f"    Functions: None\n")
                if functions:
                    f.write(f"  Functions:\n")
                    for func in functions:
                        f.write(f"    {func}\n")
                f.write("\n")  # Add a newline for separation between files
        print(f"[DEBUG] Symbols successfully written to {output_file.resolve()}")

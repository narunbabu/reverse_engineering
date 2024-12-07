from pathlib import Path
import shutil
def create_sample_project(project_path: Path):
    """
    Creates a sample Python project structure for testing.
    """
    print(f"[DEBUG] Creating sample project at {project_path.resolve()}")

    # Create directories
    (project_path / "module").mkdir(parents=True, exist_ok=True)
    (project_path / "utils").mkdir(parents=True, exist_ok=True)

    # Create sample Python files
    main_py = project_path / "main.py"
    module_py = project_path / "module" / "module.py"
    utils_py = project_path / "utils" / "utils.py"

    main_py_content = """
import module.module as mod
from utils import utils

def main_function():
    result = mod.module_function()
    utils.util_function()
    return result

class MainClass:
    \"\"\"This is the MainClass documentation.\"\"\"
    def method_one(self):
        self.data = mod.module_function()
        return self.data

    def method_two(self):
        utils.util_function()
    """

    module_py_content = """
def module_function():
    print("Module function called")
    return 42

class ModuleClass:
    def module_method(self):
        print("Module method called")
    """

    utils_py_content = """
def util_function():
    print("Utility function called")
    """

    main_py.write_text(main_py_content.strip(), encoding="utf-8")
    module_py.write_text(module_py_content.strip(), encoding="utf-8")
    utils_py.write_text(utils_py_content.strip(), encoding="utf-8")

    print(f"[DEBUG] Created main.py at {main_py.resolve()}")
    print(f"[DEBUG] Created module.py at {module_py.resolve()}")
    print(f"[DEBUG] Created utils.py at {utils_py.resolve()}")
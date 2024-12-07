# make_project_structure.py

import asyncio
import json
from pathlib import Path
from utils.project_manager import ProjectManager
from utils.dependency_analyzer import DependencyAnalyzer
from utils.diagram_generator import DiagramGenerator
from utils.document_generator import DocumentGenerator
from utils.llm_client import LLMClient
from utils.config import PROJECT_PATH
from configs.llm_config import LLMConfig

async def main():
    project_path = PROJECT_PATH
    ignored_dirs = ['tests', '__pycache__', 'migrations', 'dist','build','.ipynb_checkpoints','assets','unused' ]  # Example directories to ignore
    ignored_files = ['setup.py', 'manage.py']             # Example files to ignore
    ignored_path_substrings = ['legacy', 'third_party','__pycache__']   # Example path substrings to ignore

    project_manager = ProjectManager(
            project_path=project_path,
            ignored_dirs=ignored_dirs,
            ignored_files=ignored_files,
            ignored_path_substrings=ignored_path_substrings
        )

    project_manager.initialize_logger()  # Initialize logger before workspace setup

    project_manager.setup_workspace(clean_existing=False)  # Now it's safe to use self.logger in setup_workspace

    print(f"[DEBUG] Sample project path: {PROJECT_PATH.resolve()}")

    # Initialize the DependencyAnalyzer
    analyzer = DependencyAnalyzer(project_manager=project_manager)

    # Analyze the project
    analyzer.analyze_project()

    # Write the project data to JSON
    dependency_output = project_manager.get_analysis_folder() / "project_structure.json"
    analyzer.write_to_json(dependency_output)

    # Load the project structure JSON
    with open(dependency_output, "r", encoding="utf-8") as f:
        project_data = json.load(f)
if __name__ == "__main__":
    asyncio.run(main())
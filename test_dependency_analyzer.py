# test_dependency_analyzer.py

import shutil
from pathlib import Path
from utils.project_manager import ProjectManager
from utils.dependency_analyzer import DependencyAnalyzer
from utils.llm_client import LLMClient
from utils.docstring_generator import DocstringGenerator
from configs.llm_config import LLMConfig
import asyncio
from utils.create_sample_project import create_sample_project
from utils.config import PROJECT_PATH  # Import PROJECT_PATH from config

async  def main():
    # Define the path for the sample project
    # sample_project_path = Path("./dependency_project")
    # project_path = Path("../../LDSTheory/MaterialModel3")
    # project_path = Path("../MetaGPTGit\metagpt")

    project_manager = ProjectManager(PROJECT_PATH)
    project_manager.setup_workspace()
    print(f"[DEBUG] Sample project path: {PROJECT_PATH.resolve()}")


    # # Clean up if the sample project already exists
    # if sample_project_path.exists():
    #     print(f"[DEBUG] Removing existing sample project at {sample_project_path.resolve()}")
    #     shutil.rmtree(sample_project_path)

    # # Create the sample project
    # create_sample_project(sample_project_path)
    # print(f"Sample project created at {sample_project_path.resolve()}")

    # Initialize the DependencyAnalyzer
    analyzer = DependencyAnalyzer(project_manager=project_manager)

    # Analyze the project
    analyzer.analyze_project()

    # Write the project data to JSON
    dependency_output = project_manager.get_analysis_folder() / "project_structure.json"
    analyzer.write_to_json(dependency_output)

    # # Initialize the LLM client and generate docstrings
    # llm_config = LLMConfig()
    # async with LLMClient(llm_config) as llm_client:
    #     docstring_generator = DocstringGenerator(llm_client)
    #     generated_docstrings = await docstring_generator.generate_docstrings(analyzer.items_missing_docstrings)

    # # Update the project data with generated docstrings
    # for item in generated_docstrings:
    #     file_path = item['file_path']
    #     name = item['name']
    #     if item['type'] == 'class':
    #         analyzer.project_data[file_path]['classes'][name]['docstring'] = item.get('generated_docstring', '')
    #     elif item['type'] == 'function':
    #         if analyzer.project_data[file_path]['functions'].get(name):
    #             analyzer.project_data[file_path]['functions'][name]['docstring'] = item.get('generated_docstring', '')
    #         else:
    #             # If function is a method inside a class
    #             for class_info in analyzer.project_data[file_path]['classes'].values():
    #                 if class_info['methods'].get(name):
    #                     class_info['methods'][name]['docstring'] = item.get('generated_docstring', '')

    # # Write the updated project data to JSON
    # updated_output = project_manager.get_project_folder() / "project_structure_with_docstrings.json"
    # analyzer.write_to_json(updated_output)

    # print(f"Dependency analysis and docstring generation completed. See {updated_output.resolve()}.")

if __name__ == "__main__":
    asyncio.run(main())
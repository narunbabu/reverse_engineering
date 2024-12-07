# test_diagram_generator.py

import json
import asyncio
from pathlib import Path
from utils.project_manager import ProjectManager
from utils.diagram_generator import DiagramGenerator
from utils.config import PROJECT_PATH  # Import PROJECT_PATH from config

async def main():
    # Initialize the ProjectManager with PROJECT_PATH from .env
    project_manager = ProjectManager(PROJECT_PATH)
    project_manager.setup_workspace()
    print(f"[DEBUG] Sample project path: {PROJECT_PATH.resolve()}")

    # Initialize the DependencyAnalyzer and analyze the project
    from utils.dependency_analyzer import DependencyAnalyzer
    analyzer = DependencyAnalyzer(project_manager=project_manager)
    analyzer.analyze_project()

    # Write the project data to JSON
    dependency_output = project_manager.get_analysis_folder() / "project_structure.json"
    analyzer.write_to_json(dependency_output)

    # Load the project structure JSON
    with open(dependency_output, "r", encoding="utf-8") as f:
        project_data = json.load(f)

    # Initialize the DiagramGenerator
    generator = DiagramGenerator(project_data, project_manager)

    # Generate the class diagram PlantUML script
    output_file = project_manager.get_analysis_folder() / "class_diagram.puml"
    generator.generate_class_diagram(output_file)

    # Instructions to render the diagram
    print("To render the diagram, install PlantUML and run:")
    print(f"plantuml {output_file.resolve()}")

if __name__ == "__main__":
    asyncio.run(main())

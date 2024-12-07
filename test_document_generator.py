# test_document_generator.py

import json
import asyncio
from pathlib import Path
from utils.project_manager import ProjectManager
from utils.document_generator import DocumentGenerator
from utils.llm_client import LLMClient
from utils.config import PROJECT_PATH  # Import PROJECT_PATH from config
from configs.llm_config import LLMConfig

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

    # Initialize the LLM client
    llm_config = LLMConfig()
    async with LLMClient(llm_config) as llm_client:
        # Initialize the DocumentGenerator
        generator = DocumentGenerator(llm_client, project_manager)

        # Generate the sequence diagram
        sequence_diagram = await generator.generate_sequence_diagram(project_data)

        # Save the sequence diagram
        if sequence_diagram:
            diagram_file = project_manager.get_analysis_folder() / 'sequence_diagram.puml'
            with open(diagram_file, "w", encoding="utf-8") as f:
                f.write(sequence_diagram)
            print(f"Sequence diagram PlantUML script written to {diagram_file.resolve()}")
            print("To render the diagram, install PlantUML and run:")
            print(f"plantuml {diagram_file}")
        else:
            print("Failed to generate sequence diagram.")

if __name__ == "__main__":
    asyncio.run(main())

# run_all_generators.py

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
    # Initialize the ProjectManager with PROJECT_PATH from .env
    project_manager = ProjectManager(PROJECT_PATH)
    project_manager.setup_workspace()
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

    # Initialize the LLM client
    llm_config = LLMConfig()
    async with LLMClient(llm_config) as llm_client:
        # Initialize the DocumentGenerator
        document_generator = DocumentGenerator(llm_client, project_manager)

        # Generate docstrings (if implemented)
        # docstring_generator = DocstringGenerator(llm_client)
        # generated_docstrings = await docstring_generator.generate_docstrings(analyzer.project_data.get("missing_docstrings", []))
        # Update project_data with generated docstrings as needed

        # Generate the class diagram
        diagram_generator = DiagramGenerator(project_data, project_manager)
        class_diagram_output = project_manager.get_analysis_folder() / "class_diagram.puml"
        diagram_generator.generate_class_diagram(class_diagram_output)
        print("Class diagram generated.")

        # Generate the sequence diagram
        sequence_diagram = await document_generator.generate_sequence_diagram(project_data)
        if sequence_diagram:
            sequence_diagram_file = project_manager.get_analysis_folder() / 'sequence_diagram.puml'
            with open(sequence_diagram_file, "w", encoding="utf-8") as f:
                f.write(sequence_diagram)
            print(f"Sequence diagram PlantUML script written to {sequence_diagram_file.resolve()}")
            print("To render the diagram, install PlantUML and run:")
            print(f"plantuml {sequence_diagram_file}")
        else:
            print("Failed to generate sequence diagram.")

if __name__ == "__main__":
    asyncio.run(main())

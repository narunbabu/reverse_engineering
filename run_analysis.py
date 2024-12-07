# run_analysis.py

import asyncio
from pathlib import Path
from utils.project_manager import ProjectManager
from utils.dependency_analyzer import DependencyAnalyzer
from utils.diagram_generator import DiagramGenerator
from utils.document_generator import DocumentGenerator
from utils.llm_client import LLMClient
from utils.docstring_generator import DocstringGenerator  # If implemented
from utils.create_sample_project import 
from configs.llm_config import LLMConfig

async def main():
    # Define the path for the project to analyze
    project_path = Path("./sample_project")
    
    # Initialize the ProjectManager
    project_manager = ProjectManager(project_path)
    project_manager.setup_workspace()
    
    # Initialize the DependencyAnalyzer
    dependency_analyzer = DependencyAnalyzer(project_manager=project_manager)
    dependency_analyzer.analyze_project()
    
    # Write the dependency analysis to JSON
    dependency_output = project_manager.get_project_folder() / "project_structure.json"
    dependency_analyzer.write_to_json(dependency_output)
    
    # Initialize the LLM client
    llm_config = LLMConfig()
    async with LLMClient(llm_config) as llm_client:
        # Initialize the DocumentGenerator
        document_generator = DocumentGenerator(llm_client, project_manager)
        
        # Generate docstrings (if implemented)
        # docstring_generator = DocstringGenerator(llm_client)
        # generated_docstrings = await docstring_generator.generate_docstrings(dependency_analyzer.items_missing_docstrings)
        # Update project_data with generated docstrings as needed
        
        # Generate diagrams
        with open(dependency_output, "r", encoding="utf-8") as f:
            project_data = json.load(f)
        diagram_generator = DiagramGenerator(project_data, project_manager)
        diagram_output = project_manager.get_project_folder() / 'class_diagram.puml'
        diagram_generator.generate_class_diagram(diagram_output)
        
        # Generate additional documents (e.g., sequence diagrams)
        sequence_diagram = await document_generator.generate_sequence_diagram(project_data)
        if sequence_diagram:
            sequence_diagram_file = project_manager.get_project_folder() / 'sequence_diagram.puml'
            with open(sequence_diagram_file, "w", encoding="utf-8") as f:
                f.write(sequence_diagram)
            print(f"Sequence diagram PlantUML script written to {sequence_diagram_file.resolve()}")
            print("To render the diagram, install PlantUML and run:")
            print(f"plantuml {sequence_diagram_file}")
        else:
            print("Failed to generate sequence diagram.")

if __name__ == "__main__":
    asyncio.run(main())

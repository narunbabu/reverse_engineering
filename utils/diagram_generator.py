# utils/diagram_generator.py

from pathlib import Path
from typing import Dict
from utils.project_manager import ProjectManager
import json

class DiagramGenerator:
    def __init__(self, project_data: Dict, project_manager: ProjectManager):
        self.project_data = project_data
        self.project_manager = project_manager
        self.project_folder = self.project_manager.get_project_folder()
        self.analysis_folder = self.project_manager.get_analysis_folder()

    def generate_class_diagram(self, output_file: Path):
        lines = ["@startuml", "skinparam classAttributeIconSize 0"]
        class_definitions = {}

        # Collect class definitions
        for file_info in self.project_data.values():
            for class_name, class_info in file_info.get('classes', {}).items():
                class_definition = [f"class {class_name} {{"]
                # Add attributes and methods
                methods = class_info.get('methods', {})
                for method_name in methods.keys():
                    class_definition.append(f"    + {method_name}()")
                class_definition.append("}")
                class_definitions[class_name] = "\n".join(class_definition)

        # Add classes to lines
        lines.extend(class_definitions.values())

        # Handle relationships (inheritance)
        for file_info in self.project_data.values():
            for class_name, class_info in file_info.get('classes', {}).items():
                bases = class_info.get('bases', [])
                for base in bases:
                    lines.append(f"{base} <|-- {class_name}")

        lines.append("@enduml")

        # Write to output file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"Class diagram PlantUML script written to {output_file.resolve()}")


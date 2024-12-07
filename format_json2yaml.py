import json
import yaml  # Install with: pip install PyYAML
from pathlib import Path
from utils.project_manager import ProjectManager
from utils.config import PROJECT_PATH  # Import PROJECT_PATH from config

def json_to_yaml(json_data):
    yaml_data = yaml.dump(json_data, default_flow_style=False)
    return yaml_data

# # Example usage:
# if __name__ == "__main__":
#     with open('project_structure.json', 'r', encoding='utf-8') as f:
#         json_data = json.load(f)
#     yaml_output = json_to_yaml(json_data)
#     print(yaml_output)
if __name__ == "__main__":
    try:
        # Initialize ProjectManager
        project_manager = ProjectManager(PROJECT_PATH)
        project_manager.setup_workspace()

        # Define paths
        analysis_folder = project_manager.get_analysis_folder()
        project_structure_path = analysis_folder / "project_structure.json"
        output_file = analysis_folder / "project_structure.yaml"

        # Load JSON data
        with open(project_structure_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        print("Loaded JSON data successfully.")

        yaml_output = json_to_yaml(json_data)
        # print(yaml_output)

        # Write output to the delimited file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(yaml_output)
        print(f"Project structure written to {output_file.resolve()}")

    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure the project structure JSON file exists.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

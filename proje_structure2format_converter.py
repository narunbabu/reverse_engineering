# # format_converter.py

import json
from pathlib import Path
from utils.project_manager import ProjectManager
from utils.config import PROJECT_PATH

def json_to_custom_delimited(json_data):
    output_lines = []
    # Add definitions at the beginning
    definitions = "# Function Keys : The lines with "|" are function attributes \n# name | start_line | end_line | docstring | calls | variables_used | variables_assigned | decorators | returns | parameters"
    output_lines.append(definitions)
    for file_path, file_content in json_data.items():
        output_lines.append(f"File: {file_path}")
        print(f"Processing File: {file_path}")

        # Process functions
        functions = file_content.get('functions', {})
        for func_name, func_info in functions.items():
            print(f"    Processing Function: {func_name}")
            line = []
            line.append(func_name)
            line.append(str(func_info.get('start_line', '')))
            line.append(str(func_info.get('end_line', '')))

            # Safely handle docstring
            docstring = func_info.get('docstring') or ''
            if not isinstance(docstring, str):
                docstring = ''
            docstring = docstring.replace('"', '\\"')  # Escape double quotes
            line.append(f'"{docstring}"')

            # Handle other fields with defaults
            calls = ', '.join(func_info.get('calls', []))
            line.append(calls)

            variables = func_info.get('variables', {})
            variables_used = ', '.join(variables.get('used', []))
            line.append(variables_used)

            variables_assigned = ', '.join(variables.get('assigned', []))
            line.append(variables_assigned)

            decorators = ', '.join(func_info.get('decorators', []))
            line.append(decorators)

            returns = func_info.get('returns') or ''
            if not isinstance(returns, str):
                returns = str(returns)
            line.append(returns)

            parameters = ', '.join([
                f"{param.get('name', '')}: {param.get('annotation', '')}" 
                for param in func_info.get('parameters', [])
            ])
            line.append(parameters)

            output_lines.append(' | '.join(line))

        # Process classes
        classes = file_content.get('classes', {})
        for class_name, class_info in classes.items():
            output_lines.append(f"Class: {class_name}")
            print(f"    Processing Class: {class_name}")

            # Process methods
            methods = class_info.get('methods', {})
            for method_name, method_info in methods.items():
                print(f"        Processing Method: {method_name}")
                line = []
                line.append(method_name)
                line.append(str(method_info.get('start_line', '')))
                line.append(str(method_info.get('end_line', '')))

                # Safely handle docstring
                docstring = method_info.get('docstring') or ''
                if not isinstance(docstring, str):
                    docstring = ''
                docstring = docstring.replace('"', '\\"')  # Escape double quotes
                line.append(f'"{docstring}"')

                # Handle other fields with defaults
                calls = ', '.join(method_info.get('calls', []))
                line.append(calls)

                variables = method_info.get('variables', {})
                variables_used = ', '.join(variables.get('used', []))
                line.append(variables_used)

                variables_assigned = ', '.join(variables.get('assigned', []))
                line.append(variables_assigned)

                decorators = ', '.join(method_info.get('decorators', []))
                line.append(decorators)

                returns = method_info.get('returns') or ''
                if not isinstance(returns, str):
                    returns = str(returns)
                line.append(returns)

                parameters = ', '.join([
                    f"{param.get('name', '')}: {param.get('annotation', '')}" 
                    for param in method_info.get('parameters', [])
                ])
                line.append(parameters)

                output_lines.append(' | '.join(line))

    return '\n'.join(output_lines)

def json_to_positional_data(json_data) : 
    # Define the keys once
    key_definitions = "# Function Keys : \n# name | type | start_line | end_line | docstring | calls | variables_used | variables_assigned | decorators | returns | parameters\n"
    output_lines = [key_definitions]
    for file_path, file_content in json_data.items() : 
        output_lines.append(f"File :  {file_path}")

        # Process functions
        functions = file_content.get('functions', {})
        for func_name, func_info in functions.items() : 
            line = []
            line.append(func_name)
            line.append(func_info.get('type', ''))
            line.append(str(func_info.get('start_line', '')))
            line.append(str(func_info.get('end_line', '')))

            # Safely handle docstring
            docstring = func_info.get('docstring') or ''
            if not isinstance(docstring, str) : 
                docstring = ''
            docstring = docstring.replace('"', '\\"')
            line.append(f'"{docstring}"')

            # Handle other fields with defaults
            calls = ', '.join(func_info.get('calls', []))
            line.append(calls)

            variables = func_info.get('variables', {})
            variables_used = ', '.join(variables.get('used', []))
            line.append(variables_used)

            variables_assigned = ', '.join(variables.get('assigned', []))
            line.append(variables_assigned)

            decorators = ', '.join(func_info.get('decorators', []))
            line.append(decorators)

            returns = func_info.get('returns') or ''
            if not isinstance(returns, str) : 
                returns = str(returns)
            line.append(returns)

            parameters = ', '.join([
                f"{param.get('name', '')} : {param.get('annotation', '')}"
                for param in func_info.get('parameters', [])
            ])
            line.append(parameters)

            output_lines.append(' | '.join(line))

        # Process classes
        classes = file_content.get('classes', {})
        for class_name, class_info in classes.items() : 
            output_lines.append(f"Class :  {class_name}")

            # Process methods
            methods = class_info.get('methods', {})
            for method_name, method_info in methods.items() : 
                line = []
                line.append(method_name)
                line.append(method_info.get('type', ''))
                line.append(str(method_info.get('start_line', '')))
                line.append(str(method_info.get('end_line', '')))

                # Safely handle docstring
                docstring = method_info.get('docstring') or ''
                if not isinstance(docstring, str) : 
                    docstring = ''
                docstring = docstring.replace('"', '\\"')
                line.append(f'"{docstring}"')

                # Handle other fields with defaults
                calls = ', '.join(method_info.get('calls', []))
                line.append(calls)

                variables = method_info.get('variables', {})
                variables_used = ', '.join(variables.get('used', []))
                line.append(variables_used)

                variables_assigned = ', '.join(variables.get('assigned', []))
                line.append(variables_assigned)

                decorators = ', '.join(method_info.get('decorators', []))
                line.append(decorators)

                returns = method_info.get('returns') or ''
                if not isinstance(returns, str) : 
                    returns = str(returns)
                line.append(returns)

                parameters = ', '.join([
                    f"{param.get('name', '')} : {param.get('annotation', '')}"
                    for param in method_info.get('parameters', [])
                ])
                line.append(parameters)

                output_lines.append(' | '.join(line))

    return '\n'.join(output_lines)

def json_to_abbreviated_keys(json_data) : 
    output_lines = []
    # Abbreviated Keys : 
    key_definitions = "# Abbreviated Keys : \n# fn : function_name | sl : start_line | el : end_line | ds : docstring | c : calls | vu : variables_used | va : variables_assigned | d : decorators | r : returns | p : parameters\n"
    output_lines.append(key_definitions)
    for file_path, file_content in json_data.items() : 
        output_lines.append(f"File :  {file_path}")

        # Process functions
        functions = file_content.get('functions', {})
        for func_name, func_info in functions.items() : 
            line = []
            line.append(f"fn : {func_name}")
            line.append(f"sl : {str(func_info.get('start_line', ''))}")
            line.append(f"el : {str(func_info.get('end_line', ''))}")

            # Safely handle docstring
            docstring = func_info.get('docstring') or ''
            if not isinstance(docstring, str) : 
                docstring = ''
            docstring = docstring.replace('"', '\\"')
            line.append(f'ds : "{docstring}"')

            # Handle other fields with defaults
            calls = ', '.join(func_info.get('calls', []))
            line.append(f"c : {calls}")

            variables = func_info.get('variables', {})
            variables_used = ', '.join(variables.get('used', []))
            line.append(f"vu : {variables_used}")

            variables_assigned = ', '.join(variables.get('assigned', []))
            line.append(f"va : {variables_assigned}")

            decorators = ', '.join(func_info.get('decorators', []))
            line.append(f"d : {decorators}")

            returns = func_info.get('returns') or ''
            if not isinstance(returns, str) : 
                returns = str(returns)
            line.append(f"r : {returns}")

            parameters = ', '.join([
                f"{param.get('name', '')} : {param.get('annotation', '')}"
                for param in func_info.get('parameters', [])
            ])
            line.append(f"p : {parameters}")

            output_lines.append(' | '.join(line))

        # Process classes
        classes = file_content.get('classes', {})
        for class_name, class_info in classes.items() : 
            output_lines.append(f"Class :  {class_name}")

            # Process methods
            methods = class_info.get('methods', {})
            for method_name, method_info in methods.items() : 
                line = []
                line.append(f"fn : {method_name}")
                line.append(f"sl : {str(method_info.get('start_line', ''))}")
                line.append(f"el : {str(method_info.get('end_line', ''))}")

                # Safely handle docstring
                docstring = method_info.get('docstring') or ''
                if not isinstance(docstring, str) : 
                    docstring = ''
                docstring = docstring.replace('"', '\\"')
                line.append(f'ds : "{docstring}"')

                # Handle other fields with defaults
                calls = ', '.join(method_info.get('calls', []))
                line.append(f"c : {calls}")

                variables = method_info.get('variables', {})
                variables_used = ', '.join(variables.get('used', []))
                line.append(f"vu : {variables_used}")

                variables_assigned = ', '.join(variables.get('assigned', []))
                line.append(f"va : {variables_assigned}")

                decorators = ', '.join(method_info.get('decorators', []))
                line.append(f"d : {decorators}")

                returns = method_info.get('returns') or ''
                if not isinstance(returns, str) : 
                    returns = str(returns)
                line.append(f"r : {returns}")

                parameters = ', '.join([
                    f"{param.get('name', '')} : {param.get('annotation', '')}"
                    for param in method_info.get('parameters', [])
                ])
                line.append(f"p : {parameters}")

                output_lines.append(' | '.join(line))

    return '\n'.join(output_lines)

def json_to_indented_tree(json_data) : 
    output_lines = []
    for file_path, file_content in json_data.items() : 
        output_lines.append(f"{file_path}")
        # Process functions
        functions = file_content.get('functions', {})
        if functions : 
            output_lines.append("  Functions : ")
            for func_name, func_info in functions.items() : 
                start_line = func_info.get('start_line', '')
                end_line = func_info.get('end_line', '')
                docstring = func_info.get('docstring', 'None')
                if not isinstance(docstring, str) : 
                    docstring = 'None'
                docstring = docstring.replace('"', '\\"')
                output_lines.append(f"    {func_name} ({start_line}-{end_line}) :  \"{docstring}\"")
                # Optionally include more details

        # Process classes
        classes = file_content.get('classes', {})
        if classes : 
            output_lines.append("  Classes : ")
            for class_name, class_info in classes.items() : 
                output_lines.append(f"    {class_name}")
                methods = class_info.get('methods', {})
                if methods : 
                    output_lines.append("      Methods : ")
                    for method_name, method_info in methods.items() : 
                        start_line = method_info.get('start_line', '')
                        end_line = method_info.get('end_line', '')
                        docstring = method_info.get('docstring', 'None')
                        if not isinstance(docstring, str) : 
                            docstring = 'None'
                        docstring = docstring.replace('"', '\\"')
                        output_lines.append(f"        {method_name} ({start_line}-{end_line}) :  \"{docstring}\"")
                        # Optionally include more details

    return '\n'.join(output_lines)

def json_to_yaml(json_data) : 
    import yaml  # Make sure PyYAML is installed
    yaml_data = yaml.dump(json_data, default_flow_style=False)
    return yaml_data

# Example usage : 
if __name__ == "__main__" : 
    try : 
        # Initialize ProjectManager
        project_manager = ProjectManager(PROJECT_PATH)
        project_manager.setup_workspace()

        # Define paths
        analysis_folder = project_manager.get_analysis_folder()
        project_structure_path = analysis_folder / "project_structure.json"

        # Load JSON data
        with open(project_structure_path, 'r', encoding='utf-8') as f : 
            json_data = json.load(f)
        print("Loaded JSON data successfully.")

        # Decide which formats to produce
        formats_to_produce = {
            'custom_delimited' :  True,
            'positional_data' :  True,
            'abbreviated_keys' :  True,
            'indented_tree' :  True,
            'yaml' :  True
        }

        # Generate and write outputs
        if formats_to_produce.get('custom_delimited') : 
            output = json_to_custom_delimited(json_data)
            output_file = analysis_folder / "project_structure.delim"
            with open(output_file, "w", encoding="utf-8") as f : 
                f.write(output)
            print(f"Custom delimited format written to {output_file.resolve()}")

        if formats_to_produce.get('positional_data') : 
            output = json_to_positional_data(json_data)
            output_file = analysis_folder / "project_structure.positional"
            with open(output_file, "w", encoding="utf-8") as f : 
                f.write(output)
            print(f"Positional data format written to {output_file.resolve()}")

        if formats_to_produce.get('abbreviated_keys') : 
            output = json_to_abbreviated_keys(json_data)
            output_file = analysis_folder / "project_structure.abbrev"
            with open(output_file, "w", encoding="utf-8") as f : 
                f.write(output)
            print(f"Abbreviated keys format written to {output_file.resolve()}")

        if formats_to_produce.get('indented_tree') : 
            output = json_to_indented_tree(json_data)
            output_file = analysis_folder / "project_structure.tree"
            with open(output_file, "w", encoding="utf-8") as f : 
                f.write(output)
            print(f"Indented tree format written to {output_file.resolve()}")

        if formats_to_produce.get('yaml') : 
            output = json_to_yaml(json_data)
            output_file = analysis_folder / "project_structure.yaml"
            with open(output_file, "w", encoding="utf-8") as f : 
                f.write(output)
            print(f"YAML format written to {output_file.resolve()}")

    except FileNotFoundError as e : 
        print(f"Error :  {e}. Please ensure the project structure JSON file exists.")
    except Exception as e : 
        print(f"An unexpected error occurred :  {e}")

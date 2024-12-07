# utils/promtps.py 
file_summary_prompt = '''
Generate a concise JSON summary of the provided Python file with the following structure:
```python
{code}
```
Translate this into following concise JSON format
 ```json
{{
  "file": "filename.py",
  "purpose": "Brief description of the script's overall purpose",
  "main_functionality": "Detailed description of the script's core functionality",
  "dependencies": ["project_module1.class", "project_module2.function"], // Project modules, classes, functions
  "imports": ["external_module1", "project_module2","external_module1.function"], // External packages/modules 
  "functions": [
    {{
      "name": "function_name",
      "description": "What the function does",
      "signature": "function_signature(params) -> return_type",
      "dependencies": ["module1.class", "module1.class (function)","module2.function","class (function)","function"] // Project modules, classes, functions
    }}
  ],
  "classes": [
    {{
      "name": "ClassName",
      "class_summary": "Brief description of the class",
      "attributes": {{
        "attr_name": {{"type": "attr_type", "description": "attribute description"}}
      }},
      "methods": [
        {{
          "name": "method_name",
          "description": "What the method does",
          "signature": "method_signature(params) -> return_type",
          "dependencies": ["module1.class", "module1.class (function)","module2.function","class (function)","function"] // Project modules, classes, functions
        }}
      ]
    }}
  ],
  "main": "Description of the main execution block or 'No main block'",
  "notes":"Additional information that was not captured by above keys"
}}
```
Ensure the JSON is properly formatted by strictly providing information for the fields desired.

'''
# For file_summary_prompt
# Additional Fields That Could Be Helpful:

# To create more comprehensive documents, it would be beneficial to extract additional information from the Python file, such as:

# Docstrings and Comments: Detailed explanations within the code that provide context, usage examples, and additional insights.

# Exception Handling: Information about how the script handles errors and exceptions.

# Configuration Parameters: Any settings or parameters that can be adjusted.

# Test Cases (if any): Insights from test scripts that show expected behaviors and edge cases.
# Characteristics of Additional Fields:

# Descriptive: Provide detailed explanations beyond what is immediately apparent in the code.

# Structured: Organized in a way that can be programmatically parsed and utilized.

# Relevant: Directly related to the functionality and purpose of the script.

folder_summary_prompt = """
Generate a concise JSON summary of the provided folder file information with the following structure:
```Folder files information:
{folder_files_info_str}
```
Translate this into following concise JSON format
 ```json
{{
  "purpose": "Brief description of the folder's overall purpose",
  "main_functionality":"Detailed description of the folder scripts' core functionality",
  "files": ['firsfile.py','second_file.py'],
  "functions": ["name, description, signature"],
  "subfolders": ["folder1", "folder2"],
  "interrelationships": "Describe how files and subfolders interact",
  "notes":"Additional information that was not captured by above keys"
  
}}
```
Ensure the JSON is properly formatted by strictly providing information for the fields desired.
"""
generate_prd_prompt = """As a Product Manager, analyze the following code summary and generate a Product Requirements Document (PRD) in JSON format, including a high-level project summary:
Please ensure the PRD is comprehensive and based solely on the information provided.
Code Summary:
{folder_summary}

Please translate this into following Product Requirements Document (PRD)

```json
{{
    "Project Name": "",//string
    "Project Summary": "", //string
    "Product Goals": [""], //list of strings
    "User Stories": [""], //list of strings
    "Functional Requirements": [], //list of objects
    "Non-Functional Requirements": [],//list of objects
    "Anything Unclear": [""] //list of objects
}}
```

"""


generate_system_design_prompt = """As an Architect, analyze the following PRD and generate a System Design Document in JSON format:

PRD:
{folder_summary_str}

System Design Format:
{{
    "Architecture Overview": "{architecture_overview}",
    "Components": {components},
    "Data Models": {data_models},
    "APIs": {apis},
    "Technology Stack": {technology_stack},
    "Security Considerations": {security_considerations},
    "Scalability Considerations": {scalability_considerations}
}}
Fill in the System Design Document based on the PRD.

Please output only the JSON and nothing else.
"""

generate_task_list_prompt = """
As a Project Manager, analyze the following System Design Document and generate a Task List in JSON format.

System Design Document:
{system_design_document}

Task List Format:
{{
    "Tasks": [
        {{
            "ID": "",
            "Description": "",
            "Related Requirements": [],
            "Assigned To": "",
            "Estimated Effort": "",
            "Dependencies": [],
            "Priority": "",
            "Status": ""
        }}
    ]
}}

Please ensure the Task List is detailed and covers all necessary tasks.

Please output only the JSON and nothing else.
"""

generate_sequence_diagram_prompt = """As a Software Architect, generate a sequence diagram description in PlantUML format based on the following project structure:

Project Structure:
{project_data}

Include the main interactions between classes and functions.

Please output only the PlantUML code and nothing else.
"""




# generate_sequence_diagram_prompt = """
# As a Software Architect, generate a sequence diagram in PlantUML format based on the following folder summary:

# Folder Summary:
# {folder_summary}

# Focus on illustrating how the functions interact when fetching and processing data.

# Provide the sequence diagram code in PlantUML format. Do not include any additional explanation.

# """

generate_project_summary_prompt = """
As a Software Architect, provide a comprehensive project summary based on the following folder summaries:

{folder_summaries_str}

The summary should include:
- Project objectives and scope.
- High-level system architecture and components.
- Key functionalities and features.
- Technologies and tools used.
- How different modules and components interrelate and interact.

Please provide the summary as plain text.

"""



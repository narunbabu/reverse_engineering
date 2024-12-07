# import json
# import re

# # Your original summary_text with escape characters and code block delimiters
# summary_text = r"""```json
# {
#   "file": "food.py",
#   "imports": [
#     "random",
#     "pygame"
#   ],
#   "main": {
#     "description": "No main execution block found in this file.",
#     "steps": []
#   }
# }
# ```"""
# summary_text2 =r""" Here's the JSON summary for the provided `food.py`:

# ```json
# {
#   "file": "food.py",
#   "imports": [
#     "random",
#     "pygame"
#   ],
#   "classes": [
#     {
#       "name": "Food",
#       "class_summary": "Represents food item in the game, managing its position and rendering.",
#       "attributes": {
#         "screen_width": "The width of the game screen.",
#         "screen_height": "The height of the game screen.",
#         "_x": "Private x-coordinate of the food position.",
#         "_y": "Private y-coordinate of the food position."
#       },
#       "methods": [
#         {
#           "name": "__init__",
#           "description": "Initializes the food object with screen dimensions and generates initial position.",
#           "input": ["screen_width: int", "screen_height: int"],
#           "return": null,
#           "dependencies": [
#             "self.generate"
#           ]
#         },
#         {
#           "name": "x",
#           "description": "Property getter for x-coordinate of the food.",
#           "input": [],
#           "return": "int",
#           "dependencies": [
#             "self._x"
#           ]
#         },
#         {
#           "name": "y",
#           "description": "Property getter for y-coordinate of the food.",
#           "input": [],
#           "return": "int",
#           "dependencies": [
#             "self._y"
#           ]
#         },
#         {
#           "name": "generate",
#           "description": "Generates a new random position for the food within screen boundaries.",
#           "input": [],
#           "return": "None",
#           "dependencies": [
#             "random.randint",
#             "self.screen_width",
#             "self.screen_height"
#           ]
#         },
#         {
#           "name": "draw",
#           "description": "Draws the food as a red rectangle on the given screen.",
#           "input": ["screen"],
#           "return": null,
#           "dependencies": [
#             "pygame.draw",
#             "self.x",
#             "self.y"
#           ]
#         },
#         {
#           "name": "__str__",
#           "description": "Returns a string representation of the food object.",
#           "input": [],
#           "return": "str",
#           "dependencies": [
#             "self.x",
#             "self.y"
#           ]
#         },
#         {
#           "name": "__repr__",
#           "description": "Returns the official string representation of the food object.",
#           "input": [],
#           "return": "str",
#           "dependencies": [
#             "__str__ method"
#           ]
#         }
#       ]
#     }
#   ],
#   "main": {
#     "description": "No main execution block found in this file.",
#     "steps": []
#   }
# }
# ```"""

# # Function to extract and parse JSON from the string
# def extract_and_parse_json(text):
#     # Regex pattern to capture the JSON block between ```json and ```
#     json_pattern = r'```json\s*(\{.*?\})\s*```'
    
#     # Search for the JSON part using the pattern
#     match = re.search(json_pattern, text, flags=re.DOTALL)
    
#     if match:
#         # Extract the JSON part and unescape any escaped characters
#         json_string = match.group(1)
#         json_string = json_string.encode('utf-8').decode('unicode_escape')
        
#         # Parse the cleaned JSON string
#         try:
#             json_data = json.loads(json_string)
#             print("JSON parsed successfully!")
#             return json_data
#         except json.JSONDecodeError as e:
#             print("Failed to parse JSON:")
#             print(e)
#     else:
#         print("No JSON found in the text.")
#         return None

# # Extract and parse JSON from both summary_text and summary_text2
# print('summary_text \n')
# json_data1 = extract_and_parse_json(summary_text)
# if json_data1:
#     print(json.dumps(json_data1, indent=2))

# print('\nsummary_text2 \n')
# json_data2 = extract_and_parse_json(summary_text2)

# Optionally, you can pretty-print the extracted JSON

# if json_data2:
#     print(json.dumps(json_data2, indent=2))
import json
import re
from utils.project_manager import ProjectManager
from utils.config import PROJECT_PATH  # Import PROJECT_PATH from config

# Initialize ProjectManager
project_manager = ProjectManager(PROJECT_PATH)

# Define the path to the response text file
response_text_file = project_manager.get_analysis_folder() / 'response_text.txt'

# Function to extract and parse JSON from the string
def extract_and_parse_json(text):
    # Regex pattern to capture the JSON block between ```json and ```
    json_pattern = r'```json\s*(\{.*?\})\s*```'
    
    # Search for the JSON part using the pattern
    match = re.search(json_pattern, text, flags=re.DOTALL)
    
    if match:
        # Extract the JSON part and unescape any escaped characters
        json_string = match.group(1)
        json_string = json_string.encode('utf-8').decode('unicode_escape')
        
        # Parse the cleaned JSON string
        try:
            json_data = json.loads(json_string)
            print("JSON parsed successfully!")
            return json_data
        except json.JSONDecodeError as e:
            print("Failed to parse JSON:")
            print(e)
    else:
        print("No JSON found in the text.")
        return None

# Read the response text file
try:
    with open(response_text_file, 'r', encoding='utf-8') as file:
        response_text = file.read()
    
    # Extract and parse JSON from the read text
    json_data = extract_and_parse_json(response_text)
    
    if json_data:
        # Optionally, you can pretty-print the extracted JSON
        print(json.dumps(json_data, indent=2))

except FileNotFoundError:
    print(f"File {response_text_file} not found.")
except Exception as e:
    print(f"An error occurred: {e}")

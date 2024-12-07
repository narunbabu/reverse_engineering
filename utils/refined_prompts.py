# utils/refined_promtps.py 

file_summary_prompt ='''
Please analyze the following Python code and generate a JSON summary that includes only the specified sections and fields as detailed below. Do not add any extra sections, keys, or information. The JSON should include the following top-level keys:

file: File name

purpose: Summarize the purpose of this script.

main_functionality: Provide a detailed description of the script's main functionality.

dependencies: List public dependencies and dependencies on project modules, classes, and methods.

imports: Provide a list of all imported modules and classes.

functions: List standalone functions, each containing:
    name: Function name.
    description: Brief description of what the function does.
    signature: Function signature with parameters and return type.
    dependencies: Dependencies used within the function.

classes: List classes, each containing:
    name: Class name.
    class_summary: Brief description of the class.
    attributes: Dictionary with attribute names as keys and a dictionary containing "type" and "description" as values.
    methods: List of methods, each containing:
        name: Method name.
        description: Brief description of what the method does.
        signature: Method signature with parameters and return type.
        dependencies: Dependencies used within the method.
main: Describe the main execution block, including steps.

Additional Instructions:

If a section is not applicable (e.g., the file contains no classes or functions), include the section with an appropriate value:
For lists, use an empty list [].
For strings or descriptions, provide an appropriate message (e.g., "The file does not contain a main execution block.").
Do not include any extra keys or sections not specified above.
Consider docstrings and comments in the analysis for accurate descriptions.
Ensure the JSON is properly formatted with correct syntax and quoting.
Be concise and precise in your descriptions.
Do not include any explanations, additional notes, or content outside of the JSON output.


Example 1: snake.py
```python
## snake.py

import pygame

class Snake:
    def __init__(self, x: int = 100, y: int = 50, length: int = 3, direction: str = 'right'):
        self.x = x
        self.y = y
        self.length = length
        self.direction = direction
        self.body = [(x - i * 10, y) for i in range(length)]

    def move(self):
        head_x, head_y = self.body[0]
        if self.direction == 'up':
            new_head = (head_x, head_y - 10)
        elif self.direction == 'down':
            new_head = (head_x, head_y + 10)
        elif self.direction == 'left':
            new_head = (head_x - 10, head_y)
        elif self.direction == 'right':
            new_head = (head_x + 10, head_y)

        self.body.insert(0, new_head)
        if len(self.body) > self.length:
            self.body.pop()

    def grow(self):
        self.length += 1

    def get_body(self) -> list[tuple[int, int]]:
        return self.body

    def get_direction(self) -> str:
        return self.direction

    def set_direction(self, direction: str):
        if direction in ['up', 'down', 'left', 'right']:
            self.direction = direction

    def __str__(self) -> str:
        return f"Snake(body={{self.body}}, direction={{self.direction}})"

    def __repr__(self) -> str:
        return self.__str__()
```
JSON Output:

```json

{{
  "purpose": "Defines the Snake class for a Snake game, handling movement, growth, and direction.",
  "main_functionality": "Implements the Snake class to manage the snake's behavior in the game.",
  "dependencies": ["pygame"],
  "imports": ["pygame"],
  "functions": [],
  "classes": [
    {{
      "name": "Snake",
      "class_summary": "Represents the snake in the game, managing its body, movement, and direction.",
      "attributes": {{
        "x": {{"type": "int", "description": "The x-coordinate of the snake's head."}},
        "y": {{"type": "int", "description": "The y-coordinate of the snake's head."}},
        "length": {{"type": "int", "description": "Current length of the snake."}},
        "direction": {{"type": "str", "description": "Current movement direction ('up', 'down', 'left', 'right')."}},
        "body": {{"type": "list[tuple[int, int]]", "description": "Positions of the snake's body segments."}}
      }},
      "methods": [
        {{
          "name": "__init__",
          "description": "Initializes the Snake object with position, length, direction, and body.",
          "signature": "__init__(self, x: int = 100, y: int = 50, length: int = 3, direction: str = 'right') -> None",
          "dependencies": []
        }},
        {{
          "name": "move",
          "description": "Updates the snake's position based on its direction.",
          "signature": "move(self) -> None",
          "dependencies": []
        }},
        {{
          "name": "grow",
          "description": "Increases the snake's length by one.",
          "signature": "grow(self) -> None",
          "dependencies": []
        }},
        {{
          "name": "get_body",
          "description": "Returns the positions of the snake's body segments.",
          "signature": "get_body(self) -> list[tuple[int, int]]",
          "dependencies": []
        }},
        {{
          "name": "get_direction",
          "description": "Returns the current direction of the snake.",
          "signature": "get_direction(self) -> str",
          "dependencies": []
        }},
        {{
          "name": "set_direction",
          "description": "Sets the snake's direction if valid.",
          "signature": "set_direction(self, direction: str) -> None",
          "dependencies": []
        }},
        {{
          "name": "__str__",
          "description": "Returns a string representation of the snake.",
          "signature": "__str__(self) -> str",
          "dependencies": []
        }},
        {{
          "name": "__repr__",
          "description": "Returns the official string representation of the snake.",
          "signature": "__repr__(self) -> str",
          "dependencies": []
        }}
      ]
    }}
  ],
  "main": "The file does not contain a main execution block."
}}
```
Example 2: utils/llm_client.py
```python

# utils/llm_client.py

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple
import json
import logging

from configs.llm_config import LLMConfig

# Import your Ollama and Anthropic clients here
from llm_clients.ollama_client import OllamaLLM
from llm_clients.anthropic_client import AnthropicLLM

class LLMType(Enum):
    ANTHROPIC = 'anthropic'
    OLLAMA = 'ollama'

class LLMClient:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.llm: Optional[object] = None  # Initialize as None
        self.llm_type: Optional[LLMType] = None

        # Determine LLM type based on the config
        if self.config.api_type == 'anthropic':
            self.llm_type = LLMType.ANTHROPIC
        elif self.config.api_type == 'ollama':
            self.llm_type = LLMType.OLLAMA
        else:
            raise ValueError(f"Unsupported LLM type: {{self.config.api_type}}")

        # Handle streaming flag if present
        self.stream = self.config.stream if hasattr(self.config, 'stream') else False

    async def __aenter__(self):
        if self.llm_type == LLMType.ANTHROPIC:
            self.llm = AnthropicLLM(self.config)
        elif self.llm_type == LLMType.OLLAMA:
            self.llm = OllamaLLM(self.config)
        else:
            raise ValueError(f"Unsupported LLM type: {{self.llm_type}}")

        # Initialize the LLM client within its context
        await self.llm.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.llm:
            await self.llm.__aexit__(exc_type, exc_value, traceback)

    async def ask(self, prompt: str) -> Tuple[str, dict]:
        """
        Send a prompt to the selected LLM and receive the response along with token usage.

        Args:
            prompt (str): The user prompt.

        Returns:
            tuple: (response_text, usage_dict)
        """
        if not self.llm:
            raise RuntimeError("LLMClient is not initialized. Use 'async with' to initialize it.")

        return await self.llm.ask(prompt)

    async def ask_with_retry(self, prompt: str, max_retries: int = 3, initial_delay: float = 1.0) -> Tuple[str, dict]:
        """
        Send a prompt with automatic retry mechanism for overloaded errors.

        Args:
            prompt (str): The user prompt.
            max_retries (int): Maximum number of retry attempts.
            initial_delay (float): Initial delay between retries in seconds.

        Returns:
            tuple: (response_text, usage_dict)
        """
        if not self.llm:
            raise RuntimeError("LLMClient is not initialized. Use 'async with' to initialize it.")

        return await self.llm.ask_with_retry(prompt, max_retries, initial_delay)

    async def count_tokens(self, messages: list, system: Optional[str] = None) -> int:
        """
        Count tokens using the underlying LLM's token counting method.

        Args:
            messages (list): List of message dictionaries.
            system (str, optional): System prompt.

        Returns:
            int: Number of tokens.
        """
        if not self.llm:
            raise RuntimeError("LLMClient is not initialized. Use 'async with' to initialize it.")

        return await self.llm.count_tokens(messages, system)
    ```
JSON Output:

```json

{{
  "purpose": "Provides the LLMClient class to interact with different Large Language Models (LLMs) like Anthropic and Ollama.",
  "main_functionality": "Implements an asynchronous context manager for LLM interactions, handling initialization and requests.",
  "dependencies": [
    "asyncio",
    "dataclasses",
    "enum",
    "typing",
    "json",
    "logging",
    "configs.llm_config",
    "llm_clients.ollama_client",
    "llm_clients.anthropic_client"
  ],
  "imports": [
    "asyncio",
    "dataclasses.dataclass",
    "enum.Enum",
    "typing.Optional",
    "typing.Tuple",
    "json",
    "logging",
    "configs.llm_config.LLMConfig",
    "llm_clients.ollama_client.OllamaLLM",
    "llm_clients.anthropic_client.AnthropicLLM"
  ],
  "functions": [],
  "classes": [
    {{
      "name": "LLMType",
      "class_summary": "An enumeration of supported LLM types.",
      "attributes": {{}},
      "methods": []
    }},
    {{
      "name": "LLMClient",
      "class_summary": "An asynchronous context manager to interact with different LLMs.",
      "attributes": {{
        "config": {{"type": "LLMConfig", "description": "Configuration for the LLM."}},
        "llm": {{"type": "Optional[object]", "description": "Instance of the selected LLM client."}},
        "llm_type": {{"type": "Optional[LLMType]", "description": "Type of the LLM based on config."}},
        "stream": {{"type": "bool", "description": "Flag indicating if streaming is enabled."}}
      }},
      "methods": [
        {{
          "name": "__init__",
          "description": "Initializes the LLMClient with the given configuration.",
          "signature": "__init__(self, config: LLMConfig) -> None",
          "dependencies": ["LLMConfig", "LLMType"]
        }},
        {{
          "name": "__aenter__",
          "description": "Enters the asynchronous context, initializing the LLM client.",
          "signature": "__aenter__(self) -> LLMClient",
          "dependencies": ["AnthropicLLM", "OllamaLLM"]
        }},
        {{
          "name": "__aexit__",
          "description": "Exits the asynchronous context, properly closing the LLM client.",
          "signature": "__aexit__(self, exc_type, exc_value, traceback) -> None",
          "dependencies": []
        }},
        {{
          "name": "ask",
          "description": "Sends a prompt to the LLM and receives the response.",
          "signature": "ask(self, prompt: str) -> Tuple[str, dict]",
          "dependencies": []
        }},
        {{
          "name": "ask_with_retry",
          "description": "Sends a prompt with retry logic for handling errors.",
          "signature": "ask_with_retry(self, prompt: str, max_retries: int = 3, initial_delay: float = 1.0) -> Tuple[str, dict]",
          "dependencies": []
        }},
        {{
          "name": "count_tokens",
          "description": "Counts tokens using the LLM's token counting method.",
          "signature": "count_tokens(self, messages: list, system: Optional[str] = None) -> int",
          "dependencies": []
        }}
      ]
    }}
  ],
  "main": "The file does not contain a main execution block."
}}
```
Example 3: main.py
```python

# main.py

import asyncio
from pathlib import Path
from configs.llm_config import LLMConfig
from utils.llm_client import LLMClient
from utils.code_parser import CodeParser
from utils.document_generator import DocumentGenerator
from roles.product_manager import ProductManager
from roles.architect import Architect
from roles.project_manager import ProjectManager

async def main():
    llm_config = LLMConfig()
    if not llm_config.api_key:
        raise ValueError("API key is missing. Please set the ANTHROPIC_API_KEY environment variable.")
    
    # Optional: Print the API key length for verification without revealing it
    print(f"API Key length: {{len(llm_config.api_key)}} characters")
    
    async with LLMClient(llm_config) as llm_client:
        project_path = Path(r"C:\StandApp\SeisTransform")  # Update this path as needed
        project_type = None  # Set to 'python', 'javascript', 'react', 'laravel', etc., or leave as None to auto-detect
    
        # Initialize utilities and roles
        code_parser = CodeParser(project_path, project_type)
        doc_generator = DocumentGenerator(llm_client, project_path)
        product_manager = ProductManager(code_parser, doc_generator)
        # architect = Architect(doc_generator)
        # project_manager = ProjectManager(doc_generator)
    
        # # Simulate role interactions
        prd = await product_manager.create_prd()
        # system_design = await architect.create_system_design(prd)
        # task_list = await project_manager.create_task_list(system_design)

if __name__ == "__main__":
    asyncio.run(main())
```
JSON Output:

```json

{{
  "purpose": "Entry point script that initializes configurations and utilities to interact with LLMs and manage project roles.",
  "main_functionality": "Sets up the LLM configuration and initializes utilities and role classes to perform actions like creating PRDs.",
  "dependencies": [
    "asyncio",
    "pathlib",
    "configs.llm_config",
    "utils.llm_client",
    "utils.code_parser",
    "utils.document_generator",
    "roles.product_manager",
    "roles.architect",
    "roles.project_manager"
  ],
  "imports": [
    "asyncio",
    "pathlib.Path",
    "configs.llm_config.LLMConfig",
    "utils.llm_client.LLMClient",
    "utils.code_parser.CodeParser",
    "utils.document_generator.DocumentGenerator",
    "roles.product_manager.ProductManager",
    "roles.architect.Architect",
    "roles.project_manager.ProjectManager"
  ],
  "functions": [
    {{
      "name": "main",
      "description": "Main asynchronous function that sets up configurations and initializes role interactions.",
      "signature": "main() -> Coroutine",
      "dependencies": [
        "LLMConfig",
        "LLMClient",
        "CodeParser",
        "DocumentGenerator",
        "ProductManager"
      ]
    }}
  ],
  "classes": [],
  "main": "Contains an asynchronous main function that is executed when the script is run directly."
}}
```
**The python code to generate the JSON Output:**

Now return the JSON summary for the provided {python_file_name}
```python
{code}
```
'''

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
  "dependencies": ["external_module1", "project_module2"],
  "imports": ["module1", "module2"],
  "functions": [
    {{
      "name": "function_name",
      "description": "What the function does",
      "signature": "function_signature(params) -> return_type",
      "dependencies": ["used_modules"]
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
          "dependencies": ["used_modules"]
        }}
      ]
    }}
  ],
  "main": "Description of the main execution block or 'No main block'"
}}
```
Ensure the JSON is properly formatted by strictly providing information for the fields desired.

'''
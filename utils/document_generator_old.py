# utils/document_generator.py

import json
import re, os
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Union
from collections import defaultdict
from utils.logger import setup_logger
from utils.project_manager import ProjectManager
from utils.prompts import (
    file_summary_prompt,
    generate_prd_prompt,
    generate_system_design_prompt,
    generate_task_list_prompt,
    generate_sequence_diagram_prompt,
    folder_summary_prompt,
    generate_project_summary_prompt,
)

class DocumentGenerator:
    def __init__(self, primary_llm_client, fallback_llm_client, project_manager: ProjectManager):
        """
        Initialize the DocumentGenerator with primary and fallback LLM clients and project manager.

        Args:
            primary_llm_client: Primary LLM client for interacting with language model
            fallback_llm_client: Fallback LLM client for interacting with language model
            project_manager (ProjectManager): Manager for project-related operations
        """
        self.primary_llm_client = primary_llm_client
        self.fallback_llm_client = fallback_llm_client
        self.project_manager = project_manager
        self.project_folder = self.project_manager.get_project_folder()
        self.analysis_folder = self.project_manager.get_analysis_folder()
        self.project_path = self.project_manager.get_project_folder()
        self.code_summary_folder = self.analysis_folder / "code_summaries"
        # self.logger = setup_logger(self.analysis_folder)
        self.logger = self.project_manager.logger  # Use the same logger
        self.logger.info(f"Started project creation for '{self.project_folder.name}'")
        self.logger.info("DocumentGenerator initialized.")

    async def generate_prd(self, code_summary: str) -> dict:
        prompt = generate_prd_prompt.format(code_summary=code_summary)
        start_time = datetime.now()
        self.logger.debug("LLM Request: Generate PRD")
        try:
            prd_text, usage = await self.primary_llm_client.ask_with_retry(prompt)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            self.logger.debug(f"LLM Name: {self.primary_llm_client.config.model}")
            self.logger.debug(f"Input Tokens: {input_tokens}")
            self.logger.debug(f"Output Tokens: {output_tokens}")
            self.logger.debug(f"Request Duration: {duration} seconds")
            json_text = self.extract_json_from_text(prd_text)
            if json_text:
                prd = json.loads(json_text)
                self.logger.info(f"Generated PRD successfully in {duration:.2f} seconds with {output_tokens} output tokens.")
            else:
                self.logger.error("No JSON found in LLM response for PRD.")
                self.logger.error(f"LLM Response: {prd_text}")
                prd = {}
        except Exception as e:
            self.logger.error(f"Failed to generate PRD: {e}")
            prd = {}
        return prd

    async def generate_system_design(self, prd: dict) -> dict:
        prompt = generate_system_design_prompt.format(prd=json.dumps(prd, indent=2))
        start_time = datetime.now()
        self.logger.debug("LLM Request: Generate System Design")
        try:
            design_text, usage = await self.primary_llm_client.ask_with_retry(prompt)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            self.logger.debug(f"LLM Name: {self.primary_llm_client.config.model}")
            self.logger.debug(f"Input Tokens: {input_tokens}")
            self.logger.debug(f"Output Tokens: {output_tokens}")
            self.logger.debug(f"Request Duration: {duration} seconds")
            json_text = self.extract_json_from_text(design_text)
            if json_text:
                system_design = json.loads(json_text)
                self.logger.info(f"Generated System Design successfully in {duration:.2f} seconds with {output_tokens} output tokens.")
            else:
                self.logger.error("No JSON found in LLM response for System Design.")
                self.logger.error(f"LLM Response: {design_text}")
                system_design = {}
        except Exception as e:
            self.logger.error(f"Failed to generate System Design: {e}")
            system_design = {}
        return system_design

    async def generate_task_list(self, system_design: dict) -> dict:
        prompt = generate_task_list_prompt.format(system_design=json.dumps(system_design, indent=2))
        start_time = datetime.now()
        self.logger.debug("LLM Request: Generate Task List")
        try:
            tasks_text, usage = await self.primary_llm_client.ask_with_retry(prompt)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            self.logger.debug(f"LLM Name: {self.primary_llm_client.config.model}")
            self.logger.debug(f"Input Tokens: {input_tokens}")
            self.logger.debug(f"Output Tokens: {output_tokens}")
            self.logger.debug(f"Request Duration: {duration} seconds")
            json_text = self.extract_json_from_text(tasks_text)
            if json_text:
                task_list = json.loads(json_text)
                self.logger.info(f"Generated Task List successfully in {duration:.2f} seconds with {output_tokens} output tokens.")
            else:
                self.logger.error("No JSON found in LLM response for Task List.")
                self.logger.error(f"LLM Response: {tasks_text}")
                task_list = {}
        except Exception as e:
            self.logger.error(f"Failed to generate Task List: {e}")
            task_list = {}
        return task_list

    async def generate_sequence_diagram(self, project_data: dict) -> str:
        prompt = generate_sequence_diagram_prompt.format(project_data=json.dumps(project_data, indent=2))
        try:
            diagram_text, usage = await self.primary_llm_client.ask_with_retry(prompt)
            if "@startuml" in diagram_text and "@enduml" in diagram_text:
                self.logger.info("Generated Sequence Diagram successfully.")
                return diagram_text
            else:
                self.logger.error("No valid PlantUML code found in LLM response for Sequence Diagram.")
                self.logger.error(f"LLM Response: {diagram_text}")
                return ""
        except Exception as e:
            self.logger.error(f"Failed to generate Sequence Diagram: {e}")
            return ""

#######################################################################################
    
    async def generate_summary(self, relative_path: Path, code: str, max_retries: int = 4) -> dict:
        """
        Generate a structured summary for a given Python file.

        Args:
            code (str): File contents
            relative_path (Path): File's relative path

        Returns:
            dict: Structured summary of the file
        """
        python_file_name = relative_path.name
        # self.logger.info(f"Generating summary for: {python_file_name}")

        default_values = {
            'file': "",
            'purpose': "",
            'main_functionality': "",
            'dependencies': [],
            'imports': [],
            'functions': [],
            'classes': [],
            'main': ""
        }
        required_keys = list(default_values.keys())

        summary = await self._attempt_generate_summary(
            relative_path, code, required_keys, max_retries, self.primary_llm_client, 'primary'
        )
        if not summary:
            # If primary LLM fails, attempt with fallback LLM
            self.logger.info(f"Primary LLM failed. Attempting to use fallback LLM for summarizing {relative_path}")
            summary = await self._attempt_generate_summary(
                relative_path, code, required_keys, 1, self.fallback_llm_client, 'fallback'
            )

        if summary:
            # Save the summary to a file
            # Remove relative_to call
            summary_file_path = self.code_summary_folder / relative_path.with_suffix('.json')
            summary_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(summary_file_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            self.logger.info(f"Summary saved to {summary_file_path.resolve()}")
        else:
            self.logger.error(f"Failed to generate summary for {relative_path}")

        return summary

    
    async def _attempt_generate_summary(self, relative_path: Path, code: str, required_keys: list, max_retries: int, llm_client, llm_label: str) -> dict:
        """
        Helper method to attempt generating summary with a specified LLM client.

        Args:
            relative_path (Path): File's relative path
            code (str): File contents
            required_keys (list): List of required keys in the summary
            max_retries (int): Number of retry attempts
            llm_client: The LLM client to use (primary or fallback)
            llm_label (str): Label for logging ('primary' or 'fallback')

        Returns:
            dict: Structured summary if successful, else None
        """
        python_file_name = relative_path.name
        for attempt in range(max_retries):
            prompt = file_summary_prompt.format(python_file_name=python_file_name, code=code)
            start_time = datetime.now()
            self.logger.debug(f"LLM Request: Summarize {relative_path} with {llm_label} LLM (Attempt {attempt + 1})")

            try:
                response_text, usage = await llm_client.ask_with_retry(prompt)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                self.logger.debug(f"LLM Name: {llm_client.config.model}")
                self.logger.debug(f"Input Tokens: {usage.get('input_tokens', 0)} Output Tokens: {usage.get('output_tokens', 0)}")
                self.logger.debug(f"Request Duration: {duration} seconds")

                self.logger.info(f"Generated summary for {relative_path} in {duration:.2f} seconds using {llm_label} LLM.")

                # Extract JSON from the response
                json_text = self.extract_json_from_text(response_text)
                if json_text:
                    try:
                        summary = json.loads(json_text)

                        # Inject the file_path relative to the project folder
                        new_summary = {
                            "file_path": str(relative_path)
                        }
                        new_summary.update(summary)

                        # Fill in missing keys with default values
                        for key in required_keys:
                            if key not in new_summary:
                                new_summary[key] = default_values[key]

                        return new_summary
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to parse summary as JSON using {llm_label} LLM: {e}")
                else:
                    self.logger.warning(f"No valid JSON found in LLM response for {relative_path} using {llm_label} LLM. Retrying...")
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1}: Failed to summarize {relative_path} with {llm_label} LLM: {e}")

        self.logger.error(f"Failed to generate valid summary for {relative_path} with {llm_label} LLM after {max_retries} attempts.")
        return {}

    async def summarize_folders(self) -> dict:
        """
        Summarize relevant folders in the project by reading code summaries from self.code_summary_folder.

        Returns:
            dict: A nested dictionary containing summaries of all relevant folders.
        """
        self.logger.info("Starting folder summarization using code summaries in code_summaries folder.")

        # Mapping from folder_path to list of file summaries
        folder_to_files = defaultdict(list)

        # Walk through code_summary_folder and build folder_to_files
        for root, dirs, files in os.walk(self.code_summary_folder):
            for file in files:
                if file.endswith('.json'):
                    summary_file_path = Path(root) / file
                    # Load the code summary
                    with open(summary_file_path, 'r', encoding='utf-8') as f:
                        file_info = json.load(f)
                    # Get the relative path from code_summary_folder
                    relative_path_from_code_summaries = summary_file_path.relative_to(self.code_summary_folder)
                    # The folder path is the parent of the file
                    folder_path = relative_path_from_code_summaries.parent
                    # Build folder_key
                    if str(folder_path) != '.':
                        folder_key = '.' + os.sep + str(folder_path)
                        self.logger.debug(f"folder_path: {folder_path} File path: {relative_path_from_code_summaries}")
                        folder_to_files[folder_key].append(file_info)
                    else:
                        folder_to_files[str(folder_path)].append(file_info)

        self.logger.debug(f"folder_to_files: {folder_to_files.keys()}")

        # Build the hierarchical folder structure
        folder_tree = self.build_folder_tree(folder_to_files.keys(), folder_to_files)
        self.logger.debug(f"Built folder_tree: {folder_tree}")

        async def build_and_summarize(node):
            """
            Recursively build summaries for each folder and its subfolders.

            Args:
                node (dict): Current node in the folder tree.

            Returns:
                dict: Summary of the current folder including subfolder summaries.
            """
            folder_path = node['path']
            folder_name = node['name']
            files = node['files']
            file_names = files  # Already a list of file names

            self.logger.info(f"Summarizing folder: {folder_path}")

            # Determine the correct folder_key to match folder_to_files
            if folder_path != '.':
                folder_key = '.' + os.sep + folder_path
            else:
                folder_key = folder_path

            self.logger.debug(f"Folder_key: {folder_key} folder_path: {folder_path}")
            # file_infos = folder_to_files.get(folder_key, [])
            # self.logger.debug(f"file_infos: {file_infos}")

            folder_files_info = folder_to_files.get(folder_key, [])
            # [
            #     {
            #         "file_path": file_info.get("file_path", ""),
            #         "purpose": file_info.get("purpose", ""),
            #         "main_functionality": file_info.get("main_functionality", ""),
            #         "dependencies": file_info.get("dependencies", []),
            #         "imports": file_info.get("imports", [])
            #     }
            #     for file_info in file_infos
            # ]
            self.logger.info(f"Folder files: {files}")

            if folder_files_info:
                # self.logger.debug(f"folder_files_info[0]: {folder_files_info[0]}")

                # Convert folder_files_info to JSON string
                folder_files_info_str = json.dumps(folder_files_info, indent=2)

                # Prepare the prompt for the LLM
                prompt = folder_summary_prompt.format(folder_files_info_str=folder_files_info_str)

                # Generate summary for the folder
                summary = await self.generate_folder_summary(folder_path, prompt, max_retries=2)
                try:
                    self.logger.info(f"Summary: {summary}")
                except:
                    self.logger.error(f"Summary: Failed")

                # Initialize the folder summary object
                folder_summary = {
                    "name": folder_name,
                    "files": file_names,
                    "subfolders": [],
                    **summary
                    # "purpose": summary.get("purpose", ""),
                    # "interrelationships": summary.get("interrelationships", ""),
                    # "notes": summary.get("notes", "")
                }

                # Recursively summarize subfolders
                for subfolder_node in node.get('subfolders', []):
                    sub_summary = await build_and_summarize(subfolder_node)
                    folder_summary["subfolders"].append(sub_summary)
                return folder_summary
            else:
                # If there are no files, still summarize the folder
                # Prepare the prompt for the LLM with empty folder_files_info
                prompt = folder_summary_prompt.format(folder_files_info_str="[]")

                # Generate summary for the folder
                summary = await self.generate_folder_summary(folder_path, prompt, max_retries=2)
                self.logger.info(f"Summary: {summary}")

                # Initialize the folder summary object without files
                folder_summary = {
                    "name": folder_name,
                    "files": [],
                    "subfolders": [],
                    **summary
                    # "purpose": summary.get("purpose", ""),
                    # "interrelationships": summary.get("interrelationships", ""),
                    # "notes": summary.get("notes", "")
                }

                # Recursively summarize subfolders
                for subfolder_node in node.get('subfolders', []):
                    sub_summary = await build_and_summarize(subfolder_node)
                    folder_summary["subfolders"].append(sub_summary)
                return folder_summary

        # Start summarization from the root node
        summary = await build_and_summarize(folder_tree)

        return summary

    def build_folder_tree(self, folder_paths, folder_to_files):
        """
        Build a hierarchical folder tree from a list of folder paths.

        Args:
            folder_paths (iterable): An iterable of folder path strings.
            folder_to_files (dict): Mapping from folder path to list of files.

        Returns:
            dict: The root node representing the folder tree.
        """
        # Initialize the root node
        root = {
            "name": ".",
            "path": ".",
            "files": [Path(f.get("file_path", "")).name for f in folder_to_files.get('.', []) if "file_path" in f],
            "subfolders": []
        }

        path_to_node = {".": root}

        for path in folder_paths:
            if path == '.':
                continue  # Root already handled

            # Normalize path to use OS separator (handles Windows '\\' and Unix '/')
            normalized_path = Path(path)
            parts = normalized_path.parts

            current_node = root
            current_path = "."

            for part in parts:
                # Build the new path incrementally
                if current_path == ".":
                    new_path = part
                else:
                    new_path = os.path.join(current_path, part)

                # Check if the subfolder already exists
                existing = next((sf for sf in current_node["subfolders"] if sf["name"] == part), None)
                if existing:
                    current_node = existing
                    current_path = new_path
                else:
                    # Construct the key used in folder_to_files
                    folder_key = '.' + os.sep + new_path if current_path == "." else '.' + os.sep + new_path
                    # Retrieve files for this folder, if any
                    files = [Path(f.get("file_path", "")).name for f in folder_to_files.get(folder_key, []) if "file_path" in f]
                    if files:
                        self.logger.debug(f"Files found for folder '{folder_key}': {files}")
                    else:
                        self.logger.debug(f"No files found for folder '{folder_key}'.")

                    new_node = {
                        "name": part,
                        "path": new_path,
                        "files": files,
                        "subfolders": []
                    }
                    current_node["subfolders"].append(new_node)
                    current_node = new_node
                    current_path = new_path

        return root

    async def generate_folder_summary(self, relative_path: str, prompt: str, max_retries: int = 2) -> dict:
        """
        Generate a structured summary for a given folder using the provided prompt.

        Args:
            relative_path (str): Folder's relative path
            prompt (str): The prompt to send to the LLM
            max_retries (int): Number of retry attempts

        Returns:
            dict: Structured summary of the folder
        """
        # Attempt summarization with primary LLM
        summary = await self._attempt_generate_folder_summary(
            relative_path, prompt, max_retries, self.primary_llm_client, 'primary'
        )
        if summary:
            return summary

        # If primary LLM fails, attempt with fallback LLM
        self.logger.info(f"Primary LLM failed. Attempting to use fallback LLM for summarizing folder {relative_path}")
        summary = await self._attempt_generate_folder_summary(
            relative_path, prompt, max_retries, self.fallback_llm_client, 'fallback'
        )
        return summary

    async def _attempt_generate_folder_summary(self, relative_path: str, prompt: str, max_retries: int, llm_client, llm_label: str) -> dict:
        """
        Helper method to attempt generating folder summary with a specified LLM client.

        Args:
            relative_path (str): Folder's relative path
            prompt (str): The prompt to send to the LLM
            max_retries (int): Number of retry attempts
            llm_client: The LLM client to use (primary or fallback)
            llm_label (str): Label for logging ('primary' or 'fallback')

        Returns:
            dict: Structured folder summary if successful, else None
        """
        for attempt in range(max_retries):
            self.logger.debug(f"LLM Request: Summarize folder {relative_path} with {llm_label} LLM (Attempt {attempt + 1})")
            start_time = datetime.now()

            try:
                response_text, usage = await llm_client.ask_with_retry(prompt)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                self.logger.debug(f"LLM Name: {llm_client.config.model}")
                self.logger.info(f"Input Tokens: {usage.get('input_tokens', 0)} Output Tokens: {usage.get('output_tokens', 0)}")
                self.logger.debug(f"Request Duration: {duration} seconds")

                self.logger.info(f"Generated folder summary for {relative_path} in {duration:.2f} seconds using {llm_label} LLM.")

                # Extract JSON from the response
                json_text = self.extract_json_from_text(response_text)
                if json_text:
                    try:
                        summary = json.loads(json_text)
                        self.logger.info(f"Successfully parsed folder summary for {relative_path} using {llm_label} LLM.")
                        return summary
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to parse folder summary as JSON using {llm_label} LLM: {e}")
                else:
                    self.logger.warning(f"No valid JSON found in LLM response for folder {relative_path} using {llm_label} LLM. Retrying...")
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1}: Failed to summarize folder {relative_path} with {llm_label} LLM: {e}")

        self.logger.error(f"Failed to generate valid folder summary for {relative_path} with {llm_label} LLM after {max_retries} attempts.")
        return {}
    
    ####################################################################################

    async def generate_project_summary(self, folder_summaries) -> dict:

        folder_summaries_str = json.dumps(folder_summaries, indent=2)
        # llm_label='primary'

                # Prepare the prompt for the LLM
        prompt = generate_project_summary_prompt.format(folder_summaries_str=folder_summaries_str)

        start_time = datetime.now()
        self.logger.debug("LLM Request: Generate Project Summary")
        try:
            response_text, usage = await self.primary_llm_client.ask_with_retry(prompt)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # self.logger.info(f"Generated project summary: {response_text}")
            self.logger.info(f"Generated project summary  in {duration:.2f} seconds with {usage.get('input_tokens', 0)} input tokens, {usage.get('output_tokens', 0)} output tokens with LLM : {self.primary_llm_client.config.model}")
                
            project_summary = response_text.strip()
            return project_summary
        except Exception as e:
            self.logger.error(f"Failed to generate project summary: {e}")
            return "None Failed"

    def modify_prompt(self, prompt: str, attempt: int) -> str:
        """
        Modify the prompt based on the attempt number.
        """
        if attempt == 1:
            # Emphasize the importance of including all sections
            prompt += "\n\nIt's crucial that you include all the specified sections in your summary."
        elif attempt == 2:
            # Simplify the prompt or provide additional examples
            prompt = prompt.replace("Now, analyze and summarize the following code:", "Please summarize the following code:")
        elif attempt == 3:
            # Ask the LLM to double-check its response
            prompt += "\n\nPlease double-check that all sections are included in your summary."
        return prompt
    
    def extract_json_from_text(self, text: str) -> str:
        """
        Extract JSON content from the provided text. It looks for JSON within ```json code fences
        or triple-quoted strings.

        Args:
            text (str): The text containing JSON.

        Returns:
            str: The extracted JSON string if found, else None.
        """
        # Pattern to match JSON within ```json code fences
        json_fence_pattern = r'```json\s*(\{.*?\})\s*```'
        match = re.search(json_fence_pattern, text, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1)

        # Pattern to match JSON within triple quotes
        json_triple_quote_pattern = r'"""(\{.*?\})"""'
        match = re.search(json_triple_quote_pattern, text, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1)

        # Optionally, attempt to find any JSON object in the text
        json_general_pattern = r'(\{.*?\})'
        match = re.search(json_general_pattern, text, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1)

        return None


# code_llm_summarizer.py

import asyncio
import json
from pathlib import Path
import logging
import ast
import tokenize
import io
import tracemalloc

from utils.project_manager import ProjectManager
from utils.code_utils import has_meaningful_code  # Correctly imported
from configs.llm_config import LLMConfig
from utils.llm_client import LLMClient
from utils.document_generator import DocumentGenerator
from utils.config import PROJECT_PATH
from typing import Any, Dict, List, Optional

# Enable tracemalloc for detailed traceback (optional)
tracemalloc.start()

def remove_comments(code: str) -> str:
    """
    Remove comments from Python code while preserving docstrings.

    Args:
        code (str): The original Python code.

    Returns:
        str: The code without comments.
    """
    try:
        io_obj = io.StringIO(code)
        out = ""
        prev_toktype = tokenize.INDENT
        for tok in tokenize.generate_tokens(io_obj.readline):
            token_type, token_string, (start_line, start_col), (end_line, end_col), line = tok
            if token_type == tokenize.COMMENT:
                continue
            elif token_type == tokenize.STRING:
                if prev_toktype != tokenize.INDENT:
                    # Likely a docstring; keep it
                    out += token_string
            else:
                out += token_string
            prev_toktype = token_type
        return out
    except Exception as e:
        # In case of any parsing error, return the original code
        return code


async def main():
    # Initialize ProjectManager
    project_path = PROJECT_PATH  # PROJECT_PATH is already a Path object
    ignored_dirs = ['tests', '__pycache__', 'migrations', 'dist','build','.ipynb_checkpoints','assets','unused' ]  # Example directories to ignore
    ignored_files = ['setup.py', 'manage.py']             # Example files to ignore
    ignored_path_substrings = ['legacy', 'third_party','__pycache__']   # Example path substrings to ignore

    project_manager = ProjectManager(
            project_path=project_path,
            ignored_dirs=ignored_dirs,
            ignored_files=ignored_files,
            ignored_path_substrings=ignored_path_substrings
        )

    project_manager.initialize_logger()  # Initialize logger before workspace setup

    project_manager.setup_workspace(clean_existing=False)  # Now it's safe to use self.logger in setup_workspace

    # Define LLMConfigs (assuming LLMConfig and LLMClient are defined elsewhere)
    primary_llm_config = LLMConfig.get('ollama')       # Primary LLM configuration
    fallback_llm_config = LLMConfig.get('anthropic')  # Fallback LLM configuration

    # Use both LLMClient with context manager
    async with LLMClient(primary_llm_config) as primary_llm_client, \
               LLMClient(fallback_llm_config) as fallback_llm_client:
        # Initialize DocumentGenerator with both LLM clients
        generator = DocumentGenerator(primary_llm_client, fallback_llm_client, project_manager)
        
        

        async def file_summaries_gen():
            # Generate summaries for all Python files in the project, excluding ignored patterns
            python_files = project_manager.get_all_python_files(
                ignored_dirs=ignored_dirs,
                ignored_files=ignored_files,
                ignored_path_substrings=ignored_path_substrings
            )
            generator.logger.info(f"Found {len(python_files)} Python files in the project.")
            tasks = []
            for py_file in python_files:
                try:
                    code = py_file.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        code = py_file.read_text(encoding='latin-1')  # Fallback encoding
                        generator.logger.warning(f"Read {py_file} using 'latin-1' encoding due to UnicodeDecodeError with 'utf-8'.")
                    except Exception as e:
                        generator.logger.error(f"Failed to read {py_file} with both 'utf-8' and 'latin-1' encodings: {e}")
                        continue  # Skip this file
                
                # Remove comments (excluding docstrings)
                cleaned_code = remove_comments(code)

                if len(cleaned_code) > 0:
                    relative_path = project_manager.get_relative_path(py_file)
                    tasks.append(generator.generate_summary(relative_path, cleaned_code)) # Generating summary using LLM
            if tasks:
                await asyncio.gather(*tasks)
            else:
                generator.logger.info("No Python files with meaningful code found to summarize.")

        async def folder_summaries_gen():
            generator.logger.info("********************Folder summaries started*******************")
            folder_summaries = await generator.summarize_folders()
            folder_summaries_file = project_manager.get_analysis_folder() / "folder_summaries.json"

            with open(folder_summaries_file, "w", encoding="utf-8") as f:
                json.dump(folder_summaries, f, indent=2)

            generator.logger.info(f"Folder summaries written to {folder_summaries_file.resolve()}")
            generator.logger.info("********************Folder summaries Done*******************")

        async def all_other_doc_gen():
            # Load folder summaries
            folder_summary={}
            folder_summaries_file = project_manager.get_analysis_folder() / "folder_summaries.json"
            with open(folder_summaries_file, 'r', encoding='utf-8') as f:
                folder_summary = json.load(f)

            # # Generate Project Summary
            # project_summary = await generator.generate_project_summary(folder_summary)
            # # Save Project Summary
            # generator.save_project_summary(project_summary)
            
            # Generate PRD
            # prd = await generator.generate_prd(folder_summary)
            # # Save PRD
            # generator.save_prd(prd)

            prd_file = project_manager.get_analysis_folder() / "PRD.json"
            with open(prd_file, 'r', encoding='utf-8') as f:
                prd = json.load(f)


            # Generate System Design Document
            system_design = await generator.generate_system_design(folder_summary=prd)
            # Save System Design Document
            generator.save_system_design(system_design)

            # # Generate Task List
            # task_list = await generator.generate_task_list(system_design)
            # # Save Task List
            # generator.save_task_list(task_list)

            # # Generate Sequence Diagram
            # sequence_diagram = await generator.generate_sequence_diagram(folder_summary)
            # # Save Sequence Diagram
            # if sequence_diagram:
            #     generator.save_sequence_diagram(sequence_diagram)
            # else:
            #     generator.logger.error("Sequence Diagram generation failed.")

        await file_summaries_gen()
        # await folder_summaries_gen()
        # await all_other_doc_gen()

    # Close the logger to release the log file
    project_manager.close_logger()
# Run the main function
if __name__ == "__main__":
    asyncio.run(main())




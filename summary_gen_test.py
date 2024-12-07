
# summary_gen_test.py
import asyncio
import json
from pathlib import Path

from utils.project_manager import ProjectManager
from configs.llm_config import LLMConfig
from utils.llm_client import LLMClient
from utils.document_generator import DocumentGenerator
from utils.config import PROJECT_PATH

async def summarize_single_py_file():
    """
    Summarize a single relevant Python file in the project using both primary and fallback LLMs.
    """
    # Initialize ProjectManager
    project_manager = ProjectManager(PROJECT_PATH)
    project_manager.setup_workspace()
    project_path = project_manager.get_project_folder()

    # Define LLMConfigs for both primary and fallback LLMs
    primary_llm_config = LLMConfig.get('ollama')      # Primary LLM configuration
    fallback_llm_config = LLMConfig.get('anthropic') # Fallback LLM configuration

    # primary_llm_config = LLMConfig.get('ollama_llama_3.1_7b')      # Primary LLM configuration
    # fallback_llm_config = LLMConfig.get('ollama') # Fallback LLM configuration

    # Define directories and files to exclude
    excluded_dirs = {'.git', '__pycache__', 'venv', '.idea', '.vscode', 'build', 'dist'}
    excluded_files = {'setup.py', 'manage.py'}

    # Find the first relevant Python file
    py_file = None
    for file in project_path.rglob("*.py"):
        # Exclude files in unwanted directories
        if any(part in excluded_dirs for part in file.parts):
            continue
        # Exclude specific files
        if file.name in excluded_files:
            continue
        py_file = file
        break

    if not py_file:
        print("No Python files found to summarize.")
        return {}

    # Use both LLMClients with context manager
    async with LLMClient(primary_llm_config) as primary_llm_client, \
               LLMClient(fallback_llm_config) as fallback_llm_client:
        # Initialize DocumentGenerator with both LLM clients
        generator = DocumentGenerator(primary_llm_client, fallback_llm_client, project_manager)

        file_summaries = {}
        relative_path = py_file.relative_to(project_path)
        python_file_name = relative_path.name
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                code = f.read()
            # Skip empty files
            if not code.strip():
                print(f"File {python_file_name} is empty. Skipping.")
                return {}
            # Generate summary for the Python file
            summary = await generator.generate_summary(relative_path, code, max_retries=4)
            print(f"Summary for {python_file_name}:")
            print(json.dumps(summary, indent=2))
            file_summaries[str(relative_path)] = summary
            generator.logger.info(f"Summarized {relative_path}")
        except Exception as e:
            generator.logger.error(f"Failed to summarize {relative_path}: {e}")

        # Optionally, save the summaries to a JSON file
        # Uncomment the following lines if you wish to save the summary
        # summary_file = project_manager.get_analysis_folder() / "file_summaries.json"
        # with open(summary_file, "w", encoding="utf-8") as f:
        #     json.dump(file_summaries, f, indent=2)
        # print(f"Summaries saved to {summary_file}")

        return file_summaries

async def main():
    summaries = await summarize_single_py_file()
    print("Final Summaries:")
    print(json.dumps(summaries, indent=2))

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())

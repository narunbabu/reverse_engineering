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
    print(f"API Key length: {len(llm_config.api_key)} characters")
    
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


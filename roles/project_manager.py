# roles/project_manager.py
from utils.document_generator import DocumentGenerator
# roles/project_manager.py

class ProjectManager:
    def __init__(self, doc_generator: DocumentGenerator):
        self.doc_generator = doc_generator

    async def create_task_list(self, system_design: dict):
        task_list = await self.doc_generator.generate_task_list(system_design)
        self.doc_generator.save_document(task_list, "task")  # Removed 'await' here
        return task_list


# roles/architect.py
from utils.document_generator import DocumentGenerator
# roles/architect.py

class Architect:
    def __init__(self, doc_generator: DocumentGenerator):
        self.doc_generator = doc_generator

    async def create_system_design(self, prd: dict):
        system_design = await self.doc_generator.generate_system_design(prd)
        self.doc_generator.save_document(system_design, "system_design")  # Removed 'await' here
        return system_design

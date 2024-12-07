# roles/product_manager.py
from utils.code_parser import CodeParser
from utils.document_generator import DocumentGenerator

class ProductManager:
    def __init__(self, code_parser: 'CodeParser', doc_generator: 'DocumentGenerator'):
        self.code_parser = code_parser
        self.doc_generator = doc_generator

    async def create_prd(self):
        code_symbols = self.code_parser.extract_symbols()
        project_type = self.code_parser.project_type
        code_summary = f"Project Type: {project_type}\n\n"
        for file, symbols in code_symbols.items():
            code_summary += f"File: {file}\n"
            for symbol in symbols:
                code_summary += f"  - {symbol}\n"
            code_summary += "\n"
        print(f"code_summary {code_summary}")
        return 0
        # Generate PRD using the code summary
        prd = await self.doc_generator.generate_prd(code_summary)
        self.doc_generator.save_document(prd, "prd")  # Removed 'await' here
        return prd

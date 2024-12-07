# utils/docstring_generator.py

import asyncio
from typing import Dict, List, Union
class DocstringGenerator:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    async def generate_docstrings(self, items: List[Dict]):
        tasks = []
        for item in items:
            tasks.append(self.generate_docstring(item))
        results = await asyncio.gather(*tasks)
        return results

    async def generate_docstring(self, item: Dict):
        code_snippet = item['code']
        name = item['name']
        item_type = item['type']
        word_limit = 40  # Adjust based on your preference
        prompt = f"""Generate a concise docstring for the following {item_type} named '{name}'. Limit the docstring to approximately {word_limit} words.

Code:
{code_snippet}

Docstring:"""
        try:
            response_text, _ = await self.llm_client.ask_with_retry(prompt)
            docstring = response_text.strip().strip('"""')
            item['generated_docstring'] = docstring
            return item
        except Exception as e:
            print(f"Failed to generate docstring for {name}: {e}")
            return item

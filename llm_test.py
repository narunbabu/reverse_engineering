# import pytest
# import asyncio
# from utils.llm_client import LLMClient
# from configs.llm_config import LLMConfig

# @pytest.mark.asyncio
# async def test_llm_client_anthropic():
#     config = LLMConfig(api_type='anthropic')
#     async with LLMClient(config) as client:
#         response, usage = await client.ask("Test prompt for Anthropic.")
#         assert isinstance(response, str)
#         assert isinstance(usage, dict)

# @pytest.mark.asyncio
# async def test_llm_client_ollama():
#     config = LLMConfig(api_type='ollama')
#     async with LLMClient(config) as client:
#         response, usage = await client.ask("Test prompt for Ollama.")
#         assert isinstance(response, str)
#         assert isinstance(usage, dict)

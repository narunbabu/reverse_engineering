# tests/test_ollama_client.py

import pytest
from unittest.mock import AsyncMock, patch
from configs.llm_config import LLMConfig
from llm_clients.ollama_client import OllamaLLM, OllamaAPIError

@pytest.mark.asyncio
async def test_ollama_llm_ask_success():
    # Arrange
    config = LLMConfig.get('ollama')
    prompt = "Hello, Ollama!"
    expected_response = "Hi there!"
    expected_usage = {
        "input_tokens": 3,
        "output_tokens": 2,
        "total_tokens": 5
    }

    # Mock the aiohttp session and response
    with patch('llm_clients.ollama_client.aiohttp.ClientSession') as MockSession:
        mock_session = AsyncMock()
        MockSession.return_value = mock_session
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"response": expected_response, "usage": expected_usage})
        mock_session.post.return_value.__aenter__.return_value = mock_response

        # Act
        async with OllamaLLM(config) as client:
            response, usage = await client.ask(prompt)

        # Assert
        assert response == expected_response
        assert usage == expected_usage

@pytest.mark.asyncio
async def test_ollama_llm_api_error():
    # Arrange
    config = LLMConfig.get('ollama')
    prompt = "Hello, Ollama!"

    # Mock the aiohttp session to return an error status
    with patch('llm_clients.ollama_client.aiohttp.ClientSession') as MockSession:
        mock_session = AsyncMock()
        MockSession.return_value = mock_session
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")
        mock_session.post.return_value.__aenter__.return_value = mock_response

        # Act & Assert
        async with OllamaLLM(config) as client:
            with pytest.raises(OllamaAPIError) as exc_info:
                await client.ask(prompt)

            assert "Ollama API error" in str(exc_info.value)

# tests/test_llm_client.py

import pytest
from unittest.mock import AsyncMock, patch
from configs.llm_config import LLMConfig
from utils.llm_client import LLMClient, LLMType
from llm_clients.anthropic_client import AnthropicLLM, AnthropicAPIError
from llm_clients.ollama_client import OllamaLLM, OllamaAPIError

@pytest.mark.asyncio
async def test_llm_client_anthropic_ask_success():
    # Arrange
    config = LLMConfig.get('anthropic')
    prompt = "Hello, Anthropic!"
    expected_response = "Hi there!"
    expected_usage = {
        "input_tokens": 3,
        "output_tokens": 2,
        "total_tokens": 5
    }

    with patch('llm_clients.anthropic_client.AnthropicLLM.ask') as mock_ask:
        mock_ask.return_value = (expected_response, expected_usage)

        # Act
        async with LLMClient(config) as client:
            response, usage = await client.ask(prompt)

        # Assert
        assert response == expected_response
        assert usage == expected_usage

@pytest.mark.asyncio
async def test_llm_client_ollama_ask_success():
    # Arrange
    config = LLMConfig.get('ollama')
    prompt = "Hello, Ollama!"
    expected_response = "Hi there!"
    expected_usage = {
        "input_tokens": 3,
        "output_tokens": 2,
        "total_tokens": 5
    }

    with patch('llm_clients.ollama_client.OllamaLLM.ask') as mock_ask:
        mock_ask.return_value = (expected_response, expected_usage)

        # Act
        async with LLMClient(config) as client:
            response, usage = await client.ask(prompt)

        # Assert
        assert response == expected_response
        assert usage == expected_usage

@pytest.mark.asyncio
async def test_llm_client_unsupported_llm_type():
    # Arrange
    config = LLMConfig(
        api_type="unsupported_llm",
        api_key="test-key",
        api_base_url="https://unsupported.com",
        model="test-model"
    )

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        LLMClient(config)
    
    assert "Unsupported LLM type" in str(exc_info.value)

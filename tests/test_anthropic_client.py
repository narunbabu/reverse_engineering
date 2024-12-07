# tests/test_anthropic_client.py

import pytest
from unittest.mock import AsyncMock, patch
from configs.llm_config import LLMConfig
from llm_clients.anthropic_client import AnthropicLLM, AnthropicAPIError
from utils.config import ANTHROPIC_API  # Ensure this path is correct
@pytest.mark.asyncio
async def test_anthropic_llm_ask_success():
    # Arrange
    config = LLMConfig.get('anthropic')
    # config.api_key = ANTHROPIC_API
    # config.api_base_url = "https://api.anthropic.com"
    # config.model = "test-model"
    prompt = "Hello, how are you?"

    expected_response = "I'm fine, thank you!"
    expected_usage = {
        "input_tokens": 5,
        "output_tokens": 5,
        "total_tokens": 10
    }

    # Mock the Anthropich client
    with patch('llm_clients.anthropic_client.anthropic.AsyncAnthropic') as MockAnthropic:
        mock_client = AsyncMock()
        MockAnthropic.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.completion = expected_response
        mock_response.__aiter__.return_value = iter([{"completion": expected_response}])
        mock_client.completions.create = AsyncMock(return_value=mock_response)

        # Act
        async with AnthropicLLM(config) as client:
            response, usage = await client.ask(prompt)

        # Assert
        assert response == expected_response
        assert usage['input_tokens'] == expected_usage['input_tokens']
        assert usage['output_tokens'] == expected_usage['output_tokens']
        assert usage['total_tokens'] == expected_usage['total_tokens']

@pytest.mark.asyncio
async def test_anthropic_llm_api_error():
    # Arrange
    config = LLMConfig.get('anthropic')
    config.api_key = "test-api-key"
    config.api_base_url = "https://api.anthropic.com"
    config.model = "test-model"
    prompt = "Hello, how are you?"

    # Mock the Anthropich client to raise APIError
    with patch('llm_clients.anthropic_client.anthropic.AsyncAnthropic') as MockAnthropic:
        mock_client = AsyncMock()
        MockAnthropic.return_value = mock_client
        mock_client.completions.create.side_effect = anthropic.APIError("Overloaded", code='overloaded_error')

        # Act & Assert
        async with AnthropicLLM(config) as client:
            with pytest.raises(AnthropicAPIError) as exc_info:
                await client.ask_with_retry(prompt)

            assert "Anthropic API error" in str(exc_info.value)

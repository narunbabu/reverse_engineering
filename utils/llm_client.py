# utils/llm_client.py

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple
import json
import logging

from configs.llm_config import LLMConfig

# Import your Ollama and Anthropic clients here
from llm_clients.ollama_client import OllamaLLM
from llm_clients.anthropic_client import AnthropicLLM
from llm_clients.openai_client import OpenAILLM


class LLMType(Enum):
    ANTHROPIC = 'anthropic'
    OLLAMA = 'ollama'
    OPENAI = 'openai'

class LLMClient:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.llm: Optional[object] = None  # Initialize as None
        self.llm_type: Optional[LLMType] = None

        # Determine LLM type based on the config
        if self.config.api_type == 'anthropic':
            self.llm_type = LLMType.ANTHROPIC
        elif self.config.api_type == 'openai':
            self.llm_type = LLMType.OPENAI
        elif self.config.api_type == 'ollama':
            self.llm_type = LLMType.OLLAMA
        else:
            raise ValueError(f"Unsupported LLM type: {self.config.api_type}")

        # Handle streaming flag if present
        self.stream = self.config.stream if hasattr(self.config, 'stream') else False

    async def __aenter__(self):
        if self.llm_type == LLMType.ANTHROPIC:
            self.llm = AnthropicLLM(self.config)
        elif self.llm_type == LLMType.OPENAI:
            self.llm = OpenAILLM(self.config)
        elif self.llm_type == LLMType.OLLAMA:
            self.llm = OllamaLLM(self.config)
        else:
            raise ValueError(f"Unsupported LLM type: {self.llm_type}")

        # Initialize the LLM client within its context
        await self.llm.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.llm:
            await self.llm.__aexit__(exc_type, exc_value, traceback)

    async def ask(self, prompt: str) -> Tuple[str, dict]:
        """
        Send a prompt to the selected LLM and receive the response along with token usage.

        Args:
            prompt (str): The user prompt.

        Returns:
            tuple: (response_text, usage_dict)
        """
        if not self.llm:
            raise RuntimeError("LLMClient is not initialized. Use 'async with' to initialize it.")

        return await self.llm.ask(prompt)

    async def ask_with_retry(self, prompt: str, max_retries: int = 3, initial_delay: float = 1.0) -> Tuple[str, dict]:
        """
        Send a prompt with automatic retry mechanism for overloaded errors.

        Args:
            prompt (str): The user prompt.
            max_retries (int): Maximum number of retry attempts.
            initial_delay (float): Initial delay between retries in seconds.

        Returns:
            tuple: (response_text, usage_dict)
        """
        if not self.llm:
            raise RuntimeError("LLMClient is not initialized. Use 'async with' to initialize it.")

        return await self.llm.ask_with_retry(prompt, max_retries, initial_delay)

    async def count_tokens(self, messages: list, system: Optional[str] = None) -> int:
        """
        Count tokens using the underlying LLM's token counting method.

        Args:
            messages (list): List of message dictionaries.
            system (str, optional): System prompt.

        Returns:
            int: Number of tokens.
        """
        if not self.llm:
            raise RuntimeError("LLMClient is not initialized. Use 'async with' to initialize it.")

        return await self.llm.count_tokens(messages, system)

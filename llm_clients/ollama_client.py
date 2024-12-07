# llm_clients/ollama_client.py

import asyncio
import json
import aiohttp
from configs.llm_config import LLMConfig
from datetime import datetime
import re
import logging
import tiktoken  

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Adjust the level as needed
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class OllamaAPIError(Exception):
    """Custom exception for Ollama API errors."""
    def __init__(self, status, message):
        super().__init__(f"Ollama API error: {status} - {message}")
        self.status = status
        self.message = message

class OllamaLLM:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.base_url = config.api_base_url.rstrip('/')
        self.model = config.model
        self.stream = config.stream
        self.session = None  # Will be initialized in __aenter__

        logger.info(f"OllamaLLM initialized with base URL: {self.base_url}, Model: {self.model}")

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.session:
            await self.session.close()
            # logger.info("Ollama client session closed.")

    async def ask(self, prompt: str) -> tuple:
        """
        Send a prompt to Ollama and receive the response along with token usage.

        Args:
            prompt (str): The user prompt.

        Returns:
            tuple: (response_text, usage_dict)
        """
        url = f"{self.base_url}/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "options": {
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "stream": self.stream
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            if self.stream:
                response_text, usage = await self._stream_request(url, payload, headers)
            else:
                response_text, usage = await self._standard_request(url, payload, headers)

            return response_text, usage

        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            raise OllamaAPIError(-1, f"Network error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise OllamaAPIError(-1, f"Unexpected error: {e}") from e

    async def _standard_request(self, url, payload, headers):
        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Ollama API error: {response.status} - {error_text}")
                raise OllamaAPIError(response.status, error_text)

            data = await response.json()
            response_text = data.get("response", "")
            usage = data.get("usage", {})
            return response_text, usage

    async def _stream_request(self, url, payload, headers):
        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Ollama API error: {response.status} - {error_text}")
                raise OllamaAPIError(response.status, error_text)

            collected_content = []
            input_tokens = await self.count_tokens(payload['prompt'])
            total_output_tokens = 0
            usage = {"input_tokens": input_tokens, "output_tokens": 0, "total_tokens": input_tokens}

            async for line in response.content:
                if line:
                    line = line.decode('utf-8').strip()
                    if line:
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                collected_content.append(data["response"])
                                total_output_tokens += await self.count_tokens(data["response"])
                            if "usage" in data:
                                usage = data["usage"]
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to decode JSON line: {line}")
                            continue

            if "usage" not in usage:
                # If usage wasn't provided by the API, calculate it
                usage = {
                    "input_tokens": input_tokens,
                    "output_tokens": total_output_tokens,
                    "total_tokens": input_tokens + total_output_tokens
                }

            response_text = ''.join(collected_content)
            return response_text, usage

    async def ask_with_retry(self, prompt: str, max_retries: int = 3, initial_delay: float = 1.0) -> tuple:
        attempt = 0
        delay = initial_delay
        while attempt < max_retries:
            try:
                return await self.ask(prompt)
            except OllamaAPIError as e:
                if e.status in [429, 500, 502, 503, 504]:  # Retriable status codes
                    logger.warning(f"Ollama API is overloaded or server error. Retrying in {delay} seconds... (Attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                    attempt += 1
                    delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Non-retriable Ollama API error: {e}")
                    raise e
        raise Exception("Max retries exceeded for Ollama API.")

    async def count_tokens(self, text: str) -> int:
        encoding = tiktoken.get_encoding("cl100k_base")  # Replace with appropriate encoding
        tokens = encoding.encode(text)
        return len(tokens)

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Ollama client session closed via close method.")


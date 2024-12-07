# llm_clients/anthropic_client.py

import asyncio
import anthropic
from configs.llm_config import LLMConfig
from dataclasses import dataclass
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logs
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

@dataclass
class Usage:
    input_tokens: int
    output_tokens: int

class AnthropicLLM:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None  # Will be initialized in __aenter__
        self.model = self.config.model
        self.api_key = self.config.api_key
        self.api_url = self.config.api_base_url
        logger.info(f"AnthropicLLM initialized with model: {self.model}")

    async def __aenter__(self):
        # Initialize the asynchronous client
        try:
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key, base_url=self.api_url)
            logger.info("Anthropic client session started.")
        except AttributeError:
            logger.error("Failed to initialize AsyncAnthropic. Please verify the Anthropic SDK version and client class name.")
            raise
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
        # logger.info("Anthropic client session closed.")

    async def ask(self, prompt: str) -> tuple:
        """
        Send a prompt to Anthropic using the Messages API and receive the response along with token usage.

        Args:
            prompt (str): The user prompt.

        Returns:
            tuple: (response_text, usage_dict)
        """
        messages = [{"role": "user", "content": prompt}]
        # No need for manual token counting as usage is provided

        try:
            # logger.debug(f"Sending prompt to Anthropic: {prompt}")

            # Send the messages to Anthropic
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.config.max_tokens,
                messages=messages,
                temperature=self.config.temperature,
                stream=self.config.stream
            )

            if self.config.stream:
                # Handle streaming response
                response_text = ""
                async for chunk in response:
                    if hasattr(chunk, 'content'):
                        for content_block in chunk.content:
                            if content_block.type == 'text':
                                chunk_text = content_block.text
                                response_text += chunk_text
                                # print(chunk_text, end='', flush=True)  # Optional: Stream to console
                # print()  # Newline after streaming
            else:
                # Handle non-streaming response
                response_text = ''.join([block.text for block in response.content if block.type == 'text'])

            logger.debug(f"Received response from Anthropic: {response_text}")

            # Extract usage statistics directly from the response
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }

            return response_text.strip(), usage

        except anthropic.AnthropicError as e:
            logger.error(f"Anthropic API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    async def ask_with_retry(self, prompt: str, max_retries: int = 3, initial_delay: float = 1.0) -> tuple:
        """
        Send a prompt with automatic retry mechanism for overloaded errors.

        Args:
            prompt (str): The user prompt.
            max_retries (int): Maximum number of retry attempts.
            initial_delay (float): Initial delay between retries in seconds.

        Returns:
            tuple: (response_text, usage_dict)
        """
        attempt = 0
        delay = initial_delay

        while attempt < max_retries:
            try:
                return await self.ask(prompt)
            except anthropic.AnthropicError as e:
                if hasattr(e, 'status_code') and e.status_code == 429:
                    logger.warning(f"Anthropic API is overloaded. Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    attempt += 1
                    delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Non-retriable Anthropic API error: {e}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error during ask_with_retry: {e}")
                raise
        raise Exception("Max retries exceeded for Anthropic API.")

    async def close(self):
        """
        Close the Anthropic client session.
        """
        if self.client:
            try:
                await self.client.close()
                # logger.info("Anthropic client session closed via close method.")
            except AttributeError:
                logger.error("Failed to close Anthropic client. The client may not support asynchronous closing.")

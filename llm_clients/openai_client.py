import asyncio
import openai
from configs.llm_config import LLMConfig
from dataclasses import dataclass
import logging
from openai import APIConnectionError, AsyncOpenAI, AsyncStream
from openai._base_client import AsyncHttpxClientWrapper
from openai.types import CompletionUsage
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from tenacity import (
    after_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)


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

class OpenAILLM:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None  # Will be initialized in __aenter__
        self.model = self.config.model
        self.api_key = self.config.api_key
        self.api_url = self.config.api_base_url
        logger.info(f"OpenAILLM initialized with model: {self.model}")

    async def __aenter__(self):
        # Initialize the asynchronous client
        try:
            openai.api_key = self.api_key
            openai.api_base = self.api_url
            logger.info("OpenAI client session started.")
            kwargs = self._make_client_kwargs()
            self.aclient = AsyncOpenAI(**kwargs)
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def ask(self, prompt: str) -> tuple:
        """
        Send a prompt to OpenAI using the chat API and receive the response along with token usage.

        Args:
            prompt (str): The user prompt.

        Returns:
            tuple: (response_text, usage_dict)
        """
        try:
            # Prepare the messages for the OpenAI API
            messages = [{"role": "user", "content": prompt}]
            response = await self.aclient.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )

            response_text = response.choices[0].message.content

            print(f"response_text: {response_text}")
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens":  response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            print(f"Usage: {usage}")

            return response_text.strip(), usage

        except APIConnectionError as e:
            logger.error(f"OpenAI API error: {e}")
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
            except APIConnectionError:
                logger.warning(f"OpenAI API is overloaded. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                attempt += 1
                delay *= 2  # Exponential backoff
            except Exception as e:
                logger.error(f"Unexpected error during ask_with_retry: {e}")
                raise
        raise Exception("Max retries exceeded for OpenAI API.")
    def _make_client_kwargs(self) -> dict:
        kwargs = {"api_key": self.config.api_key, "base_url": self.config.api_base_url}

        # to use proxy, openai v1 needs http_client
        if proxy_params := self._get_proxy_params():
            kwargs["http_client"] = AsyncHttpxClientWrapper(**proxy_params)

        return kwargs

    def _get_proxy_params(self) -> dict:
        params = {}
        if self.config.proxy:
            params = {"proxies": self.config.proxy}
            if self.config.api_base_url:
                params["base_url"] = self.config.api_base_url

        return params
    async def close(self):
        """
        Close the OpenAI client session properly.
        """
        if self.aclient:
            try:
                # Attempt to call 'close' if 'aclose' is unavailable
                if hasattr(self.aclient, 'aclose'):
                    await self.aclient.aclose()
                    logger.info("OpenAI client session closed using 'aclose'.")
                elif hasattr(self.aclient, 'close'):
                    await self.aclient.close()
                    logger.info("OpenAI client session closed using 'close'.")
                else:
                    logger.warning("AsyncOpenAI client does not have 'aclose' or 'close' methods.")
            except Exception as e:
                logger.error(f"Error while closing OpenAI client: {e}")
        else:
            logger.info("OpenAI client was not initialized or already closed.")


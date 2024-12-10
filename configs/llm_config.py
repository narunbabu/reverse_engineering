
# utils/llm_config.py

from dataclasses import dataclass
from typing import Optional
from utils.config import ANTHROPIC_API, OPENAI_API  # Ensure this path is correct

@dataclass
class LLMConfig:
    """
    Unified configuration class for different Large Language Models (LLMs).
    """
    # Common configuration parameters
    temperature: float = 0.7
    max_tokens: int = 1024  # Adjusted to match your usage example
    model: str = "claude-3-5-sonnet-20241022"  # Updated to use Messages API supported model
    api_base_url: str = "https://api.anthropic.com"
    
    # Specific parameters (optional)
    api_key: Optional[str] = None
    api_type: Optional[str] = None
    stream: Optional[bool] = False
    proxy: Optional[str] = None

    @classmethod
    def get(cls, llm_type: str) -> 'LLMConfig':
        """
        Factory method to retrieve specific LLM configurations based on the llm_type.

        Args:
            llm_type (str): The type of LLM ('anthropic' or 'ollama').

        Returns:
            LLMConfig: An instance of LLMConfig with parameters set for the specified LLM.

        Raises:
            ValueError: If an unsupported llm_type is provided.
        """
        llm_type = llm_type.lower()
        if llm_type == 'anthropic':
            return cls(
                api_key=ANTHROPIC_API,
                api_base_url="https://api.anthropic.com",
                model="claude-3-5-sonnet-20241022",  # Use a supported model
                temperature=0.7,
                max_tokens=  1024,
                api_type="anthropic",
                stream=False  # Adjust based on your needs
            )
        elif llm_type == 'openai':
            return cls(
                api_type="openai",
                api_key=OPENAI_API,
                api_base_url="https://api.openai.com/v1",
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=1024,
                stream=True  # Enable streaming for Ollama if supported
            )
        elif llm_type == 'ollama':
            return cls(
                api_type='ollama',
                api_base_url='http://localhost:11434/api',
                # model="qwen2.5-coder:14b",
                model="qwen2.5-coder:14b",
                temperature=0.7,
                max_tokens=1024,
                stream=True  # Enable streaming for Ollama if supported
            )
        elif llm_type == 'ollama_qwen_7b':
            return cls(
                api_type='ollama',
                api_base_url='http://localhost:11434/api',
                # model="qwen2.5-coder:14b",
                model="qwen2.5-coder:7b",
                temperature=0.4,
                max_tokens=1024,
                stream=True  # Enable streaming for Ollama if supported
            )
        elif llm_type == 'ollama_llama_3.1_7b':
            return cls(
                api_type='ollama',
                api_base_url='http://localhost:11434/api',
                # model="qwen2.5-coder:14b",
                model="llama3.1:latest",
                temperature=0.4,
                max_tokens=1024,
                stream=True  # Enable streaming for Ollama if supported
            )
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")

    def __post_init__(self):
        """
        Post-initialization processing to validate fields.
        """
        if self.api_type not in ['anthropic', 'ollama','openai']:
            raise ValueError('api_type must be either "anthropic" or "ollama".')
 
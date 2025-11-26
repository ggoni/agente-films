"""LiteLLM client service for multi-model LLM support."""

import logging
from typing import Any

import httpx
from litellm import completion

from backend.app.config import Settings

logger = logging.getLogger(__name__)


class LiteLLMClient:
    """
    Client for interacting with LiteLLM proxy for multi-model support.

    Provides unified interface to multiple LLM providers (OpenAI, Anthropic, Google)
    through LiteLLM proxy with automatic retries and error handling.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        """
        Initialize LiteLLM client.

        Args:
            settings: Application settings (uses defaults if not provided)
        """
        self.settings = settings or Settings()
        self.base_url = self.settings.LITELLM_BASE_URL
        self.api_key = self.settings.LITELLM_API_KEY
        self.default_model = self.settings.MODEL

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate chat completion using specified model.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name from LiteLLM config (defaults to settings.MODEL)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional model-specific parameters

        Returns:
            Response dict with completion text and metadata

        Example:
            >>> client = LiteLLMClient()
            >>> messages = [{"role": "user", "content": "Hello!"}]
            >>> response = await client.chat_completion(messages)
            >>> print(response["content"])
        """
        model_name = model or self.default_model

        logger.info(f"Requesting completion from model: {model_name}")

        try:
            response = await completion(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                api_base=self.base_url,
                **kwargs,
            )

            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

            logger.info(
                f"Completion successful. Tokens used: {usage['total_tokens']}"
            )

            return {
                "content": content,
                "model": model_name,
                "usage": usage,
                "finish_reason": response.choices[0].finish_reason,
            }

        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            raise

    async def stream_chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> Any:
        """
        Generate streaming chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name from LiteLLM config
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters

        Yields:
            Response chunks as they arrive

        Example:
            >>> client = LiteLLMClient()
            >>> messages = [{"role": "user", "content": "Tell a story"}]
            >>> async for chunk in client.stream_chat_completion(messages):
            ...     print(chunk, end="")
        """
        model_name = model or self.default_model

        logger.info(f"Starting streaming completion from model: {model_name}")

        try:
            response = await completion(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                api_base=self.base_url,
                **kwargs,
            )

            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error in streaming completion: {e}")
            raise

    async def list_models(self) -> list[str]:
        """
        List available models from LiteLLM proxy.

        Returns:
            List of available model names

        Example:
            >>> client = LiteLLMClient()
            >>> models = await client.list_models()
            >>> print(models)
            ['gemini-2.5-flash', 'gpt-4', 'claude-3-5-sonnet']
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/model/info",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                response.raise_for_status()
                data = response.json()
                models = [model["model_name"] for model in data.get("data", [])]
                logger.info(f"Available models: {models}")
                return models

        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

    async def health_check(self) -> bool:
        """
        Check if LiteLLM proxy is healthy.

        Returns:
            True if proxy is responding, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200

        except Exception as e:
            logger.error(f"LiteLLM proxy health check failed: {e}")
            return False

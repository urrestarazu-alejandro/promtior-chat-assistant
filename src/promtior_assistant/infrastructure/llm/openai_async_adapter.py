"""OpenAI LLM async adapter implementation."""

from typing import Any

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


class OpenAIAsyncAdapter:
    """Async adapter for OpenAI LLM provider.

    Implements LLMPort interface for OpenAI models.
    Supports async context manager protocol for resource management.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
    ):
        """Initialize OpenAI async adapter.

        Args:
            api_key: OpenAI API key
            model: Model identifier
            temperature: Default sampling temperature
        """
        self._client = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=temperature,
        )
        self._model = model
        self._temperature = temperature

    async def __aenter__(self) -> "OpenAIAsyncAdapter":
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager and cleanup resources."""
        self._client = None

    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate text from prompt using OpenAI.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        response = await self._client.ainvoke([HumanMessage(content=prompt)])
        return response.content

    @property
    def model_name(self) -> str:
        """Get model name."""
        return self._model

"""Ollama LLM async adapter implementation."""

import os
from typing import Any

import httpx

from ...config import settings


class OllamaAsyncAdapter:
    """Async adapter for Ollama LLM provider.

    Implements LLMPort interface for Ollama models using async HTTP client.
    Supports async context manager protocol for resource management.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama2",
        temperature: float = 0.7,
    ):
        """Initialize Ollama async adapter.

        Args:
            base_url: Ollama base URL
            model: Model identifier
            temperature: Default sampling temperature
        """
        self._base_url = base_url
        self._model = model
        self._temperature = temperature
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "OllamaAsyncAdapter":
        """Enter async context manager."""
        self._client = httpx.AsyncClient(timeout=120.0)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager and cleanup resources."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_headers(self) -> dict[str, str]:
        """Get authorization headers if using remote Ollama."""
        is_remote = "localhost" not in self._base_url and "127.0.0.1" not in self._base_url
        headers = {}

        if is_remote:
            api_key = (
                settings.ollama_api_key
                or os.getenv("OLLAMA_API_KEY")
                or os.getenv("OLLAMA_AUTH_TOKEN")
            )
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

        return headers

    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate text from prompt using Ollama.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        if self._client:
            return await self._generate_with_client(self._client, prompt, temperature)

        async with httpx.AsyncClient(timeout=120.0) as client:
            return await self._generate_with_client(client, prompt, temperature)

    async def _generate_with_client(
        self, client: httpx.AsyncClient, prompt: str, temperature: float
    ) -> str:
        """Generate text using provided HTTP client."""
        response = await client.post(
            f"{self._base_url}/api/chat",
            json={
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "temperature": temperature or self._temperature,
            },
            headers=self._get_headers(),
        )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

        result = response.json()
        return result["message"]["content"]

    @property
    def model_name(self) -> str:
        """Get model name."""
        return self._model

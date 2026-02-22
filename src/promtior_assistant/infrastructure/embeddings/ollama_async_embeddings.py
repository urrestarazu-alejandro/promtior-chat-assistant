"""Ollama embeddings async adapter implementation."""

import os

import httpx

from ...config import settings


class OllamaEmbeddingsAsyncAdapter:
    """Async adapter for Ollama embeddings.

    Implements EmbeddingsPort interface using async HTTP client.
    """

    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://localhost:11434",
    ):
        """Initialize Ollama embeddings async adapter.

        Args:
            model: Embedding model identifier
            base_url: Ollama base URL
        """
        self._model = model
        self._base_url = base_url

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

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple documents.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self._base_url}/api/embed",
                json={"model": self._model, "input": texts},
                headers=self._get_headers(),
            )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

        result = response.json()
        return result.get("embeddings", [])

    async def embed_query(self, text: str) -> list[float]:
        """Embed a single query.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self._base_url}/api/embed",
                json={"model": self._model, "input": text},
                headers=self._get_headers(),
            )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

        result = response.json()
        embeddings = result.get("embeddings", [[]])
        return embeddings[0] if embeddings else []

    @property
    def model_name(self) -> str:
        """Get embeddings model name."""
        return self._model

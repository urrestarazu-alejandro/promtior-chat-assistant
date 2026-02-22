"""Ollama embeddings adapter implementation."""

import os

import httpx
from langchain_core.embeddings import Embeddings
from pydantic import ConfigDict

from ...config import settings


class CustomOllamaEmbeddings(Embeddings):
    """Custom OllamaEmbeddings implementation that supports API key authentication."""

    model_config = ConfigDict(extra="ignore")

    def __init__(self, model: str = "nomic-embed-text", base_url: str = "https://ollama.com"):
        super().__init__()
        self.model = model
        self.base_url = base_url

    def _get_headers(self) -> dict[str, str]:
        """Get authorization headers if using remote Ollama."""
        is_remote = "localhost" not in self.base_url and "127.0.0.1" not in self.base_url
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

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple documents.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings
        """
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model, "input": texts},
                headers=self._get_headers(),
            )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

        result = response.json()
        return result.get("embeddings", [])

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model, "input": text},
                headers=self._get_headers(),
            )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

        result = response.json()
        embeddings = result.get("embeddings", [[]])
        return embeddings[0] if embeddings else []

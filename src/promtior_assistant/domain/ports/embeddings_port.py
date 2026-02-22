"""Port (interface) for embeddings providers."""

from typing import Protocol


class EmbeddingsPort(Protocol):
    """Port for text embeddings providers.

    This interface defines the contract for embedding services.
    """

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple documents.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        ...

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        ...

    @property
    def model_name(self) -> str:
        """Get the embeddings model name.

        Returns:
            Model identifier
        """
        ...

"""Embedding metadata model for tracking vector store configuration."""

from enum import Enum


class EmbeddingProvider(str, Enum):
    """Supported embedding providers."""

    OLLAMA = "ollama"
    OPENAI = "openai"


class EmbeddingMetadata:
    """Metadata about embeddings used in vector store.

    This class tracks which embedding provider and model were used
    to create the vector store, enabling automatic validation and
    preventing dimension mismatches.
    """

    def __init__(
        self,
        provider: EmbeddingProvider | str,
        model: str,
        dimension: int,
    ):
        """Initialize embedding metadata.

        Args:
            provider: Embedding provider (ollama or openai)
            model: Model name
            dimension: Embedding dimension
        """
        self.provider = EmbeddingProvider(provider) if isinstance(provider, str) else provider
        self.model = model
        self.dimension = dimension

    @classmethod
    def from_ollama(cls, model: str) -> "EmbeddingMetadata":
        """Create metadata for Ollama embeddings.

        Args:
            model: Ollama model name

        Returns:
            EmbeddingMetadata instance
        """
        return cls(
            provider=EmbeddingProvider.OLLAMA,
            model=model,
            dimension=768,
        )

    @classmethod
    def from_openai(cls, model: str) -> "EmbeddingMetadata":
        """Create metadata for OpenAI embeddings.

        Args:
            model: OpenAI model name

        Returns:
            EmbeddingMetadata instance
        """
        dimension_map = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        dimension = dimension_map.get(model, 1536)

        return cls(
            provider=EmbeddingProvider.OPENAI,
            model=model,
            dimension=dimension,
        )

    def matches(self, other: "EmbeddingMetadata") -> bool:
        """Check if metadata matches another.

        Args:
            other: Other metadata to compare

        Returns:
            True if provider and dimension match
        """
        return self.provider == other.provider and self.dimension == other.dimension

    def to_dict(self) -> dict[str, str | int]:
        """Convert to dictionary for storage.

        Returns:
            Dictionary representation
        """
        return {
            "embedding_provider": self.provider.value,
            "embedding_model": self.model,
            "embedding_dimension": self.dimension,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | int]) -> "EmbeddingMetadata":
        """Create from dictionary.

        Args:
            data: Dictionary with metadata

        Returns:
            EmbeddingMetadata instance
        """
        return cls(
            provider=str(data["embedding_provider"]),
            model=str(data["embedding_model"]),
            dimension=int(data["embedding_dimension"]),
        )

    def __repr__(self) -> str:
        """String representation."""
        return f"EmbeddingMetadata(provider={self.provider.value}, model={self.model}, dim={self.dimension})"

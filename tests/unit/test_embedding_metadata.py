"""Tests for EmbeddingMetadata model."""

import pytest

from src.promtior_assistant.domain.exceptions import EmbeddingMismatchError
from src.promtior_assistant.domain.models.embedding_metadata import (
    EmbeddingMetadata,
    EmbeddingProvider,
)


class TestEmbeddingMetadata:
    """Tests for EmbeddingMetadata class."""

    def test_from_ollama(self):
        """Test creating metadata for Ollama embeddings."""
        metadata = EmbeddingMetadata.from_ollama("nomic-embed-text")

        assert metadata.provider == EmbeddingProvider.OLLAMA
        assert metadata.model == "nomic-embed-text"
        assert metadata.dimension == 768

    def test_from_openai_small(self):
        """Test creating metadata for OpenAI small embeddings."""
        metadata = EmbeddingMetadata.from_openai("text-embedding-3-small")

        assert metadata.provider == EmbeddingProvider.OPENAI
        assert metadata.model == "text-embedding-3-small"
        assert metadata.dimension == 1536

    def test_from_openai_large(self):
        """Test creating metadata for OpenAI large embeddings."""
        metadata = EmbeddingMetadata.from_openai("text-embedding-3-large")

        assert metadata.provider == EmbeddingProvider.OPENAI
        assert metadata.model == "text-embedding-3-large"
        assert metadata.dimension == 3072

    def test_from_openai_ada(self):
        """Test creating metadata for OpenAI ada embeddings."""
        metadata = EmbeddingMetadata.from_openai("text-embedding-ada-002")

        assert metadata.provider == EmbeddingProvider.OPENAI
        assert metadata.model == "text-embedding-ada-002"
        assert metadata.dimension == 1536

    def test_from_openai_unknown_defaults_to_1536(self):
        """Test unknown OpenAI model defaults to 1536 dimensions."""
        metadata = EmbeddingMetadata.from_openai("unknown-model")

        assert metadata.provider == EmbeddingProvider.OPENAI
        assert metadata.model == "unknown-model"
        assert metadata.dimension == 1536

    def test_matches_same_provider_and_dimension(self):
        """Test matching metadata with same provider and dimension."""
        metadata1 = EmbeddingMetadata.from_ollama("model1")
        metadata2 = EmbeddingMetadata.from_ollama("model2")

        assert metadata1.matches(metadata2)

    def test_matches_different_provider(self):
        """Test non-matching metadata with different provider."""
        ollama_metadata = EmbeddingMetadata.from_ollama("nomic-embed-text")
        openai_metadata = EmbeddingMetadata.from_openai("text-embedding-3-small")

        assert not ollama_metadata.matches(openai_metadata)

    def test_matches_different_dimension(self):
        """Test non-matching metadata with different dimensions."""
        small_metadata = EmbeddingMetadata.from_openai("text-embedding-3-small")
        large_metadata = EmbeddingMetadata.from_openai("text-embedding-3-large")

        assert not small_metadata.matches(large_metadata)

    def test_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = EmbeddingMetadata.from_ollama("nomic-embed-text")
        data = metadata.to_dict()

        assert data["embedding_provider"] == "ollama"
        assert data["embedding_model"] == "nomic-embed-text"
        assert data["embedding_dimension"] == 768

    def test_from_dict(self):
        """Test creating metadata from dictionary."""
        data = {
            "embedding_provider": "openai",
            "embedding_model": "text-embedding-3-small",
            "embedding_dimension": 1536,
        }
        metadata = EmbeddingMetadata.from_dict(data)

        assert metadata.provider == EmbeddingProvider.OPENAI
        assert metadata.model == "text-embedding-3-small"
        assert metadata.dimension == 1536

    def test_repr(self):
        """Test string representation."""
        metadata = EmbeddingMetadata.from_ollama("nomic-embed-text")
        repr_str = repr(metadata)

        assert "ollama" in repr_str
        assert "nomic-embed-text" in repr_str
        assert "768" in repr_str


class TestEmbeddingMismatchError:
    """Tests for EmbeddingMismatchError exception."""

    def test_error_message_includes_details(self):
        """Test error message includes all relevant details."""
        error = EmbeddingMismatchError(
            expected_provider="ollama",
            expected_model="nomic-embed-text",
            expected_dimension=768,
            actual_provider="openai",
            actual_model="text-embedding-3-small",
            actual_dimension=1536,
        )

        error_msg = str(error)
        assert "ollama" in error_msg
        assert "nomic-embed-text" in error_msg
        assert "768" in error_msg
        assert "openai" in error_msg
        assert "text-embedding-3-small" in error_msg
        assert "1536" in error_msg
        assert "re-ingest" in error_msg.lower()

    def test_error_attributes(self):
        """Test error has all expected attributes."""
        error = EmbeddingMismatchError(
            expected_provider="ollama",
            expected_model="nomic-embed-text",
            expected_dimension=768,
            actual_provider="openai",
            actual_model="text-embedding-3-small",
            actual_dimension=1536,
        )

        assert error.expected_provider == "ollama"
        assert error.expected_model == "nomic-embed-text"
        assert error.expected_dimension == 768
        assert error.actual_provider == "openai"
        assert error.actual_model == "text-embedding-3-small"
        assert error.actual_dimension == 1536

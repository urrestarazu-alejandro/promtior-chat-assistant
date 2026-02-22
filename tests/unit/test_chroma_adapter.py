"""Tests for ChromaDB vector store adapter."""

from unittest.mock import MagicMock, patch

import pytest

from src.promtior_assistant.domain.models.embedding_metadata import EmbeddingMetadata
from src.promtior_assistant.domain.ports.vector_store_port import Document
from src.promtior_assistant.infrastructure.vector_store.chroma_adapter import (
    ChromaVectorStoreAdapter,
)


class TestChromaVectorStoreAdapter:
    """Tests for ChromaVectorStoreAdapter class."""

    @patch("src.promtior_assistant.infrastructure.vector_store.chroma_adapter.Chroma")
    def test_initialize(self, mock_chroma):
        """Test adapter initialization."""
        mock_embeddings = MagicMock()
        metadata = EmbeddingMetadata.from_ollama("test-model")
        adapter = ChromaVectorStoreAdapter(
            persist_directory="/tmp/chroma_test",
            embeddings=mock_embeddings,
            embedding_metadata=metadata,
            validate_metadata=False,
        )
        mock_chroma.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.promtior_assistant.infrastructure.vector_store.chroma_adapter.Chroma")
    async def test_retrieve_documents(self, mock_chroma):
        """Test retrieving documents."""
        mock_embeddings = MagicMock()
        mock_client = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "Test content"
        mock_doc.metadata = {"source": "test"}
        mock_client.similarity_search.return_value = [mock_doc]
        mock_chroma.return_value = mock_client

        metadata = EmbeddingMetadata.from_ollama("test-model")
        adapter = ChromaVectorStoreAdapter(
            persist_directory="/tmp/chroma_test",
            embeddings=mock_embeddings,
            embedding_metadata=metadata,
            validate_metadata=False,
        )

        docs = await adapter.retrieve_documents("test query", k=3)

        assert len(docs) == 1
        assert docs[0].page_content == "Test content"
        mock_client.similarity_search.assert_called_once_with("test query", k=3)

    @pytest.mark.asyncio
    @patch("src.promtior_assistant.infrastructure.vector_store.chroma_adapter.Chroma")
    async def test_add_documents(self, mock_chroma):
        """Test adding documents."""
        mock_embeddings = MagicMock()
        mock_client = MagicMock()
        mock_chroma.return_value = mock_client

        metadata = EmbeddingMetadata.from_ollama("test-model")
        adapter = ChromaVectorStoreAdapter(
            persist_directory="/tmp/chroma_test",
            embeddings=mock_embeddings,
            embedding_metadata=metadata,
            validate_metadata=False,
        )

        docs = [Document(page_content="Test content", metadata={"source": "test"})]
        await adapter.add_documents(docs)

        mock_client.add_documents.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.promtior_assistant.infrastructure.vector_store.chroma_adapter.Chroma")
    async def test_delete_collection(self, mock_chroma):
        """Test deleting collection."""
        mock_embeddings = MagicMock()
        mock_client = MagicMock()
        mock_chroma.return_value = mock_client

        metadata = EmbeddingMetadata.from_ollama("test-model")
        adapter = ChromaVectorStoreAdapter(
            persist_directory="/tmp/chroma_test",
            embeddings=mock_embeddings,
            embedding_metadata=metadata,
            validate_metadata=False,
        )

        await adapter.delete_collection()

        mock_client.delete_collection.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.promtior_assistant.infrastructure.vector_store.chroma_adapter.Chroma")
    async def test_retrieve_documents_empty(self, mock_chroma):
        """Test retrieving with no results."""
        mock_embeddings = MagicMock()
        mock_client = MagicMock()
        mock_client.similarity_search.return_value = []
        mock_chroma.return_value = mock_client

        metadata = EmbeddingMetadata.from_ollama("test-model")
        adapter = ChromaVectorStoreAdapter(
            persist_directory="/tmp/chroma_test",
            embeddings=mock_embeddings,
            embedding_metadata=metadata,
            validate_metadata=False,
        )

        docs = await adapter.retrieve_documents("nonexistent query")

        assert len(docs) == 0

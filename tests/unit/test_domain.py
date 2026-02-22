"""Tests for domain ports and services."""

import pytest

from src.promtior_assistant.domain.ports.vector_store_port import Document, VectorStorePort


class TestDocument:
    """Tests for Document model."""

    def test_create_document(self):
        """Test creating a document."""
        doc = Document(page_content="Test content", metadata={"source": "test"})
        assert doc.page_content == "Test content"
        assert doc.metadata == {"source": "test"}

    def test_document_with_complex_metadata(self):
        """Test document with complex metadata."""
        metadata = {"source": "test", "page": 1, "tags": ["important", "review"]}
        doc = Document(page_content="Test content", metadata=metadata)
        assert doc.metadata == metadata


class TestVectorStorePort:
    """Tests for VectorStorePort interface."""

    def test_vector_store_port_is_abstract(self):
        """Test that VectorStorePort is an abstract class."""
        with pytest.raises(TypeError):
            VectorStorePort()

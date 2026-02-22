"""ChromaDB vector store adapter."""

import json
import logging
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from ...domain.exceptions import EmbeddingMismatchError
from ...domain.models.embedding_metadata import EmbeddingMetadata
from ...domain.ports.vector_store_port import Document, VectorStorePort

logger = logging.getLogger(__name__)


class ChromaVectorStoreAdapter(VectorStorePort):
    """Adapter for ChromaDB vector store.

    Implements VectorStorePort interface for ChromaDB.
    Features:
    - Automatic embedding metadata tracking
    - Validation against stored metadata
    - Provider-specific collection names
    """

    METADATA_FILE = "embedding_metadata.json"

    def __init__(
        self,
        persist_directory: str,
        embeddings: Embeddings,
        embedding_metadata: EmbeddingMetadata,
        validate_metadata: bool = True,
    ):
        """Initialize ChromaDB adapter.

        Args:
            persist_directory: Directory for persistent storage
            embeddings: Embeddings provider
            embedding_metadata: Current embedding configuration
            validate_metadata: Whether to validate against stored metadata

        Raises:
            EmbeddingMismatchError: If stored metadata doesn't match current config
        """
        self._persist_directory = Path(persist_directory)
        self._embedding_metadata = embedding_metadata

        collection_name = f"promtior_docs_{embedding_metadata.provider.value}"

        if validate_metadata and self._persist_directory.exists():
            self._validate_metadata()

        self._client = Chroma(
            persist_directory=str(self._persist_directory),
            embedding_function=embeddings,
            collection_name=collection_name,
        )

    async def retrieve_documents(
        self,
        query: str,
        k: int = 3,
    ) -> list[Document]:
        """Retrieve relevant documents for a query.

        Args:
            query: Search query
            k: Number of documents to retrieve

        Returns:
            List of relevant documents
        """
        docs = self._client.similarity_search(query, k=k)

        return [Document(page_content=doc.page_content, metadata=doc.metadata) for doc in docs]

    async def add_documents(
        self,
        documents: list[Document],
    ) -> None:
        """Add documents to the vector store.

        Args:
            documents: Documents to add
        """
        from langchain_core.documents import Document as LangChainDocument

        langchain_docs = [
            LangChainDocument(page_content=doc.page_content, metadata=doc.metadata)
            for doc in documents
        ]
        self._client.add_documents(langchain_docs)

    async def delete_collection(self) -> None:
        """Delete the entire collection."""
        self._client.delete_collection()

    def save_metadata(self) -> None:
        """Save embedding metadata to disk.

        This should be called after ingesting data to track which
        embeddings were used.
        """
        self._persist_directory.mkdir(parents=True, exist_ok=True)
        metadata_path = self._persist_directory / self.METADATA_FILE

        with open(metadata_path, "w") as f:
            json.dump(self._embedding_metadata.to_dict(), f, indent=2)

        logger.info(f"Saved embedding metadata: {self._embedding_metadata}")

    def _validate_metadata(self) -> None:
        """Validate current embedding config against stored metadata.

        Raises:
            EmbeddingMismatchError: If metadata doesn't match
        """
        metadata_path = self._persist_directory / self.METADATA_FILE

        if not metadata_path.exists():
            logger.warning(
                f"No embedding metadata found at {metadata_path}. "
                "This vector store was created before metadata tracking. "
                "Skipping validation."
            )
            return

        with open(metadata_path) as f:
            stored_data = json.load(f)

        stored_metadata = EmbeddingMetadata.from_dict(stored_data)

        if not self._embedding_metadata.matches(stored_metadata):
            raise EmbeddingMismatchError(
                expected_provider=stored_metadata.provider.value,
                expected_model=stored_metadata.model,
                expected_dimension=stored_metadata.dimension,
                actual_provider=self._embedding_metadata.provider.value,
                actual_model=self._embedding_metadata.model,
                actual_dimension=self._embedding_metadata.dimension,
            )

        logger.info(f"Embedding metadata validated: {stored_metadata}")

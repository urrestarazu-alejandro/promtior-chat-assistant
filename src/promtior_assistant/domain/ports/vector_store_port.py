"""Port (interface) for vector stores."""

from typing import Protocol


class Document:
    """Document with content and metadata."""

    def __init__(self, page_content: str, metadata: dict):
        self.page_content = page_content
        self.metadata = metadata


class VectorStorePort(Protocol):
    """Port for vector database implementations.

    This interface defines operations for document storage and retrieval.
    """

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
        ...

    async def add_documents(
        self,
        documents: list[Document],
    ) -> None:
        """Add documents to the vector store.

        Args:
            documents: Documents to add
        """
        ...

    async def delete_collection(self) -> None:
        """Delete the entire collection."""
        ...

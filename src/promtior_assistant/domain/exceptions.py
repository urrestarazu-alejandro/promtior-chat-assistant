"""Domain-level exceptions."""


class EmbeddingMismatchError(Exception):
    """Exception raised when embedding configuration doesn't match vector store.

    This error occurs when:
    - Vector store was created with one embedding provider (e.g., Ollama)
    - Application tries to use a different provider (e.g., OpenAI)
    - Embedding dimensions don't match
    """

    def __init__(
        self,
        expected_provider: str,
        expected_model: str,
        expected_dimension: int,
        actual_provider: str,
        actual_model: str,
        actual_dimension: int,
    ):
        """Initialize mismatch error.

        Args:
            expected_provider: Provider used to create vector store
            expected_model: Model used to create vector store
            expected_dimension: Dimension of stored embeddings
            actual_provider: Current provider configuration
            actual_model: Current model configuration
            actual_dimension: Current embedding dimension
        """
        self.expected_provider = expected_provider
        self.expected_model = expected_model
        self.expected_dimension = expected_dimension
        self.actual_provider = actual_provider
        self.actual_model = actual_model
        self.actual_dimension = actual_dimension

        message = (
            f"Embedding configuration mismatch detected!\n"
            f"Vector store was created with:\n"
            f"  - Provider: {expected_provider}\n"
            f"  - Model: {expected_model}\n"
            f"  - Dimension: {expected_dimension}\n"
            f"But you're trying to use:\n"
            f"  - Provider: {actual_provider}\n"
            f"  - Model: {actual_model}\n"
            f"  - Dimension: {actual_dimension}\n\n"
            f"To fix this, you need to re-ingest data with the current provider.\n"
            f"Run: POST /admin/reingest?admin_key=<YOUR_KEY>"
        )
        super().__init__(message)

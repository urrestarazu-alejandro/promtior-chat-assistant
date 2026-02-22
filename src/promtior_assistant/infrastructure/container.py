"""Dependency Injection Container (Singleton Pattern)."""

import logging

from langchain_core.embeddings import Embeddings

from ..domain.ports.llm_port import LLMPort
from .factories import create_embeddings, create_llm


class Container:
    """Dependency Injection Container using Singleton pattern.

    This container manages the lifecycle of expensive resources (LLM clients,
    embeddings, vector store connections) ensuring they are created once and
    reused across all requests.

    Benefits:
    - Connection pooling (HTTP clients reused)
    - Memory efficiency (single instances)
    - Performance (avoid re-initialization)
    - Clean separation of concerns
    """

    _llm: LLMPort | None = None
    _embeddings: Embeddings | None = None

    @classmethod
    def get_llm(cls) -> LLMPort:
        """Get or create LLM instance (singleton).

        Returns:
            LLM provider instance
        """
        if cls._llm is None:
            cls._llm = create_llm()
        if cls._llm is None:
            raise RuntimeError("Failed to initialize LLM")
        return cls._llm

    @classmethod
    def get_embeddings(cls) -> Embeddings:
        """Get or create embeddings instance (singleton).

        Returns:
            Embeddings provider instance
        """
        if cls._embeddings is None:
            cls._embeddings = create_embeddings()
        return cls._embeddings

    @classmethod
    async def initialize(cls):
        """Initialize all dependencies on startup.

        Pre-creates all singletons to avoid cold start on first request.
        """
        logger = logging.getLogger(__name__)

        logger.info("Initializing Container dependencies...")

        llm = cls.get_llm()
        logger.info(f"  ✓ LLM initialized: {llm.model_name}")

        _ = cls.get_embeddings()
        logger.info("  ✓ Embeddings initialized")

        logger.info("Container initialization complete")

    @classmethod
    async def cleanup(cls):
        """Cleanup resources on shutdown.

        Closes all connections and releases resources.
        """
        logger = logging.getLogger(__name__)

        logger.info("Cleaning up Container resources...")

        cls._llm = None
        cls._embeddings = None

        logger.info("Container cleanup complete")

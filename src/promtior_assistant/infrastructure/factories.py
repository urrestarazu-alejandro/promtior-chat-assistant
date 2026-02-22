"""Factory functions for creating infrastructure components."""

import os

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from ..config import settings
from ..domain.ports.llm_port import LLMPort
from ..infrastructure.embeddings.ollama_embeddings import CustomOllamaEmbeddings
from ..infrastructure.llm.ollama_async_adapter import OllamaAsyncAdapter
from ..infrastructure.llm.openai_async_adapter import OpenAIAsyncAdapter


def create_llm() -> LLMPort:
    """Create async LLM adapter based on configuration.

    Returns:
        LLM adapter instance

    Raises:
        ValueError: If configuration is invalid
    """
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")

        return OpenAIAsyncAdapter(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=0.7,
        )

    return OllamaAsyncAdapter(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        temperature=0.7,
    )


def create_embeddings() -> Embeddings:
    """Create embeddings adapter based on configuration.

    Returns:
        Embeddings adapter instance (sync - required by ChromaDB)

    Raises:
        ValueError: If configuration is invalid
    """
    import logging

    logger = logging.getLogger(__name__)

    logger.warning(f"create_embeddings: llm_provider={settings.llm_provider}")
    logger.warning(f"create_embeddings: use_openai_embeddings={settings.use_openai_embeddings}")

    if settings.llm_provider == "openai" and settings.use_openai_embeddings:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")

        logger.info(f"Using OpenAI embeddings: {settings.openai_embedding_model}")
        return OpenAIEmbeddings(
            model=settings.openai_embedding_model,
        )

    logger.info(f"Using Ollama embeddings: {settings.ollama_embedding_model}")
    return CustomOllamaEmbeddings(
        base_url=settings.ollama_base_url,
        model=settings.ollama_embedding_model,
    )

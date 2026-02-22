"""Dependency injection for FastAPI v1 API."""

import os

from ....application.use_cases.answer_question import AnswerQuestionUseCase
from ....config import settings
from ....domain.models.embedding_metadata import EmbeddingMetadata
from ....domain.services.validators import InputValidator, OutputValidator
from ....infrastructure.factories import create_embeddings, create_llm
from ....infrastructure.vector_store.chroma_adapter import ChromaVectorStoreAdapter


def _get_current_embedding_metadata() -> EmbeddingMetadata:
    """Get embedding metadata for current configuration.

    Returns:
        EmbeddingMetadata matching current settings
    """
    if settings.llm_provider == "openai":
        use_openai_embeddings = os.getenv("USE_OPENAI_EMBEDDINGS", "false").lower() == "true"

        if use_openai_embeddings:
            return EmbeddingMetadata.from_openai(settings.openai_embedding_model)
        return EmbeddingMetadata.from_ollama(settings.ollama_embedding_model)

    return EmbeddingMetadata.from_ollama(settings.ollama_embedding_model)


def get_answer_question_use_case() -> AnswerQuestionUseCase:
    """Create AnswerQuestionUseCase with all dependencies.

    Returns:
        Configured use case
    """
    llm = create_llm()
    embeddings = create_embeddings()
    embedding_metadata = _get_current_embedding_metadata()

    vector_store = ChromaVectorStoreAdapter(
        persist_directory=settings.chroma_persist_directory,
        embeddings=embeddings,
        embedding_metadata=embedding_metadata,
        validate_metadata=True,
    )

    return AnswerQuestionUseCase(
        llm=llm,
        vector_store=vector_store,
        input_validator=InputValidator(),
        output_validator=OutputValidator(),
    )

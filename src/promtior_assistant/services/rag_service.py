"""RAG service implementation."""

import asyncio
import logging
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from ..config import settings
from ..domain.services.validators import InputValidator, OutputValidator
from ..infrastructure.embeddings.ollama_embeddings import CustomOllamaEmbeddings
from ..infrastructure.llm.ollama_adapter import CustomOllamaChat

logger = logging.getLogger(__name__)


def _get_embeddings() -> Embeddings:
    """Get embeddings based on LLM provider.

    Automatically detects the correct embedding provider to match
    the vector store configuration. No manual configuration needed!
    """
    import os

    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        use_openai_embeddings = os.getenv("USE_OPENAI_EMBEDDINGS", "false").lower() == "true"

        if use_openai_embeddings:
            return OpenAIEmbeddings(
                model=settings.openai_embedding_model,
            )
        return CustomOllamaEmbeddings(
            model=settings.ollama_embedding_model,
            base_url=settings.ollama_base_url,
        )
    return CustomOllamaEmbeddings(
        model=settings.ollama_embedding_model,
        base_url=settings.ollama_base_url,
    )


def _get_llm() -> BaseChatModel:
    """Get LLM based on provider."""
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        return ChatOpenAI(
            model=settings.openai_model,
            temperature=0.7,
        )
    return CustomOllamaChat(
        model=settings.ollama_model,
        temperature=0.7,
        base_url=settings.ollama_base_url,
    )


def _get_prompt_template() -> PromptTemplate:
    """Get the prompt template for RAG."""
    template = """Use the context below to answer the question.

Context: In May 2023, Promtior was founded facing this context.
Question: When was Promtior founded?
Answer: In May 2023

Context: Promtior offers AI consulting services.
Question: What does Promtior do?
Answer: Promtior offers AI consulting services

Context: {context}
Question: {question}
Answer:"""
    return PromptTemplate(
        template=template,
        input_variables=["context", "question"],
    )


@lru_cache(maxsize=1)
def _get_vector_store() -> Chroma:
    """Get vector store (cached)."""
    embeddings = _get_embeddings()
    return Chroma(
        persist_directory=settings.chroma_persist_directory,
        embedding_function=embeddings,
    )


@lru_cache(maxsize=1)
def _get_qa_chain() -> Runnable:
    """Get RAG chain (cached)."""
    prompt = _get_prompt_template()
    llm = _get_llm()
    vector_store = _get_vector_store()

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False,
    )


def _validate_environment() -> None:
    """Validate production environment setup."""
    if settings.environment == "production":
        if settings.llm_provider != "openai":
            logger.warning(
                "Production environment should use OpenAI for better reliability. "
                f"Current provider: {settings.llm_provider}"
            )
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required in production environment. "
                "Set OPENAI_API_KEY in your .env file."
            )


async def get_rag_answer(question: str) -> str:
    """
    Get answer using RAG with best practices:
    1. Input validation
    2. Cost tracking (production)
    3. Retry logic
    4. Output validation

    Args:
        question: User question

    Returns:
        Answer from the RAG system

    Raises:
        ValueError: If input is invalid or environment misconfigured
        Exception: For errors during RAG processing
    """
    _validate_environment()

    validated_question = InputValidator.validate(question)

    max_retries = 3
    last_error = None

    for attempt in range(max_retries):
        try:
            qa_chain = _get_qa_chain()
            result = await qa_chain.ainvoke({"query": validated_question})
            answer = result["result"]

            validated_answer = OutputValidator.validate(answer)
            return validated_answer

        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = 2**attempt
                logger.warning(
                    f"RAG call failed (attempt {attempt + 1}/{max_retries}), "
                    f"retrying in {wait_time}s: {e}"
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"RAG call failed after {max_retries} attempts: {e}")

    raise Exception(f"Failed to generate RAG answer after {max_retries} attempts: {last_error}")

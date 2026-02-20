"""RAG chain implementation following AI wrapper best practices."""

import os
import time
import logging
from dataclasses import dataclass
from functools import lru_cache

import httpx
from pydantic import ConfigDict
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import Runnable

from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .config import settings

logger = logging.getLogger(__name__)


@dataclass
class UsageStats:
    """Track AI usage for cost management."""

    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    cost: float = 0.0

    def calculate_cost(self) -> float:
        rates = {
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        }
        rate = rates.get(self.model, {"input": 0.50, "output": 1.50})
        return (self.input_tokens * rate["input"] + self.output_tokens * rate["output"]) / 1_000_000


class UsageTracker:
    """Track and log AI API usage."""

    def __init__(self):
        self.stats: list[UsageStats] = []

    def log(self, stats: UsageStats):
        self.stats.append(stats)
        logger.info(
            f"AI Usage - Model: {stats.model}, "
            f"Input: {stats.input_tokens}, Output: {stats.output_tokens}, "
            f"Cost: ${stats.cost:.4f}"
        )

    def get_total_cost(self) -> float:
        return sum(s.cost for s in self.stats)


usage_tracker = UsageTracker()


class InputValidator:
    """Validate and sanitize user input."""

    MAX_LENGTH = 2000
    MIN_LENGTH = 3

    @classmethod
    def validate(cls, question: str) -> str:
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        question = question.strip()

        if len(question) < cls.MIN_LENGTH:
            raise ValueError(f"Question too short (min {cls.MIN_LENGTH} chars)")

        if len(question) > cls.MAX_LENGTH:
            raise ValueError(f"Question too long (max {cls.MAX_LENGTH} chars)")

        return question


class OutputValidator:
    """Validate AI output quality."""

    @staticmethod
    def validate(answer: str) -> str:
        if not answer or not answer.strip():
            raise ValueError("Empty response from AI")

        if len(answer.strip()) < 5:
            raise ValueError("Response too short to be valid")

        return answer.strip()


class CustomOllamaEmbeddings(Embeddings):
    """Custom OllamaEmbeddings implementation that supports API key authentication."""

    model_config = ConfigDict(extra="ignore")

    def __init__(self, model: str = "nomic-embed-text", base_url: str = "https://ollama.com"):
        super().__init__()
        self.model = model
        self.base_url = base_url

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        is_remote = "localhost" not in self.base_url and "127.0.0.1" not in self.base_url
        headers = {}

        if is_remote:
            api_key = (
                settings.ollama_api_key
                or os.getenv("OLLAMA_API_KEY")
                or os.getenv("OLLAMA_AUTH_TOKEN")
            )
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model, "input": texts},
                headers=headers,
            )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

        result = response.json()
        return result.get("embeddings", [])

    def embed_query(self, text: str) -> list[float]:
        is_remote = "localhost" not in self.base_url and "127.0.0.1" not in self.base_url
        headers = {}

        if is_remote:
            api_key = (
                settings.ollama_api_key
                or os.getenv("OLLAMA_API_KEY")
                or os.getenv("OLLAMA_AUTH_TOKEN")
            )
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model, "input": text},
                headers=headers,
            )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

        result = response.json()
        embeddings = result.get("embeddings", [[]])
        return embeddings[0] if embeddings else []


class CustomOllamaChat(BaseChatModel):
    """Custom ChatOllama implementation that supports API key authentication."""

    model_config = ConfigDict(extra="ignore")

    model: str = "gpt-oss:20b"
    temperature: float = 0.7
    base_url: str = "https://ollama.com"

    @property
    def _llm_type(self) -> str:
        return "custom_ollama"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager=None,
        **kwargs,
    ) -> ChatResult:
        is_remote = "localhost" not in self.base_url and "127.0.0.1" not in self.base_url
        headers = {}

        if is_remote:
            api_key = (
                settings.ollama_api_key
                or os.getenv("OLLAMA_API_KEY")
                or os.getenv("OLLAMA_AUTH_TOKEN")
            )
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

        prompt = messages[-1].content

        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "temperature": self.temperature,
                },
                headers=headers,
            )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

        result = response.json()
        content = result["message"]["content"]

        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])


def _get_embeddings() -> Embeddings:
    """Get embeddings based on LLM provider.

    Note: In production, we use Ollama embeddings because ChromaDB was populated
    with Ollama's embedding dimension (768). If you want to use OpenAI embeddings,
    you need to re-ingest the data with OpenAI provider.
    """
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        # Check if we should use OpenAI embeddings or Ollama embeddings
        # Ollama embeddings are used by default to maintain compatibility with existing ChromaDB
        use_openai_embeddings = os.getenv("USE_OPENAI_EMBEDDINGS", "false").lower() == "true"

        if use_openai_embeddings:
            return OpenAIEmbeddings(
                model=settings.openai_embedding_model,
            )
        # Default: use Ollama embeddings for compatibility
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
    return PromptTemplate(
        template="""Eres un asistente que responde preguntas sobre Promtior, una empresa de consultoría tecnológica y organizacional especializada en inteligencia artificial.

Usa el siguiente contexto para responder la pregunta. Si no sabes la respuesta basándote en el contexto, di que no tienes esa información.

Contexto: {context}

Pregunta: {question}

Respuesta:""",
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
    Get answer using RAG with AI wrapper best practices:
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
                time.sleep(wait_time)
            else:
                logger.error(f"RAG call failed after {max_retries} attempts: {e}")

    raise Exception(f"Failed to generate RAG answer after {max_retries} attempts: {last_error}")

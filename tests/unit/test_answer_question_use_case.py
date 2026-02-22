"""Unit tests for AnswerQuestionUseCase."""

from unittest.mock import AsyncMock

import pytest

from src.promtior_assistant.application.use_cases.answer_question import (
    AnswerQuestionUseCase,
)
from src.promtior_assistant.domain.ports.llm_port import LLMPort
from src.promtior_assistant.domain.ports.vector_store_port import Document
from src.promtior_assistant.domain.services.validators import (
    InputValidator,
    OutputValidator,
)


@pytest.fixture
def mock_llm():
    """Mock LLM port."""
    llm = AsyncMock(spec=LLMPort)
    llm.generate.return_value = "Promtior ofrece consultoría en IA y transformación digital."
    llm.model_name = "mock-model"
    return llm


@pytest.fixture
def mock_vector_store():
    """Mock vector store port."""
    vector_store = AsyncMock()

    mock_doc = Document(
        page_content="Promtior es una empresa de consultoría especializada en IA.",
        metadata={"source": "test"},
    )

    vector_store.retrieve_documents.return_value = [mock_doc]
    return vector_store


@pytest.fixture
def use_case(mock_llm, mock_vector_store):
    """Create use case with mocked dependencies."""
    return AnswerQuestionUseCase(
        llm=mock_llm,
        vector_store=mock_vector_store,
        input_validator=InputValidator(),
        output_validator=OutputValidator(),
    )


@pytest.mark.asyncio
async def test_execute_success(use_case, mock_llm, mock_vector_store):
    """Test successful question answering."""
    question = "¿Qué servicios ofrece Promtior?"

    answer = await use_case.execute(question)

    assert answer == "Promtior ofrece consultoría en IA y transformación digital."
    mock_vector_store.retrieve_documents.assert_called_once()
    mock_llm.generate.assert_called_once()


@pytest.mark.asyncio
async def test_execute_invalid_input(use_case):
    """Test with invalid input."""
    with pytest.raises(ValueError, match="Question too short"):
        await use_case.execute("ab")


@pytest.mark.asyncio
async def test_execute_llm_failure_with_retry(use_case, mock_llm, mock_vector_store):
    """Test retry logic when LLM fails."""
    mock_llm.generate.side_effect = [
        Exception("API error"),
        Exception("API error"),
        "Success answer",
    ]

    answer = await use_case.execute("¿Qué es Promtior?")

    assert answer == "Success answer"
    assert mock_llm.generate.call_count == 3


@pytest.mark.asyncio
async def test_execute_max_retries_exceeded(use_case, mock_llm):
    """Test that max retries raises exception."""
    mock_llm.generate.side_effect = Exception("API error")

    with pytest.raises(Exception, match="Failed to generate RAG answer"):
        await use_case.execute("¿Qué es Promtior?")

    assert mock_llm.generate.call_count == 3


@pytest.mark.asyncio
async def test_execute_empty_documents(use_case, mock_llm, mock_vector_store):
    """Test with empty document results."""
    mock_vector_store.retrieve_documents.return_value = []

    answer = await use_case.execute("¿Qué es Promtior?")

    assert "Promtior ofrece consultoría en IA y transformación digital." in answer


@pytest.mark.asyncio
async def test_build_prompt(use_case):
    """Test prompt building."""
    question = "¿Qué servicios ofrecen?"
    context = "Promtior es una empresa de consultoría."

    prompt = use_case._build_prompt(question, context)

    assert question in prompt
    assert context in prompt
    assert "Promtior" in prompt

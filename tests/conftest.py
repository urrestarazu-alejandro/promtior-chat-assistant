"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture
def mock_rag_answer():
    """Mock RAG answer for testing without Ollama dependency."""
    async def mock_answer(question: str) -> str:
        # Simulate RAG responses based on question
        if "servicios" in question.lower() or "services" in question.lower():
            return "Promtior ofrece servicios de consultoría tecnológica y organizacional especializada en inteligencia artificial."
        elif "fundada" in question.lower() or "founded" in question.lower():
            return "Promtior fue fundada en 2023."
        elif "promtior" in question.lower():
            return "Promtior es una empresa de consultoría especializada en IA y transformación digital."
        else:
            return "Promtior es una empresa de consultoría tecnológica."

    return mock_answer


@pytest.fixture(autouse=True)
def mock_rag_for_tests(request, mock_rag_answer):
    """Auto-mock RAG for unit tests only (not integration tests)."""
    # Skip mocking for integration tests
    if "integration" in request.keywords:
        yield None
    else:
        with patch('src.promtior_assistant.main.get_rag_answer') as mock:
            mock.return_value = mock_rag_answer
            yield mock

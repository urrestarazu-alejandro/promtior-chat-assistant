"""Pytest configuration and fixtures."""

from unittest.mock import patch

import pytest


@pytest.fixture
def mock_rag_answer():
    """Mock RAG answer for testing without Ollama dependency."""

    async def mock_answer(question: str) -> str:
        q = question.lower()
        if "servicios" in q or "services" in q:
            return "Promtior ofrece servicios de consultoría tecnológica y organizacional."
        elif "fundada" in q or "founded" in q:
            return "Promtior fue fundada en 2023."
        elif "promtior" in q:
            return "Promtior es una empresa de consultoría especializada en IA."
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
        with patch("src.promtior_assistant.main.get_rag_answer") as mock:
            mock.return_value = mock_rag_answer
            yield mock

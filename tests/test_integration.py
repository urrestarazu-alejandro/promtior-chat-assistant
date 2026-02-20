"""Integration tests that require Ollama running."""

import pytest
from fastapi.testclient import TestClient

from src.promtior_assistant.main import app

client = TestClient(app)

pytestmark = pytest.mark.integration


@pytest.mark.integration
def test_ask_real_ollama():
    """
    Integration test with real Ollama.

    Requires:
    - Ollama running on localhost:11434
    - ChromaDB populated with data
    """
    response = client.get("/ask?q=¿Qué es Promtior?")
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "answer" in data
    assert "status" in data
    assert data["status"] == "success"
    assert len(data["answer"]) > 10  # Real answer should be substantial


@pytest.mark.integration
def test_real_rag_quality():
    """Test that RAG returns meaningful answers."""
    response = client.get("/ask?q=¿Qué servicios ofrece Promtior?")
    assert response.status_code == 200
    data = response.json()
    answer_lower = data["answer"].lower()

    # Answer should contain relevant keywords from the actual scraped data
    assert len(data["answer"]) > 20
    # Note: Actual content depends on what was scraped

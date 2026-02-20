"""Basic API tests."""

from fastapi.testclient import TestClient

from src.promtior_assistant.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Promtior" in data["message"]
    assert "usage" in data


def test_health():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "environment" in data


def test_ask_missing_query():
    """Test ask endpoint without query parameter."""
    response = client.get("/ask")
    assert response.status_code == 422  # Validation error


def test_ask_empty_query():
    """Test ask endpoint with empty query."""
    response = client.get("/ask?q=")
    assert response.status_code == 422  # Validation error


def test_ask_with_question():
    """Test ask endpoint with a question."""
    response = client.get("/ask?q=¿Qué es Promtior?")
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "answer" in data
    assert "status" in data
    assert data["status"] == "success"
    assert data["question"] == "¿Qué es Promtior?"
    assert len(data["answer"]) > 0


def test_ask_services_question():
    """Test asking about Promtior services."""
    response = client.get("/ask?q=¿Qué servicios ofrece Promtior?")
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    # Check if answer contains relevant keywords
    answer_lower = data["answer"].lower()
    assert any(
        keyword in answer_lower
        for keyword in ["consultoría", "consulting", "servicios", "services", "ia", "ai"]
    )


def test_ask_founding_question():
    """Test asking about Promtior founding."""
    response = client.get("/ask?q=¿Cuándo fue fundada Promtior?")
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    # Check if answer contains year
    assert "2023" in data["answer"]

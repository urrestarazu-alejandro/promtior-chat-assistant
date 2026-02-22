"""Basic API tests."""

from unittest.mock import MagicMock, patch

import pytest
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


def test_health_live():
    """Test liveness probe endpoint."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


def test_health_ready():
    """Test readiness probe endpoint."""
    with patch("src.promtior_assistant.main.Container") as mock_container:
        mock_container._llm = MagicMock()
        mock_container._embeddings = MagicMock()

        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "components" in data
        assert data["components"]["llm"] == "ready"
        assert data["components"]["embeddings"] == "ready"


def test_health_ready_not_ready():
    """Test readiness probe when components not initialized."""
    with patch("src.promtior_assistant.main.Container") as mock_container:
        mock_container._llm = None
        mock_container._embeddings = None

        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_ready"
        assert data["components"]["llm"] == "not_initialized"


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


def test_reingest_invalid_key():
    """Test reingest endpoint with invalid admin key."""
    with patch("src.promtior_assistant.main.os.getenv") as mock_getenv:
        mock_getenv.return_value = "correct_key"

        response = client.post("/admin/reingest?admin_key=wrong_key")
        assert response.status_code == 401


def test_reingest_missing_key():
    """Test reingest endpoint without admin key."""
    with patch("src.promtior_assistant.main.os.getenv") as mock_getenv:
        mock_getenv.return_value = "correct_key"

        response = client.post("/admin/reingest")
        assert response.status_code == 422  # FastAPI Query param is required


def test_reingest_invalid_key_env():
    """Test reingest endpoint when no env key is set."""
    with patch("src.promtior_assistant.main.os.getenv") as mock_getenv:
        mock_getenv.return_value = None

        response = client.post("/admin/reingest?admin_key=any")
        assert response.status_code == 401


def test_api_v1_ask():
    """Test v1 ask endpoint."""
    response = client.get("/api/v1/ask?q=¿Qué es Promtior?")
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "answer" in data
    assert "status" in data
    assert data["status"] == "success"


def test_root_includes_examples():
    """Test root endpoint includes usage examples."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "examples" in data
    assert len(data["examples"]) > 0


def test_health_includes_environment():
    """Test health endpoint includes environment info."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["environment"] in ["development", "production"]


def test_liveness_returns_alive():
    """Test liveness returns alive status."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


def test_readiness_when_ready():
    """Test readiness when all components ready."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "components" in data

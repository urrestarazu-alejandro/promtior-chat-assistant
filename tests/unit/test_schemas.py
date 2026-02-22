"""Tests for Pydantic request/response schemas."""

import pytest
from pydantic import ValidationError

from src.promtior_assistant.presentation.schemas.request import AskRequest, ReingestRequest
from src.promtior_assistant.presentation.schemas.response import (
    AskResponse,
    ErrorResponse,
    HealthResponse,
    ReingestResponse,
)


class TestAskRequest:
    """Tests for AskRequest schema."""

    def test_valid_question(self):
        """Test creating a valid ask request."""
        request = AskRequest(question="¿Qué servicios ofrece Promtior?")
        assert request.question == "¿Qué servicios ofrece Promtior?"

    def test_question_min_length(self):
        """Test question minimum length validation."""
        with pytest.raises(ValidationError) as exc_info:
            AskRequest(question="ab")
        assert "question" in str(exc_info.value)

    def test_question_max_length(self):
        """Test question maximum length validation."""
        long_question = "a" * 2001
        with pytest.raises(ValidationError) as exc_info:
            AskRequest(question=long_question)
        assert "question" in str(exc_info.value)

    def test_question_exact_min_length(self):
        """Test question at exact minimum length."""
        request = AskRequest(question="abc")
        assert request.question == "abc"

    def test_question_exact_max_length(self):
        """Test question at exact maximum length."""
        request = AskRequest(question="a" * 2000)
        assert len(request.question) == 2000


class TestReingestRequest:
    """Tests for ReingestRequest schema."""

    def test_valid_admin_key(self):
        """Test creating a valid reingest request."""
        request = ReingestRequest(admin_key="secret-key-123")
        assert request.admin_key == "secret-key-123"


class TestAskResponse:
    """Tests for AskResponse schema."""

    def test_valid_response(self):
        """Test creating a valid ask response."""
        response = AskResponse(
            question="¿Qué servicios ofrece Promtior?",
            answer="Promtior ofrece servicios de consultoría.",
        )
        assert response.question == "¿Qué servicios ofrece Promtior?"
        assert response.answer == "Promtior ofrece servicios de consultoría."
        assert response.status == "success"

    def test_custom_status(self):
        """Test response with custom status."""
        response = AskResponse(question="test", answer="test answer", status="partial")
        assert response.status == "partial"


class TestReingestResponse:
    """Tests for ReingestResponse schema."""

    def test_valid_response(self):
        """Test creating a valid reingest response."""
        response = ReingestResponse(status="success", message="Data re-ingested successfully")
        assert response.status == "success"
        assert response.message == "Data re-ingested successfully"


class TestHealthResponse:
    """Tests for HealthResponse schema."""

    def test_valid_response(self):
        """Test creating a valid health response."""
        response = HealthResponse(status="healthy", environment="development")
        assert response.status == "healthy"
        assert response.environment == "development"


class TestErrorResponse:
    """Tests for ErrorResponse schema."""

    def test_valid_response(self):
        """Test creating a valid error response."""
        response = ErrorResponse(detail="Something went wrong")
        assert response.detail == "Something went wrong"

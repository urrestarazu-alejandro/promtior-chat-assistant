"""Unit tests for validators."""

import pytest

from src.promtior_assistant.domain.services.validators import (
    InputValidator,
    OutputValidator,
)


class TestInputValidator:
    """Tests for InputValidator."""

    def test_validate_success(self):
        """Test successful validation."""
        question = "¿Qué servicios ofrece Promtior?"
        result = InputValidator.validate(question)
        assert result == question

    def test_validate_strips_whitespace(self):
        """Test that whitespace is stripped."""
        question = "  ¿Qué es Promtior?  "
        result = InputValidator.validate(question)
        assert result == "¿Qué es Promtior?"

    def test_validate_empty_raises(self):
        """Test that empty input raises."""
        with pytest.raises(ValueError, match="Question cannot be empty"):
            InputValidator.validate("")

    def test_validate_whitespace_only_raises(self):
        """Test that whitespace-only input raises."""
        with pytest.raises(ValueError, match="Question cannot be empty"):
            InputValidator.validate("   ")

    def test_validate_too_short_raises(self):
        """Test that too short input raises."""
        with pytest.raises(ValueError, match="Question too short"):
            InputValidator.validate("ab")

    def test_validate_exactly_min_length(self):
        """Test that exactly min length is valid."""
        result = InputValidator.validate("abc")
        assert result == "abc"

    def test_validate_too_long_raises(self):
        """Test that too long input raises."""
        long_question = "a" * 2001
        with pytest.raises(ValueError, match="Question too long"):
            InputValidator.validate(long_question)

    def test_validate_exactly_max_length(self):
        """Test that exactly max length is valid."""
        question = "a" * 2000
        result = InputValidator.validate(question)
        assert len(result) == 2000


class TestOutputValidator:
    """Tests for OutputValidator."""

    def test_validate_success(self):
        """Test successful validation."""
        answer = "Promtior ofrece servicios de consultoría en IA."
        result = OutputValidator.validate(answer)
        assert result == answer

    def test_validate_strips_whitespace(self):
        """Test that whitespace is stripped."""
        answer = "  Respuesta válida  "
        result = OutputValidator.validate(answer)
        assert result == "Respuesta válida"

    def test_validate_empty_raises(self):
        """Test that empty output raises."""
        with pytest.raises(ValueError, match="Empty response from AI"):
            OutputValidator.validate("")

    def test_validate_whitespace_only_raises(self):
        """Test that whitespace-only output raises."""
        with pytest.raises(ValueError, match="Empty response from AI"):
            OutputValidator.validate("   ")

    def test_validate_too_short_raises(self):
        """Test that too short output raises."""
        with pytest.raises(ValueError, match="Response too short"):
            OutputValidator.validate("abc")

    def test_validate_exactly_min_length(self):
        """Test that exactly min length is valid."""
        result = OutputValidator.validate("abcde")
        assert result == "abcde"

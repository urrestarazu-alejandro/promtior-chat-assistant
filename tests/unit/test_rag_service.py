"""Tests for RAG service."""

from unittest.mock import patch

import pytest

from src.promtior_assistant.services.rag_service import (
    _get_prompt_template,
    _validate_environment,
)


class TestRagService:
    """Tests for RAG service functions."""

    @patch("src.promtior_assistant.services.rag_service.settings")
    def test_get_prompt_template(self, mock_settings):
        """Test getting prompt template."""
        prompt = _get_prompt_template()
        assert prompt is not None
        assert "context" in prompt.input_variables
        assert "question" in prompt.input_variables

    @patch("src.promtior_assistant.services.rag_service.settings")
    def test_validate_environment_development(self, mock_settings):
        """Test environment validation in development."""
        mock_settings.environment = "development"
        mock_settings.llm_provider = "ollama"
        mock_settings.openai_api_key = None
        _validate_environment()

    @patch("src.promtior_assistant.services.rag_service.settings")
    @patch("src.promtior_assistant.services.rag_service.logger")
    def test_validate_environment_production_warning(self, mock_logger, mock_settings):
        """Test environment validation in production with non-OpenAI provider."""
        mock_settings.environment = "production"
        mock_settings.llm_provider = "ollama"
        mock_settings.openai_api_key = "sk-test-key"

        _validate_environment()
        mock_logger.warning.assert_called_once()

    @patch("src.promtior_assistant.services.rag_service.settings")
    def test_validate_environment_production_requires_api_key(self, mock_settings):
        """Test that production requires API key."""
        mock_settings.environment = "production"
        mock_settings.llm_provider = "openai"
        mock_settings.openai_api_key = None

        with pytest.raises(ValueError, match="OPENAI_API_KEY is required in production"):
            _validate_environment()

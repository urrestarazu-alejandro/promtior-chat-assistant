"""Tests for factory functions."""

import os
from unittest.mock import patch

import pytest

from src.promtior_assistant.infrastructure.factories import create_embeddings, create_llm


class TestCreateLLM:
    """Tests for create_llm factory function."""

    @patch("src.promtior_assistant.infrastructure.factories.settings")
    def test_create_ollama_llm(self, mock_settings):
        """Test creating Ollama LLM."""
        mock_settings.llm_provider = "ollama"
        mock_settings.ollama_base_url = "http://localhost:11434"
        mock_settings.ollama_model = "llama2"

        llm = create_llm()
        assert llm.model_name == "llama2"

    @patch("src.promtior_assistant.infrastructure.factories.settings")
    def test_create_openai_llm(self, mock_settings):
        """Test creating OpenAI LLM."""
        mock_settings.llm_provider = "openai"
        mock_settings.openai_api_key = "sk-test-key"
        mock_settings.openai_model = "gpt-4o-mini"

        llm = create_llm()
        assert llm.model_name == "gpt-4o-mini"

    @patch("src.promtior_assistant.infrastructure.factories.settings")
    def test_openai_requires_api_key(self, mock_settings):
        """Test that OpenAI requires API key."""
        mock_settings.llm_provider = "openai"
        mock_settings.openai_api_key = None
        mock_settings.openai_model = "gpt-4o-mini"

        with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
            create_llm()


class TestCreateEmbeddings:
    """Tests for create_embeddings factory function."""

    @patch("src.promtior_assistant.infrastructure.factories.settings")
    def test_create_ollama_embeddings(self, mock_settings):
        """Test creating Ollama embeddings."""
        mock_settings.llm_provider = "ollama"
        mock_settings.ollama_base_url = "http://localhost:11434"
        mock_settings.ollama_embedding_model = "nomic-embed-text"

        embeddings = create_embeddings()
        assert embeddings.model == "nomic-embed-text"

    @patch("src.promtior_assistant.infrastructure.factories.settings")
    def test_openai_embeddings_requires_api_key(self, mock_settings):
        """Test that OpenAI embeddings require API key."""
        mock_settings.llm_provider = "openai"
        mock_settings.openai_api_key = None
        mock_settings.openai_embedding_model = "text-embedding-3-small"

        with patch.dict(os.environ, {"USE_OPENAI_EMBEDDINGS": "true"}):
            with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
                create_embeddings()

    @patch("src.promtior_assistant.infrastructure.factories.settings")
    def test_openai_provider_uses_ollama_embeddings_by_default(self, mock_settings):
        """Test that OpenAI provider uses Ollama embeddings by default."""
        mock_settings.llm_provider = "openai"
        mock_settings.openai_api_key = "sk-test-key"
        mock_settings.ollama_base_url = "http://localhost:11434"
        mock_settings.ollama_embedding_model = "nomic-embed-text"

        with patch.dict(os.environ, {"USE_OPENAI_EMBEDDINGS": "false"}, clear=True):
            embeddings = create_embeddings()
            assert embeddings.model == "nomic-embed-text"

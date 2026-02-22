"""Tests for configuration settings."""

import os
from unittest.mock import patch

from src.promtior_assistant.config import Settings


class TestSettings:
    """Tests for Settings configuration."""

    def test_default_development_settings(self):
        """Test default development settings."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            with patch("src.promtior_assistant.config.Settings.model_config", {"env_file": None}):
                settings = Settings(_env_file=None)
                assert settings.environment == "development"
                assert settings.llm_provider == "ollama"

    def test_production_settings(self):
        """Test production settings with explicit provider."""
        with (
            patch.dict(
                os.environ,
                {"ENVIRONMENT": "production", "LLM_PROVIDER": "openai"},
                clear=True,
            ),
            patch("src.promtior_assistant.config.Settings.model_config", {"env_file": None}),
        ):
            settings = Settings(_env_file=None)
            assert settings.environment == "production"
            assert settings.llm_provider == "openai"

    def test_production_defaults_to_openai(self):
        """Test that production defaults to openai provider."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            with patch("src.promtior_assistant.config.Settings.model_config", {"env_file": None}):
                settings = Settings(_env_file=None)
                assert settings.llm_provider == "openai"

    def test_ollama_settings(self):
        """Test Ollama-specific settings."""
        with (
            patch.dict(
                os.environ,
                {
                    "OLLAMA_BASE_URL": "http://localhost:11434",
                    "OLLAMA_MODEL": "llama2",
                    "OLLAMA_EMBEDDING_MODEL": "nomic-embed-text",
                },
                clear=True,
            ),
            patch("src.promtior_assistant.config.Settings.model_config", {"env_file": None}),
        ):
            settings = Settings(_env_file=None)
            assert settings.ollama_base_url == "http://localhost:11434"
            assert settings.ollama_model == "llama2"
            assert settings.ollama_embedding_model == "nomic-embed-text"

    def test_openai_settings(self):
        """Test OpenAI-specific settings."""
        with (
            patch.dict(
                os.environ,
                {
                    "OPENAI_API_KEY": "sk-test-key",
                    "OPENAI_MODEL": "gpt-4o-mini",
                    "OPENAI_EMBEDDING_MODEL": "text-embedding-3-small",
                },
                clear=True,
            ),
            patch("src.promtior_assistant.config.Settings.model_config", {"env_file": None}),
        ):
            settings = Settings(_env_file=None)
            assert settings.openai_api_key == "sk-test-key"
            assert settings.openai_model == "gpt-4o-mini"
            assert settings.openai_embedding_model == "text-embedding-3-small"

    def test_chroma_persist_directory_development(self):
        """Test ChromaDB directory in development."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            with patch("src.promtior_assistant.config.Settings.model_config", {"env_file": None}):
                settings = Settings(_env_file=None)
                assert settings.chroma_persist_directory == "./data/chroma_db"

    def test_chroma_persist_directory_production(self):
        """Test ChromaDB directory in production."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            with patch("src.promtior_assistant.config.Settings.model_config", {"env_file": None}):
                settings = Settings(_env_file=None)
                assert "chroma_db" in settings.chroma_persist_directory

    def test_chroma_persist_directory_production_custom_path(self):
        """Test ChromaDB directory in production with custom path."""
        with (
            patch.dict(
                os.environ,
                {"ENVIRONMENT": "production", "CHROMA_DB_PATH": "/custom/path/chroma"},
                clear=True,
            ),
            patch("src.promtior_assistant.config.Settings.model_config", {"env_file": None}),
        ):
            settings = Settings(_env_file=None)
            assert settings.chroma_persist_directory == "/custom/path/chroma"

    def test_chroma_persist_directory_production_temp_dir(self):
        """Test ChromaDB uses tempfile in production."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            with patch("src.promtior_assistant.config.Settings.model_config", {"env_file": None}):
                settings = Settings(_env_file=None)
                path = settings.chroma_persist_directory
                assert path.startswith("/var/") or path.startswith("/tmp/") or "chroma_db" in path

    def test_empty_llm_provider_defaults_based_on_environment_development(self):
        """Test that empty llm_provider defaults to ollama in development."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development", "LLM_PROVIDER": ""}, clear=True):
            with patch("src.promtior_assistant.config.Settings.model_config", {"env_file": None}):
                settings = Settings(_env_file=None)
                assert settings.llm_provider == "ollama"

    def test_empty_llm_provider_defaults_based_on_environment_production(self):
        """Test that empty llm_provider defaults to openai in production."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "LLM_PROVIDER": ""}, clear=True):
            with patch("src.promtior_assistant.config.Settings.model_config", {"env_file": None}):
                settings = Settings(_env_file=None)
                assert settings.llm_provider == "openai"

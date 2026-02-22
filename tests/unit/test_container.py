"""Tests for dependency injection container."""

from unittest.mock import MagicMock, patch

import pytest

from src.promtior_assistant.infrastructure.container import Container


@pytest.fixture(autouse=True)
def reset_container():
    """Reset container singleton between tests."""
    Container._llm = None
    Container._embeddings = None
    yield
    Container._llm = None
    Container._embeddings = None


class TestContainer:
    """Tests for Container singleton."""

    @patch("src.promtior_assistant.infrastructure.container.create_llm")
    @patch("src.promtior_assistant.infrastructure.container.create_embeddings")
    def test_get_llm_creates_instance(self, mock_create_embeddings, mock_create_llm):
        """Test that get_llm creates an LLM instance."""
        mock_llm = MagicMock()
        mock_llm.model_name = "gpt-4o-mini"
        mock_create_llm.return_value = mock_llm

        llm = Container.get_llm()
        assert llm == mock_llm
        mock_create_llm.assert_called_once()

    @patch("src.promtior_assistant.infrastructure.container.create_llm")
    @patch("src.promtior_assistant.infrastructure.container.create_embeddings")
    def test_get_llm_returns_cached_instance(self, mock_create_embeddings, mock_create_llm):
        """Test that get_llm returns cached instance."""
        mock_llm = MagicMock()
        mock_create_llm.return_value = mock_llm

        llm1 = Container.get_llm()
        llm2 = Container.get_llm()

        assert llm1 == llm2
        assert mock_create_llm.call_count == 1

    @patch("src.promtior_assistant.infrastructure.container.create_llm")
    @patch("src.promtior_assistant.infrastructure.container.create_embeddings")
    def test_get_embeddings_creates_instance(self, mock_create_embeddings, mock_create_llm):
        """Test that get_embeddings creates an embeddings instance."""
        mock_embeddings = MagicMock()
        mock_create_embeddings.return_value = mock_embeddings

        embeddings = Container.get_embeddings()
        assert embeddings == mock_embeddings
        mock_create_embeddings.assert_called_once()

    @patch("src.promtior_assistant.infrastructure.container.create_llm")
    @patch("src.promtior_assistant.infrastructure.container.create_embeddings")
    def test_get_embeddings_returns_cached_instance(self, mock_create_embeddings, mock_create_llm):
        """Test that get_embeddings returns cached instance."""
        mock_embeddings = MagicMock()
        mock_create_embeddings.return_value = mock_embeddings

        embeddings1 = Container.get_embeddings()
        embeddings2 = Container.get_embeddings()

        assert embeddings1 == embeddings2
        assert mock_create_embeddings.call_count == 1

    @patch("src.promtior_assistant.infrastructure.container.create_llm")
    @patch("src.promtior_assistant.infrastructure.container.create_embeddings")
    def test_get_llm_raises_on_failure(self, mock_create_embeddings, mock_create_llm):
        """Test that get_llm raises RuntimeError when creation fails."""
        mock_create_llm.return_value = None

        with pytest.raises(RuntimeError, match="Failed to initialize LLM"):
            Container.get_llm()

    @patch("src.promtior_assistant.infrastructure.container.create_llm")
    @patch("src.promtior_assistant.infrastructure.container.create_embeddings")
    @pytest.mark.asyncio
    async def test_initialize(self, mock_create_embeddings, mock_create_llm):
        """Test container initialization."""
        mock_llm = MagicMock()
        mock_llm.model_name = "gpt-4o-mini"
        mock_create_llm.return_value = mock_llm

        mock_embeddings = MagicMock()
        mock_create_embeddings.return_value = mock_embeddings

        await Container.initialize()

        mock_create_llm.assert_called_once()
        mock_create_embeddings.assert_called_once()

    @patch("src.promtior_assistant.infrastructure.container.create_llm")
    @patch("src.promtior_assistant.infrastructure.container.create_embeddings")
    @pytest.mark.asyncio
    async def test_cleanup(self, mock_create_embeddings, mock_create_llm):
        """Test container cleanup."""
        mock_llm = MagicMock()
        mock_llm.model_name = "gpt-4o-mini"
        mock_create_llm.return_value = mock_llm

        mock_embeddings = MagicMock()
        mock_create_embeddings.return_value = mock_embeddings

        await Container.initialize()
        await Container.cleanup()

        assert Container._llm is None
        assert Container._embeddings is None

"""Tests for LLM adapters."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.promtior_assistant.infrastructure.llm.ollama_async_adapter import OllamaAsyncAdapter
from src.promtior_assistant.infrastructure.llm.openai_async_adapter import OpenAIAsyncAdapter


class TestOpenAIAsyncAdapter:
    """Tests for OpenAI async adapter."""

    def test_init(self):
        """Test adapter initialization."""
        adapter = OpenAIAsyncAdapter(api_key="sk-test", model="gpt-4o-mini", temperature=0.5)
        assert adapter._model == "gpt-4o-mini"
        assert adapter._temperature == 0.5

    def test_model_name_property(self):
        """Test model_name property."""
        adapter = OpenAIAsyncAdapter(api_key="sk-test", model="gpt-4o-mini")
        assert adapter.model_name == "gpt-4o-mini"

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with OpenAIAsyncAdapter(api_key="sk-test") as adapter:
            assert adapter is not None

    @pytest.mark.asyncio
    async def test_generate(self):
        """Test generate method."""
        adapter = OpenAIAsyncAdapter(api_key="sk-test", model="gpt-4o-mini")

        mock_response = MagicMock()
        mock_response.content = "Generated text"
        adapter._client = AsyncMock()
        adapter._client.ainvoke = AsyncMock(return_value=mock_response)

        result = await adapter.generate("Test prompt")
        assert result == "Generated text"
        adapter._client.ainvoke.assert_called_once()


class TestOllamaAsyncAdapter:
    """Tests for Ollama async adapter."""

    def test_init(self):
        """Test adapter initialization."""
        adapter = OllamaAsyncAdapter(
            base_url="http://localhost:11434",
            model="llama2",
            temperature=0.5,
        )
        assert adapter._model == "llama2"
        assert adapter._temperature == 0.5

    def test_model_name_property(self):
        """Test model_name property."""
        adapter = OllamaAsyncAdapter(model="llama2")
        assert adapter.model_name == "llama2"

    def test_get_headers_local(self):
        """Test headers for local Ollama."""
        adapter = OllamaAsyncAdapter(base_url="http://localhost:11434")
        headers = adapter._get_headers()
        assert headers == {}

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with OllamaAsyncAdapter() as adapter:
            assert adapter is not None
            assert adapter._client is not None

"""Tests for API v1 dependencies."""

from unittest.mock import MagicMock, patch

from src.promtior_assistant.presentation.api.v1.dependencies import get_answer_question_use_case


class TestDependencies:
    """Tests for FastAPI v1 dependencies."""

    @patch("src.promtior_assistant.presentation.api.v1.dependencies.ChromaVectorStoreAdapter")
    @patch("src.promtior_assistant.presentation.api.v1.dependencies.create_embeddings")
    @patch("src.promtior_assistant.presentation.api.v1.dependencies.create_llm")
    def test_get_answer_question_use_case(
        self, mock_create_llm, mock_create_embeddings, mock_chroma
    ):
        """Test creating AnswerQuestionUseCase."""
        mock_llm = MagicMock()
        mock_embeddings = MagicMock()
        mock_vector_store = MagicMock()

        mock_create_llm.return_value = mock_llm
        mock_create_embeddings.return_value = mock_embeddings
        mock_chroma.return_value = mock_vector_store

        use_case = get_answer_question_use_case()

        assert use_case is not None
        mock_create_llm.assert_called_once()
        mock_create_embeddings.assert_called_once()
        mock_chroma.assert_called_once()

    @patch("src.promtior_assistant.presentation.api.v1.dependencies.settings")
    @patch("src.promtior_assistant.presentation.api.v1.dependencies.ChromaVectorStoreAdapter")
    @patch("src.promtior_assistant.presentation.api.v1.dependencies.create_embeddings")
    @patch("src.promtior_assistant.presentation.api.v1.dependencies.create_llm")
    @patch("src.promtior_assistant.presentation.api.v1.dependencies._get_current_embedding_metadata")
    def test_get_answer_question_use_case_with_settings(
        self,
        mock_get_metadata,
        mock_create_llm,
        mock_create_embeddings,
        mock_chroma,
        mock_settings,
    ):
        """Test creating use case with settings."""
        from src.promtior_assistant.domain.models.embedding_metadata import EmbeddingMetadata

        mock_settings.chroma_persist_directory = "/tmp/test_chroma"

        mock_llm = MagicMock()
        mock_embeddings = MagicMock()
        mock_vector_store = MagicMock()
        mock_metadata = EmbeddingMetadata.from_ollama("test-model")

        mock_create_llm.return_value = mock_llm
        mock_create_embeddings.return_value = mock_embeddings
        mock_chroma.return_value = mock_vector_store
        mock_get_metadata.return_value = mock_metadata

        use_case = get_answer_question_use_case()

        mock_chroma.assert_called_once_with(
            persist_directory="/tmp/test_chroma",
            embeddings=mock_embeddings,
            embedding_metadata=mock_metadata,
            validate_metadata=True,
        )

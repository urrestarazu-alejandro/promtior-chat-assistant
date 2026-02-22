"""Configuration settings for the application."""

import os
import tempfile

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: str = Field(default="development")

    # LLM Provider (openai | ollama) - defaults to openai in production
    llm_provider: str = Field(default="")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.llm_provider:
            self.llm_provider = "openai" if self.environment == "production" else "ollama"

    # Ollama (Development)
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama2")
    ollama_embedding_model: str = Field(default="nomic-embed-text")
    ollama_api_key: str | None = Field(default=None)

    # OpenAI (Production)
    openai_api_key: str | None = Field(default=None)
    openai_model: str = Field(default="gpt-4o-mini")
    openai_embedding_model: str = Field(default="text-embedding-3-small")

    @property
    def use_openai_embeddings(self) -> bool:
        """Check if OpenAI embeddings should be used."""
        return os.getenv("USE_OPENAI_EMBEDDINGS", "false").lower() == "true"

    # ChromaDB
    @property
    def chroma_persist_directory(self) -> str:
        if self.environment == "production":
            return os.environ.get(
                "CHROMA_DB_PATH", os.path.join(tempfile.gettempdir(), "chroma_db")
            )
        return "./data/chroma_db"

    # Security - CORS Configuration
    @property
    def cors_allowed_origins(self) -> list[str]:
        """Get CORS allowed origins from environment.

        In production, reads from CORS_ALLOWED_ORIGINS env var (comma-separated).
        In development, allows localhost origins for testing.

        Returns:
            list[str]: List of allowed origins
        """
        origins_str = os.getenv("CORS_ALLOWED_ORIGINS", "")
        if self.environment == "production" and origins_str:
            return [o.strip() for o in origins_str.split(",")]
        return ["http://localhost:3000", "http://localhost:8000"]

    @property
    def cors_allow_credentials(self) -> bool:
        """Only allow credentials when specific origins are set.

        Credentials should only be allowed when we have explicit origins configured.
        Never allow credentials with wildcard origins (security risk).

        Returns:
            bool: True if production with specific origins, False otherwise
        """
        return self.environment == "production" and bool(os.getenv("CORS_ALLOWED_ORIGINS"))


# Global settings instance
settings = Settings()

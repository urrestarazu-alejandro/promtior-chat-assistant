"""Configuration settings for the application."""

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

    # ChromaDB
    chroma_persist_directory: str = Field(default="./data/chroma_db_v2")


# Global settings instance
settings = Settings()

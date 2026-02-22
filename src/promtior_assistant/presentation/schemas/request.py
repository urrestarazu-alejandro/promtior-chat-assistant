"""Pydantic request schemas."""

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Request schema for asking a question."""

    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="The question to ask about Promtior",
        examples=["¿Qué servicios ofrece Promtior?"],
    )


class ReingestRequest(BaseModel):
    """Request schema for re-ingesting data."""

    admin_key: str = Field(..., description="Admin key for authentication")

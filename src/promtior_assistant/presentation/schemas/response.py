"""Pydantic response schemas."""

from pydantic import BaseModel


class AskResponse(BaseModel):
    """Response schema for answering a question."""

    question: str
    answer: str
    status: str = "success"


class ReingestResponse(BaseModel):
    """Response schema for re-ingest operation."""

    status: str
    message: str


class HealthResponse(BaseModel):
    """Response schema for health check."""

    status: str
    environment: str


class ErrorResponse(BaseModel):
    """Response schema for errors."""

    detail: str

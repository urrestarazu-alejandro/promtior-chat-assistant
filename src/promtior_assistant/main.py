"""FastAPI application - MVP."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .infrastructure.container import Container
from .presentation.api.v1 import routes as v1_routes
from .presentation.exceptions import (
    AuthenticationError,
    BusinessRuleError,
    LLMProviderError,
    PromtiorError,
    ValidationError,
)
from .presentation.middleware.logging import LoggingMiddleware
from .presentation.middleware.request_id import RequestIDMiddleware
from .presentation.middleware.timeout import TimeoutMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI.

    Handles application startup and shutdown:
    - Startup: Initialize Container (pre-create singletons)
    - Shutdown: Cleanup resources (close connections)
    """
    logger.info("=" * 60)
    logger.info("Starting Promtior RAG Assistant API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info("=" * 60)

    try:
        await Container.initialize()
        logger.info("✓ Application startup complete")
    except Exception as e:
        logger.error(f"✗ Startup failed: {e}", exc_info=True)
        raise

    yield

    logger.info("=" * 60)
    logger.info("Shutting down Promtior RAG Assistant API")
    logger.info("=" * 60)

    try:
        await Container.cleanup()
        logger.info("✓ Application shutdown complete")
    except Exception as e:
        logger.error(f"✗ Shutdown error: {e}", exc_info=True)


def get_rag_answer():
    from .services.rag_service import get_rag_answer as _get_rag_answer

    return _get_rag_answer


app = FastAPI(
    title="Promtior RAG Assistant",
    version="0.1.0",
    description="RAG-based chatbot for answering questions about Promtior",
    lifespan=lifespan,
)


# Exception handlers
@app.exception_handler(PromtiorError)
async def promtior_error_handler(request, exc: PromtiorError):
    logger.error(f"Promtior error: {exc.message}")
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message},
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc: ValidationError):
    logger.warning(f"Validation error: {exc.message}")
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=422,
        content={"error": exc.message, "type": "validation_error"},
    )


@app.exception_handler(BusinessRuleError)
async def business_rule_error_handler(request, exc: BusinessRuleError):
    logger.warning(f"Business rule violation: {exc.message}")
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=400,
        content={"error": exc.message, "type": "business_rule_error"},
    )


@app.exception_handler(LLMProviderError)
async def llm_provider_error_handler(request, exc: LLMProviderError):
    logger.error(f"LLM provider error: {exc.message}")
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=503,
        content={"error": exc.message, "type": "llm_provider_error"},
    )


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request, exc: AuthenticationError):
    logger.warning(f"Authentication error: {exc.message}")
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=401,
        content={"error": exc.message, "type": "authentication_error"},
    )


# Middleware stack (order matters - added in reverse)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TimeoutMiddleware, timeout=300.0)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 routes
app.include_router(v1_routes.router, prefix="/api/v1", tags=["questions"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Promtior RAG Assistant API",
        "version": "0.1.0",
        "environment": settings.environment,
        "usage": "GET /ask?q=your_question",
        "examples": [
            "/ask?q=¿Qué servicios ofrece Promtior?",
            "/ask?q=¿Cuándo fue fundada la empresa?",
        ],
    }


@app.get("/health")
async def health():
    """Basic health check endpoint."""
    return {"status": "ok", "environment": settings.environment}


@app.get("/health/live")
async def liveness():
    """Kubernetes liveness probe."""
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness():
    """Kubernetes readiness probe."""
    components = {
        "llm": "ready" if Container._llm is not None else "not_initialized",
        "embeddings": "ready" if Container._embeddings is not None else "not_initialized",
    }

    is_ready = all(v == "ready" for v in components.values())

    return {
        "status": "ready" if is_ready else "not_ready",
        "components": components,
    }


@app.post("/admin/reingest")
async def reingest(admin_key: str = Query(...)):
    """Re-ingest data into ChromaDB. Requires admin key.

    Note: This endpoint has an extended timeout of 5 minutes for data processing.
    """
    expected_key = os.getenv("ADMIN_REINGEST_KEY")
    if not expected_key or admin_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid admin key")

    try:
        import asyncio
        import shutil

        from .ingest import ingest_data

        chroma_dir = settings.chroma_persist_directory
        logger.info(f"Re-ingest started. Chroma directory: {chroma_dir}")
        logger.info(f"Environment: {settings.environment}")

        if os.path.exists(chroma_dir):
            logger.info(f"Removing existing ChromaDB directory: {chroma_dir}")
            try:
                import stat

                for root, dirs, files in os.walk(chroma_dir):
                    for d in dirs:
                        os.chmod(os.path.join(root, d), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    for f in files:
                        os.chmod(os.path.join(root, f), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                shutil.rmtree(chroma_dir, ignore_errors=True)
                logger.info("Directory removed")
            except Exception as e:
                logger.warning(f"Error removing directory: {e}, continuing anyway...")

        os.makedirs(chroma_dir, mode=0o777, exist_ok=True)
        logger.info(f"Created directory: {chroma_dir} with full permissions")

        logger.info("Starting ingest_data()...")
        await asyncio.to_thread(ingest_data)
        logger.info("Ingest completed successfully")

        return {"status": "success", "message": "Data re-ingested successfully"}
    except Exception as e:
        import traceback

        logger.error(f"Re-ingest failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Re-ingest failed: {str(e)}") from e


@app.get("/ask")
async def ask_question(
    q: str = Query(
        ...,
        min_length=1,
        max_length=500,
        description="Your question about Promtior",
        examples=["¿Qué servicios ofrece Promtior?"],
    ),
):
    """Ask a question about Promtior."""
    try:
        answer = await get_rag_answer()(q)
        return {
            "question": q,
            "answer": answer,
            "status": "success",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}",
        ) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

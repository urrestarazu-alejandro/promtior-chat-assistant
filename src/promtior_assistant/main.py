"""FastAPI application - MVP."""

import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import settings


def get_rag_answer():
    from .rag import get_rag_answer as _get_rag_answer

    return _get_rag_answer


app = FastAPI(
    title="Promtior RAG Assistant",
    version="0.1.0",
    description="RAG-based chatbot for answering questions about Promtior",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Root endpoint with API information.

    Returns:
        API information and usage instructions
    """
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
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "ok", "environment": settings.environment}


@app.post("/admin/reingest")
async def reingest(admin_key: str = Query(...)):
    """
    Re-ingest data into ChromaDB. Requires admin key.

    This will:
    1. Delete existing ChromaDB collection
    2. Scrape the Promtior website
    3. Generate new embeddings
    4. Store in ChromaDB
    """
    expected_key = os.getenv("ADMIN_REINGEST_KEY")
    if not expected_key or admin_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid admin key")

    try:
        from .ingest import ingest_data
        import shutil

        chroma_dir = settings.chroma_persist_directory
        if os.path.exists(chroma_dir):
            shutil.rmtree(chroma_dir)
            os.makedirs(chroma_dir)

        ingest_data()

        return {"status": "success", "message": "Data re-ingested successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Re-ingest failed: {str(e)}")


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
    """
    Ask a question about Promtior.

    Args:
        q: Question to ask

    Returns:
        Answer from the RAG system

    Examples:
        - curl "http://localhost:8000/ask?q=¿Qué servicios ofrece Promtior?"
        - curl "http://localhost:8000/ask?q=¿Cuándo fue fundada la empresa?"
    """
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
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

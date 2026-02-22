"""API v1 routes."""

from fastapi import APIRouter, Depends, HTTPException, Request

from ....application.use_cases.answer_question import AnswerQuestionUseCase
from .dependencies import get_answer_question_use_case

router = APIRouter()


@router.get("/ask")
async def ask_question(
    request: Request,
    q: str,
    use_case: AnswerQuestionUseCase = Depends(get_answer_question_use_case),
):
    """Ask a question about Promtior.

    Rate limited to 30 requests per minute (configured in main.py).
    Note: The rate limiting is applied at the main app level, so this endpoint
    automatically inherits the rate limiting configuration.

    Args:
        request: FastAPI request object (for rate limiting)
        q: Question to ask
        use_case: Injected use case

    Returns:
        Answer from RAG system
    """
    try:
        answer = await use_case.execute(q)
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

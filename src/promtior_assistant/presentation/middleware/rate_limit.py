"""Rate limiting middleware using SlowAPI.

Provides DoS protection and prevents brute force attacks.
Uses in-memory storage (resets on restart) - sufficient for MVP.

Note: Rate limit headers (X-RateLimit-*) are disabled to avoid conflicts
with FastAPI's automatic JSON response conversion. The rate limiting
still works, but clients won't receive X-RateLimit-Remaining headers.
"""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)


def get_limiter() -> Limiter:
    """Create rate limiter with in-memory backend.

    Default limits:
    - 100 requests per hour
    - 20 requests per minute

    Endpoint-specific limits can override these defaults using the
    `@limiter.limit()` decorator.

    Storage: In-memory (resets on restart)
    - Simpler, no external dependencies
    - Good enough for MVP
    - For production with multiple instances, consider Redis backend

    Returns:
        Limiter: Configured SlowAPI limiter instance
    """
    logger.info("Initializing rate limiter with in-memory storage")
    return Limiter(
        key_func=get_remote_address,
        default_limits=["100/hour", "20/minute"],
        storage_uri="memory://",
        headers_enabled=False,
    )


async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom 429 handler with retry-after headers.

    Args:
        request: FastAPI request object
        exc: RateLimitExceeded exception

    Returns:
        JSONResponse: 429 error with retry-after header
    """
    retry_after = exc.detail.split("Retry after ")[1] if "Retry after" in exc.detail else "60"

    logger.warning(
        f"Rate limit exceeded for {get_remote_address(request)}",
        extra={
            "ip": get_remote_address(request),
            "endpoint": request.url.path,
            "retry_after": retry_after,
        },
    )

    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": retry_after,
        },
        headers={"Retry-After": retry_after},
    )

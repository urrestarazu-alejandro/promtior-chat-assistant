"""Timeout middleware for request handling."""

import asyncio
import logging
import time
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60.0


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to add timeout handling to requests.

    This middleware ensures that long-running requests are terminated
    after a specified timeout to prevent resource exhaustion.

    Attributes:
        app: The ASGI application
        timeout: Timeout in seconds (default: 60)
    """

    def __init__(self, app: Callable, timeout: float = DEFAULT_TIMEOUT):
        """Initialize timeout middleware.

        Args:
            app: The ASGI application
            timeout: Timeout in seconds
        """
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with timeout handling.

        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain

        Returns:
            Response from the handler

        Raises:
            JSONResponse: If request times out
        """
        start_time = time.perf_counter()

        try:
            response = await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout,
            )

            duration = time.perf_counter() - start_time

            if duration > self.timeout * 0.8:
                logger.warning(
                    f"Request to {request.url.path} took {duration:.2f}s "
                    f"(approaching timeout of {self.timeout}s)"
                )

            return response

        except TimeoutError:
            duration = time.perf_counter() - start_time
            logger.error(f"Request to {request.url.path} timed out after {duration:.2f}s")

            return JSONResponse(
                status_code=504,
                content={
                    "error": "Request timeout",
                    "message": f"The request took longer than {self.timeout} seconds",
                    "timeout": self.timeout,
                },
            )

"""Authentication dependencies.

Provides secure authentication mechanisms for protected endpoints.
"""

import logging
import os
from typing import Annotated

from fastapi import Header, HTTPException

logger = logging.getLogger(__name__)


async def verify_admin_key(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    """Verify admin key from Authorization header.

    Security improvements over query parameter approach:
    - Not visible in URL/logs/browser history
    - Standard HTTP authentication pattern
    - Easier to rotate credentials

    Args:
        authorization: Authorization header value (expected format: "Bearer <key>")

    Returns:
        str: The verified admin key

    Raises:
        HTTPException: 401 if authorization header is missing, malformed, or invalid
    """
    if not authorization:
        logger.warning("Admin authentication failed: Missing Authorization header")
        raise HTTPException(
            status_code=401,
            detail="Authorization header required. Use: Authorization: Bearer <admin_key>",
        )

    if not authorization.startswith("Bearer "):
        logger.warning(
            "Admin authentication failed: Invalid Authorization header format",
            extra={"format": authorization[:20]},
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format. Use: Authorization: Bearer <admin_key>",
        )

    provided_key = authorization.replace("Bearer ", "").strip()

    if not provided_key:
        logger.warning("Admin authentication failed: Empty bearer token")
        raise HTTPException(
            status_code=401,
            detail="Empty bearer token. Provide a valid admin key.",
        )

    expected_key = os.getenv("ADMIN_REINGEST_KEY")

    if not expected_key:
        logger.error("Admin authentication failed: ADMIN_REINGEST_KEY not configured")
        raise HTTPException(
            status_code=503,
            detail="Admin authentication not configured. Contact system administrator.",
        )

    if provided_key != expected_key:
        logger.warning(
            "Admin authentication failed: Invalid admin key",
            extra={"key_prefix": provided_key[:4] if len(provided_key) >= 4 else "***"},
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid admin key.",
        )

    logger.info("Admin authentication successful")
    return provided_key

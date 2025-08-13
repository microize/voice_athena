"""Middleware for request/response processing."""

import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from .exceptions import CodePlatformException

logger = logging.getLogger(__name__)


async def exception_handler(request: Request, exc: CodePlatformException) -> JSONResponse:
    """Global exception handler for custom exceptions."""
    logger.error(f"Exception occurred: {exc.message}", exc_info=True)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for FastAPI HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
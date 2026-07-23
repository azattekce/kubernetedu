"""
Custom middleware for request processing
"""
import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add unique request ID to each request"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add request ID to request state and response headers
        """
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        # Bind request ID to logger context
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        # Clear context
        structlog.contextvars.clear_contextvars()

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request and response details
        """
        start_time = time.time()

        # Get request ID from state
        request_id = getattr(request.state, "request_id", "unknown")

        # Log request
        logger.info(
            "Request received",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            client_host=request.client.host if request.client else None,
            request_id=request_id,
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log response
        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            request_id=request_id,
        )

        return response

"""
Security Middleware for AutoCbot API
Implements rate limiting and security headers
"""

from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers to all responses"""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)

            # Ensure response is a valid Response object
            if not isinstance(response, Response):
                logger.error(f"Invalid response type: {type(response)}")
                return Response(
                    content='{"detail":"Internal server error"}',
                    status_code=500,
                    headers={"Content-Type": "application/json"}
                )

            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            return response
        except Exception as e:
            logger.error(f"SecurityHeadersMiddleware error: {e}", exc_info=True)
            return Response(
                content='{"detail":"Internal server error"}',
                status_code=500,
                headers={"Content-Type": "application/json"}
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting"""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health", "/", "/docs"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)

        recent = [ts for ts in self.requests[client_ip] if ts > cutoff]

        if len(recent) >= self.requests_per_minute:
            return Response(
                content='{"detail":"Rate limit exceeded"}',
                status_code=429,
                headers={"Content-Type": "application/json"}
            )

        self.requests[client_ip].append(now)
        return await call_next(request)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Adds unique request ID"""

    async def dispatch(self, request: Request, call_next):
        import uuid
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        try:
            response = await call_next(request)

            # Ensure response is a valid Response object
            if not isinstance(response, Response):
                logger.error(f"Invalid response type: {type(response)}")
                return Response(
                    content='{"detail":"Internal server error"}',
                    status_code=500,
                    headers={
                        "Content-Type": "application/json",
                        "X-Request-ID": request_id
                    }
                )

            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            logger.error(f"RequestIDMiddleware error: {e}", exc_info=True)
            return Response(
                content='{"detail":"Internal server error"}',
                status_code=500,
                headers={
                    "Content-Type": "application/json",
                    "X-Request-ID": request_id
                }
            )

"""Rate limiting middleware using slowapi."""

from fastapi import FastAPI, Request, Response
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from ..core.config import settings


def get_request_identifier(request: Request) -> str:
    """
    Get a unique identifier for the request.

    Uses API key if available, otherwise falls back to IP address.
    """
    # Check for API key in headers
    api_key = request.headers.get("X-API-Key")
    if api_key and settings.API_KEY_ENABLED:
        return f"apikey:{api_key}"

    # Fall back to IP address
    return get_remote_address(request)


# Create the limiter instance
limiter = Limiter(
    key_func=get_request_identifier,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
    enabled=settings.RATE_LIMIT_ENABLED,
    headers_enabled=True,
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Handle rate limit exceeded errors."""
    retry_after = exc.detail.split("per")[0].strip() if exc.detail else "60"

    return Response(
        content='{"error": "Rate limit exceeded", "detail": "Too many requests"}',
        status_code=429,
        media_type="application/json",
        headers={
            "Retry-After": retry_after,
            "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_MINUTE),
            "X-RateLimit-Remaining": "0",
        },
    )


def setup_rate_limiting(app: FastAPI) -> None:
    """Configure rate limiting for the FastAPI application."""
    if not settings.RATE_LIMIT_ENABLED:
        return

    # Add the limiter to app state
    app.state.limiter = limiter

    # Add the SlowAPI middleware
    app.add_middleware(SlowAPIMiddleware)

    # Add exception handler for rate limit exceeded
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

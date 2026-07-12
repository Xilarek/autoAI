"""Rate limiting через Redis (работает с несколькими инстансами)"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# Redis-based limiter — работает при нескольких инстансах backend
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri=settings.REDIS_URL,  # Используем Redis вместо in-memory
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded: {request.client.host} -> {request.url.path}")
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests",
            "retry_after": 60
        },
        headers={"Retry-After": "60"}
    )

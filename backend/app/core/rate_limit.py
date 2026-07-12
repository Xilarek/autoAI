"""Rate limiting middleware"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# Создаём limiter (без storage_uri — используем in-memory)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
)

# Обработчик превышения лимита
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Обработчик превышения rate limit"""
    logger.warning(f"Rate limit exceeded: {request.client.host} -> {request.url.path}")
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests",
            "retry_after": 60
        },
        headers={"Retry-After": "60"}
    )

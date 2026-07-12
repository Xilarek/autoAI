"""Переиспользуемый HTTP клиент с connection pooling"""

import httpx
from typing import Optional
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# Глобальный HTTP клиент с connection pooling
_http_client: Optional[httpx.AsyncClient] = None


def get_http_client() -> httpx.AsyncClient:
    """Получить переиспользуемый HTTP клиент"""
    global _http_client
    
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
                keepalive_expiry=30,
            ),
            http2=False,
        )
        logger.info("🌐 Создан HTTP клиент с connection pooling")
    
    return _http_client


def create_fresh_http_client() -> httpx.AsyncClient:
    """
    Создать НОВЫЙ HTTP клиент (не глобальный).
    
    Используется в Celery задачах, где event loop может быть закрыт.
    """
    client = httpx.AsyncClient(
        timeout=httpx.Timeout(60.0, connect=10.0),
        limits=httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20,
            keepalive_expiry=30,
        ),
        http2=False,
    )
    logger.info("🌐 Создан НОВЫЙ HTTP клиент для Celery задачи")
    return client


async def close_http_client():
    """Закрыть глобальный HTTP клиент"""
    global _http_client
    
    if _http_client is not None and not _http_client.is_closed:
        await _http_client.aclose()
        _http_client = None
        logger.info("🔒 HTTP клиент закрыт")


class HTTPClientContext:
    """Контекстный менеджер для HTTP клиента"""
    
    async def __aenter__(self):
        return get_http_client()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

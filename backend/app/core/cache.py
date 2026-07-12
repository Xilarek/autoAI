"""Redis кэширование для AutoAI"""

from aiocache import Cache
from aiocache.serializers import JsonSerializer
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# Создаём кэш с JSON сериализацией
cache = Cache(
    Cache.REDIS,
    endpoint="redis",
    port=6379,
    db=2,  # Используем отдельную БД для кэша
    serializer=JsonSerializer(),
    namespace="autoai",
)

# Декораторы для удобного кэширования
def cached(ttl: int = 60):
    """Декоратор для кэширования результатов функций
    
    Args:
        ttl: Время жизни кэша в секундах (по умолчанию 60)
    """
    from aiocache import cached as aiocache_cached
    
    return aiocache_cached(
        cache=Cache.REDIS,
        endpoint="redis",
        port=6379,
        db=2,
        serializer=JsonSerializer(),
        namespace="autoai",
        ttl=ttl,
    )

async def invalidate_cache(pattern: str = "*"):
    """Инвалидация кэша по паттерну"""
    try:
        await cache.delete(pattern)
        logger.info(f"🗑️ Кэш инвалидирован: {pattern}")
    except Exception as e:
        logger.error(f"Ошибка инвалидации кэша: {e}")

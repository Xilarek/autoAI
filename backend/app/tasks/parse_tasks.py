"""
ОДНА универсальная Celery задача для всех площадок.

Архитектура:
- parse_listing(platform, params) — работает с ЛЮБОЙ площадкой
- Парсер получается через registry: get_parser(platform)
- Добавление новой площадки НЕ требует изменений в этом файле
"""

from app.tasks.celery_app import celery_app
from app.parsers import get_parser
from app.services.listing_service import ListingService
from app.core.database import SessionLocal
from app.core.logger import setup_logger
from app.core.exceptions import ParserError, ParserBlockedError
import asyncio

logger = setup_logger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.parse_tasks.parse_listing",
    max_retries=2,  # Уменьшили с 3 до 2
    retry_backoff=True,
    retry_backoff_max=300,  # 5 минут максимум
    retry_jitter=True,
)
def parse_listing(self, platform: str, params: dict):
    """
    Универсальная задача парсинга для ЛЮБОЙ площадки.
    
    Args:
        platform: Название площадки ("drom", "avito", "auto_ru")
        params: Параметры поиска (query, region, year_min, etc.)
    
    Returns:
        {"status": "completed", "count": N, "platform": platform}
    """
    try:
        # Получаем парсер через registry
        parser = get_parser(platform)
        
        # Запускаем асинхронный парсинг с НОВЫМ HTTP клиентом
        async def run_parser():
            return await parser.parse_search(params, use_fresh_client=True)
        
        listings = asyncio.run(run_parser())
        
        if not listings:
            logger.warning(f"[{platform}] Парсер не вернул объявлений")
            return {"status": "completed", "count": 0, "platform": platform}
        
        # Сохраняем синхронно (для Celery)
        db = SessionLocal()
        try:
            service = ListingService()
            saved = service.save_listings_sync(db, listings)
            count = len(saved)
        finally:
            db.close()
        
        logger.info(f"✅ [{platform}] Парсинг завершён. Сохранено: {count}")
        return {"status": "completed", "count": count, "platform": platform}
        
    except ParserBlockedError as e:
        # Не повторяем при блокировке (403)
        logger.error(f"🚫 [{platform}] Заблокировано: {e.message}")
        return {"status": "blocked", "error": e.message, "platform": platform}
        
    except ParserError as e:
        logger.error(f"❌ [{platform}] Ошибка парсинга: {e.message}")
        raise self.retry(exc=e, countdown=60)
        
    except Exception as exc:
        logger.error(f"❌ [{platform}] Неизвестная ошибка: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)

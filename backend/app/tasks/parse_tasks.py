"""Celery задачи для парсеров"""

from app.tasks.celery_app import celery_app
from app.parsers.drom_apify import DromApifyParser
from app.parsers.avito_apify import AvitoApifyParser
from app.services.listing_service import ListingService
from app.core.database import SessionLocal
from app.core.logger import setup_logger
from app.core.exceptions import ParserError
import asyncio

logger = setup_logger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.parse_tasks.parse_drom_apify",
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def parse_drom_apify(self, params: dict):
    """Парсинг Дрома через Apify"""
    try:
        # Запускаем асинхронный парсинг
        async def run_parser():
            parser = DromApifyParser()
            return await parser.parse_search(params)
        
        listings = asyncio.run(run_parser())
        
        if not listings:
            logger.warning("Парсер не вернул объявлений")
            return {"status": "completed", "count": 0}
        
        # Сохраняем синхронно (для Celery)
        db = SessionLocal()
        try:
            service = ListingService()
            saved = service.save_listings_sync(db, listings)
            count = len(saved)
        finally:
            db.close()
        
        logger.info(f"✅ Парсинг Дрома завершён. Сохранено: {count}")
        return {"status": "completed", "count": count}
        
    except ParserError as e:
        logger.error(f"❌ Ошибка парсинга Дрома: {e.message}")
        raise self.retry(exc=e, countdown=60)
    except Exception as exc:
        logger.error(f"❌ Неизвестная ошибка парсинга Дрома: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(
    bind=True,
    name="app.tasks.parse_tasks.parse_avito_apify",
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def parse_avito_apify(self, params: dict):
    """Парсинг Авито через Apify"""
    try:
        async def run_parser():
            parser = AvitoApifyParser()
            return await parser.parse_search(params)
        
        listings = asyncio.run(run_parser())
        
        if not listings:
            logger.warning("Парсер Авито не вернул объявлений")
            return {"status": "completed", "count": 0}
        
        db = SessionLocal()
        try:
            service = ListingService()
            saved = service.save_listings_sync(db, listings)
            count = len(saved)
        finally:
            db.close()
        
        logger.info(f"✅ Парсинг Авито завершён. Сохранено: {count}")
        return {"status": "completed", "count": count}
        
    except ParserError as e:
        logger.error(f"❌ Ошибка парсинга Авито: {e.message}")
        raise self.retry(exc=e, countdown=60)
    except Exception as exc:
        logger.error(f"❌ Неизвестная ошибка парсинга Авито: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)

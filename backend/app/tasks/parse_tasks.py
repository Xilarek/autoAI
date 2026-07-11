import asyncio

from app.parsers.avito import AvitoParser
from app.parsers.drom import DromParser
from app.services.listing_service import ListingService
from app.tasks.celery_app import celery_app

from app.core.database import SessionLocal
from app.core.logger import setup_logger

logger = setup_logger(__name__)


@celery_app.task(
    bind=True,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    name="app.tasks.parse_tasks.parse_avito",
)
def parse_avito(self, params: dict):
    """Парсинг Авито"""
    try:

        async def run():
            parser = AvitoParser()
            listings = await parser.parse_search(params)
            db = SessionLocal()
            try:
                service = ListingService()
                saved = await service.save_listings(db, listings)
                return len(saved)
            finally:
                db.close()

        count = asyncio.run(run())
        logger.info(f"✅ Парсинг Авито завершён. Сохранено: {count}")
        return {"status": "completed", "count": count}
    except Exception as exc:
        logger.error(f"❌ Ошибка парсинга Авито: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    name="app.tasks.parse_tasks.parse_drom",
)
def parse_drom(self, params: dict):
    """Парсинг Дрома"""
    try:

        async def run():
            parser = DromParser()
            listings = await parser.parse_search(params)
            db = SessionLocal()
            try:
                service = ListingService()
                saved = await service.save_listings(db, listings)
                return len(saved)
            finally:
                db.close()

        count = asyncio.run(run())
        logger.info(f"✅ Парсинг Дрома завершён. Сохранено: {count}")
        return {"status": "completed", "count": count}
    except Exception as exc:
        logger.error(f"❌ Ошибка парсинга Дрома: {exc}", exc_info=True)
        raise self.retry(exc=exc)

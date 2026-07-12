from app.tasks.celery_app import celery_app
from app.parsers.drom_apify import DromApifyParser
from app.services.listing_service import ListingService
from app.core.database import SessionLocal
from app.core.logger import setup_logger
import asyncio

logger = setup_logger(__name__)

@celery_app.task(
    bind=True,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    name="app.tasks.parse_tasks.parse_drom_apify"
)
def parse_drom_apify(self, params: dict):
    """Парсинг Дрома через Apify"""
    try:
        async def run():
            parser = DromApifyParser()
            listings = await parser.parse_search(params)
            
            if not listings:
                logger.warning("Парсер не вернул объявлений")
                return 0
            
            db = SessionLocal()
            try:
                service = ListingService()
                saved = await service.save_listings(db, listings)
                return len(saved)
            finally:
                db.close()
        
        count = asyncio.run(run())
        logger.info(f"✅ Парсинг Дрома через Apify завершён. Сохранено: {count}")
        return {"status": "completed", "count": count}
    except Exception as exc:
        logger.error(f"❌ Ошибка парсинга Дрома: {exc}", exc_info=True)
        raise self.retry(exc=exc)

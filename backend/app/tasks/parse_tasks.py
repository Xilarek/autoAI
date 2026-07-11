from app.tasks.celery_app import celery_app
from app.parsers.avito import AvitoParser
from app.services.listing_service import ListingService
from app.core.database import SessionLocal

@celery_app.task(bind=True, max_retries=3, name="app.tasks.parse_tasks.parse_avito")
def parse_avito(self, params: dict):
    """Фоновая задача: Парсинг Авито"""
    try:
        # Создаем синхронную версию парсера
        import asyncio
        
        async def run_parser():
            parser = AvitoParser()
            listings = await parser.parse_search(params)
            
            # Сохраняем в БД
            db = SessionLocal()
            try:
                service = ListingService()
                saved = await service.save_listings(db, listings)
                return len(saved)
            finally:
                db.close()
        
        count = asyncio.run(run_parser())
        
        print(f"✅ Парсинг завершен. Сохранено объявлений: {count}")
        return {"status": "completed", "count": count}
        
    except Exception as exc:
        print(f"❌ Ошибка парсинга: {exc}")
        raise self.retry(exc=exc, countdown=60)
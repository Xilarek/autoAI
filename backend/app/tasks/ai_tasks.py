"""Celery задачи для AI-анализа"""

from app.tasks.celery_app import celery_app
from app.services.car_listing_analyzer import CarListingAnalyzer
from app.core.database import SessionLocal
from app.models.car_listing import CarListing
from sqlalchemy import select
from app.core.logger import setup_logger
import asyncio

logger = setup_logger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.ai_tasks.run_deep_analysis",
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def run_deep_analysis(self, listing_id: int):
    """Запуск AI-анализа объявления"""
    try:
        async def run():
            db = SessionLocal()
            try:
                result = await db.execute(
                    select(CarListing).where(CarListing.id == listing_id)
                )
                listing = result.scalar_one_or_none()
                
                if not listing:
                    logger.error(f"Объявление {listing_id} не найдено")
                    return {"status": "error", "message": "Listing not found"}
                
                analyzer = CarListingAnalyzer()
                analysis = await analyzer.analyze_listing({
                    "brand": listing.brand,
                    "model": listing.model,
                    "year": listing.year,
                    "price_rub": listing.price_rub,
                    "mileage": listing.mileage,
                    "description": listing.description or "",
                })
                
                listing.ai_summary = analysis.get("summary")
                listing.ai_risks = analysis.get("risks", [])
                listing.ai_verdict = analysis.get("verdict")
                listing.fair_price = analysis.get("market_price")
                
                await db.commit()
                
                logger.info(f"✅ AI-анализ завершён для {listing_id}: {analysis.get('verdict')}")
                return {"status": "completed", "verdict": analysis.get("verdict")}
                
            except Exception as e:
                await db.rollback()
                raise e
            finally:
                db.close()
        
        result = asyncio.run(run())
        return result
        
    except Exception as exc:
        logger.error(f"❌ Ошибка AI-анализа {listing_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)

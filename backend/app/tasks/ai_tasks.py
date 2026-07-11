import asyncio

from app.models.car_listing import CarListing
from app.services.car_listing_analyzer import CarListingAnalyzer
from app.tasks.celery_app import celery_app
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.logger import setup_logger

logger = setup_logger(__name__)


@celery_app.task(
    bind=True,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    name="app.tasks.ai_tasks.run_deep_analysis",
)
def run_deep_analysis(self, listing_id: int):
    """AI-анализ объявления"""
    try:

        async def analyze():
            db = SessionLocal()
            try:
                result = db.execute(select(CarListing).where(CarListing.id == listing_id))
                listing = result.scalar_one_or_none()

                if not listing:
                    logger.warning(f"Объявление {listing_id} не найдено")
                    return

                listing_dict = {
                    "brand": listing.brand,
                    "model": listing.model,
                    "year": listing.year,
                    "mileage": listing.mileage or 0,
                    "engine_volume": listing.engine_volume or 0,
                    "fuel_type": listing.fuel_type or "",
                    "transmission": listing.transmission or "",
                    "region": listing.region or "",
                    "price_rub": float(listing.price_rub) if listing.price_rub else 0,
                    "description": listing.description or "",
                }

                analyzer = CarListingAnalyzer()
                analysis = await analyzer.analyze_listing(listing_dict)

                listing.ai_summary = analysis.get("summary", "")
                listing.ai_risks = analysis.get("risks", [])
                listing.ai_verdict = analysis.get("verdict", "ТОРГОВАТЬСЯ")
                listing.fair_price = analysis.get("market_price", 0)
                listing.value_score = analysis.get("score", 0.5)

                db.commit()

                logger.info(f"✅ Анализ завершён: {listing.brand} {listing.model} -> {listing.ai_verdict}")
                return analysis

            finally:
                db.close()

        result = asyncio.run(analyze())
        return {"status": "completed", "listing_id": listing_id, "result": result}

    except Exception as exc:
        logger.error(f"❌ Ошибка анализа {listing_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc)

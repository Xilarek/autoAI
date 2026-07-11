from app.tasks.celery_app import celery_app
from app.services.ai_agent import AiAgent
from app.models.car_listing import CarListing
from app.core.database import SessionLocal
from sqlalchemy import select
import asyncio
import json

@celery_app.task(bind=True, max_retries=3, name="app.tasks.ai_tasks.run_deep_analysis")
def run_deep_analysis(self, listing_id: int):
    """AI-анализ объявления"""
    try:
        async def analyze():
            db = SessionLocal()
            try:
                result = db.execute(
                    select(CarListing).where(CarListing.id == listing_id)
                )
                listing = result.scalar_one_or_none()
                
                if not listing:
                    print(f"Объявление {listing_id} не найдено")
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
                    "price_rub": listing.price_rub or 0,
                    "description": listing.description or "",
                }
                
                agent = AiAgent()
                analysis = await agent.analyze_listing(listing_dict)
                
                # Сохраняем результаты
                listing.ai_summary = analysis.get("summary", "")
                # Риски как JSON-массив (не строка!)
                listing.ai_risks = analysis.get("risks", [])
                listing.ai_verdict = analysis.get("verdict", "ТОРГОВАТЬСЯ")
                listing.fair_price = analysis.get("market_price", 0)
                listing.value_score = analysis.get("score", 0.5)
                
                db.commit()
                
                print(f"Анализ завершён: {listing.brand} {listing.model} -> {listing.ai_verdict}")
                return analysis
                
            finally:
                db.close()
        
        result = asyncio.run(analyze())
        return {"status": "completed", "listing_id": listing_id, "result": result}
        
    except Exception as exc:
        print(f"Ошибка анализа: {exc}")
        raise self.retry(exc=exc, countdown=60)

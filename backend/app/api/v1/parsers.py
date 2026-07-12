from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.parsers.drom_apify import DromApifyParser
from app.services.listing_service import ListingService
from app.schemas.search import SearchParams
from app.core.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/drom/search")
async def search_drom(
    params: SearchParams,
    db: AsyncSession = Depends(get_db)
):
    """Поиск на Дроме через Apify"""
    try:
        parser = DromApifyParser()
        listings = await parser.parse_search(params.dict())
        
        if not listings:
            logger.warning("Парсер не вернул объявлений")
            return {
                "count": 0,
                "listings": [],
                "message": "Не удалось получить объявления. Проверьте APIFY_TOKEN."
            }
        
        service = ListingService()
        saved = await service.save_listings(db, listings)
        
        logger.info(f"Дром: найдено {len(saved)} объявлений")
        
        return {
            "count": len(saved),
            "listings": [
                {
                    "id": listing.id,
                    "brand": listing.brand,
                    "model": listing.model,
                    "year": listing.year,
                    "price": int(listing.price_rub) if listing.price_rub else 0,
                    "url": listing.url
                }
                for listing in saved
            ]
        }
    except Exception as e:
        logger.error(f"Ошибка парсинга Дрома: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

@router.post("/drom/parse-task")
async def start_drom_parsing(params: SearchParams, background_tasks: BackgroundTasks):
    """Запустить парсинг Дрома в фоне"""
    from app.tasks.parse_tasks import parse_drom_apify
    task = parse_drom_apify.delay(params.dict())
    return {"status": "queued", "task_id": task.id}

from app.api.deps.auth import require_api_key
from app.parsers.avito import AvitoParser
from app.parsers.drom import DromParser
from app.schemas.search import SearchParams
from app.services.listing_service import ListingService
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


@router.post("/avito/search")
async def search_avito(params: SearchParams, db: AsyncSession = Depends(get_db)):
    """Поиск на Авито"""
    try:
        parser = AvitoParser()
        listings = await parser.parse_search(params.dict())

        service = ListingService()
        saved = await service.save_listings(db, listings)

        logger.info(f"Авито: найдено {len(saved)} объявлений")

        return {
            "count": len(saved),
            "listings": [
                {
                    "id": listing.id,
                    "brand": listing.brand,
                    "model": listing.model,
                    "year": listing.year,
                    "price": int(listing.price_rub) if listing.price_rub else 0,
                    "url": listing.url,
                }
                for listing in saved
            ],
        }
    except Exception as e:
        logger.error(f"Ошибка парсинга Авито: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Parsing failed")


@router.post("/drom/search")
async def search_drom(params: SearchParams, db: AsyncSession = Depends(get_db)):
    """Поиск на Дроме"""
    try:
        parser = DromParser()
        listings = await parser.parse_search(params.dict())

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
                    "url": listing.url,
                }
                for listing in saved
            ],
        }
    except Exception as e:
        logger.error(f"Ошибка парсинга Дрома: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Parsing failed")


@router.post("/avito/parse-task", dependencies=[Depends(require_api_key)])
async def start_avito_parsing(params: SearchParams, background_tasks: BackgroundTasks):
    """Запустить парсинг Авито в фоне"""
    from app.tasks.parse_tasks import parse_avito

    task = parse_avito.delay(params.dict())
    return {"status": "queued", "task_id": task.id}


@router.post("/drom/parse-task", dependencies=[Depends(require_api_key)])
async def start_drom_parsing(params: SearchParams, background_tasks: BackgroundTasks):
    """Запустить парсинг Дрома в фоне"""
    from app.tasks.parse_tasks import parse_drom

    task = parse_drom.delay(params.dict())
    return {"status": "queued", "task_id": task.id}

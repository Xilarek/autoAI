from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.parsers.avito import AvitoParser
from app.parsers.drom import DromParser
from app.services.listing_service import ListingService

router = APIRouter()

@router.post("/avito/search")
async def search_avito(
    params: dict,
    db: AsyncSession = Depends(get_db)
):
    """Поиск на Авито"""
    parser = AvitoParser()
    listings = await parser.parse_search(params)
    
    service = ListingService()
    saved = await service.save_listings(db, listings)
    
    return {
        "count": len(saved),
        "listings": [
            {
                "id": listing.id,
                "brand": listing.brand,
                "model": listing.model,
                "year": listing.year,
                "price": listing.price_rub,
                "url": listing.url
            }
            for listing in saved
        ]
    }

@router.post("/drom/search")
async def search_drom(
    params: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Поиск на Дроме
    
    Пример params:
    {
        "query": "Toyota Tiguan",
        "region": "moscow",
        "price_max": 2500000,
        "year_min": 2018
    }
    """
    parser = DromParser()
    listings = await parser.parse_search(params)
    
    service = ListingService()
    saved = await service.save_listings(db, listings)
    
    return {
        "count": len(saved),
        "listings": [
            {
                "id": listing.id,
                "brand": listing.brand,
                "model": listing.model,
                "year": listing.year,
                "price": listing.price_rub,
                "url": listing.url
            }
            for listing in saved
        ]
    }

@router.post("/avito/parse-task")
async def start_avito_parsing(
    params: dict,
    background_tasks: BackgroundTasks
):
    """Запустить парсинг Авито в фоне"""
    from app.tasks.parse_tasks import parse_avito
    task = parse_avito.delay(params)
    return {
        "status": "queued",
        "task_id": task.id
    }

@router.post("/drom/parse-task")
async def start_drom_parsing(
    params: dict,
    background_tasks: BackgroundTasks
):
    """Запустить парсинг Дрома в фоне"""
    from app.tasks.parse_tasks import parse_drom
    task = parse_drom.delay(params)
    return {
        "status": "queued",
        "task_id": task.id
    }

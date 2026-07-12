"""API endpoints для парсеров"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from celery.result import AsyncResult
from app.core.database import get_db
from app.schemas.search import SearchParams
from app.core.rate_limit import limiter
from app.core.logger import setup_logger
from app.core.exceptions import ParserError

logger = setup_logger(__name__)
router = APIRouter()


@router.post("/drom/search")
@limiter.limit("10/minute")
async def search_drom(request: Request, params: SearchParams):
    """Запустить парсинг Дрома в фоне (асинхронно)"""
    from app.tasks.parse_tasks import parse_drom_apify
    
    task = parse_drom_apify.delay(params.dict())
    
    logger.info(f"🚀 Запущен парсинг Дрома: task_id={task.id}")
    
    return {
        "status": "queued",
        "task_id": task.id,
        "message": "Парсинг запущен в фоне. Используйте /tasks/{task_id} для получения результата."
    }


@router.post("/avito/search")
@limiter.limit("10/minute")
async def search_avito(request: Request, params: SearchParams):
    """Запустить парсинг Авито в фоне (асинхронно)"""
    from app.tasks.parse_tasks import parse_avito_apify
    
    task = parse_avito_apify.delay(params.dict())
    
    logger.info(f"🚀 Запущен парсинг Авито: task_id={task.id}")
    
    return {
        "status": "queued",
        "task_id": task.id,
        "message": "Парсинг запущен в фоне. Используйте /tasks/{task_id} для получения результата."
    }


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str, db: AsyncSession = Depends(get_db)):
    """Получить статус задачи парсинга"""
    from sqlalchemy import select
    from app.models.car_listing import CarListing
    
    result = AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": result.status,  # PENDING, STARTED, SUCCESS, FAILURE, RETRY
    }
    
    if result.status == "SUCCESS":
        task_result = result.result
        response["result"] = task_result
        
        # Получить свежие объявления из БД
        db_result = await db.execute(
            select(CarListing)
            .where(CarListing.is_deleted == False)
            .order_by(CarListing.id.desc())
            .limit(task_result.get("count", 20))
        )
        listings = db_result.scalars().all()
        
        response["listings"] = [
            {
                "id": listing.id,
                "brand": listing.brand,
                "model": listing.model,
                "year": listing.year,
                "price": int(listing.price_rub) if listing.price_rub else 0,
                "url": listing.url,
                "source": listing.source,
            }
            for listing in listings
        ]
    
    elif result.status == "FAILURE":
        response["error"] = str(result.result)
    
    return response


@router.get("/tasks")
async def list_recent_tasks():
    """Список последних задач (упрощённо)"""
    from app.tasks.celery_app import celery_app
    
    inspector = celery_app.control.inspect()
    
    return {
        "active": inspector.active() or {},
        "scheduled": inspector.scheduled() or {},
        "reserved": inspector.reserved() or {},
    }

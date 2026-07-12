"""
Универсальный API для всех площадок.

Архитектура:
- POST /parsers/{platform}/search — универсальный endpoint для ЛЮБОЙ площадки
- GET  /parsers/platforms — список всех поддерживаемых площадок
- GET  /parsers/tasks/{task_id} — статус задачи
- GET  /parsers/tasks — список активных задач

Обратная совместимость:
- POST /parsers/drom/search → перенаправляет на универсальный
- POST /parsers/avito/search → перенаправляет на универсальный
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Path
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.core.database import get_db
from app.schemas.search import SearchParams
from app.core.rate_limit import limiter
from app.core.logger import setup_logger
from app.parsers import get_parser, list_platforms
from app.tasks.parse_tasks import parse_listing

logger = setup_logger(__name__)
router = APIRouter()


class ParseResponse(BaseModel):
    """Ответ на запрос парсинга"""
    status: str
    task_id: str
    platform: str
    message: str


# ============================================
# УНИВЕРСАЛЬНЫЙ ENDPOINT (главное!)
# ============================================

@router.post("/{platform}/search", response_model=ParseResponse)
@limiter.limit("10/minute")
async def search_listing(
    request: Request,
    platform: str = Path(..., description="Площадка: drom, avito, auto_ru"),
    params: SearchParams = None,
):
    """
    Универсальный endpoint для парсинга ЛЮБОЙ площадки.
    
    Примеры:
    - POST /parsers/drom/search
    - POST /parsers/avito/search
    - POST /parsers/auto_ru/search (когда добавим)
    """
    
    # Валидация площадки
    if platform not in list_platforms():
        available = ", ".join(list_platforms())
        raise HTTPException(
            status_code=400,
            detail=f"Unknown platform: '{platform}'. Available: {available}"
        )
    
    # Запускаем универсальную задачу в фоне
    task = parse_listing.delay(platform, params.dict())
    
    logger.info(f"🚀 Запущен парсинг {platform}: task_id={task.id}")
    
    return ParseResponse(
        status="queued",
        task_id=task.id,
        platform=platform,
        message=f"Парсинг {platform} запущен в фоне. Используйте /parsers/tasks/{{task_id}} для статуса."
    )


# ============================================
# СТАТУС ЗАДАЧ
# ============================================

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str, db: AsyncSession = Depends(get_db)):
    """Получить статус задачи парсинга"""
    from celery.result import AsyncResult
    from sqlalchemy import select
    from app.models.car_listing import CarListing
    from app.tasks.celery_app import celery_app
    
    result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": result.status,
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
    """Список последних задач"""
    from app.tasks.celery_app import celery_app
    
    inspector = celery_app.control.inspect()
    
    return {
        "active": inspector.active() or {},
        "scheduled": inspector.scheduled() or {},
        "reserved": inspector.reserved() or {},
    }


# ============================================
# СПИСОК ПЛОЩАДОК
# ============================================

@router.get("/platforms")
async def get_platforms():
    """Список всех поддерживаемых площадок"""
    platforms = list_platforms()
    return {
        "platforms": platforms,
        "count": len(platforms)
    }

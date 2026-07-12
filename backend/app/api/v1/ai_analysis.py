"""API endpoints для AI-анализа"""

from fastapi import APIRouter, Depends, BackgroundTasks, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.core.database import get_db
from app.models.car_listing import CarListing
from app.services.car_listing_analyzer import CarListingAnalyzer
from app.tasks.ai_tasks import run_deep_analysis
from app.schemas.search import ListingOut, ReportsResponse
from app.api.deps.auth import require_api_key
from app.core.cache import cached
from app.core.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/analyze/{listing_id}", dependencies=[Depends(require_api_key)])
async def analyze_listing(
    listing_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Запуск AI-анализа одного объявления"""
    result = await db.execute(select(CarListing).where(CarListing.id == listing_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Listing not found")
    
    background_tasks.add_task(run_deep_analysis, listing_id)
    return {"status": "queued", "listing_id": listing_id}

@router.post("/analyze-all", dependencies=[Depends(require_api_key)])
async def analyze_all_listings(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Запуск AI-анализа всех объявлений"""
    result = await db.execute(
        select(CarListing).where(CarListing.is_deleted == False)
    )
    listings = result.scalars().all()
    
    task_ids = []
    for listing in listings:
        task = run_deep_analysis.delay(listing.id)
        task_ids.append({"listing_id": listing.id, "task_id": task.id})
    
    logger.info(f"Запущен анализ {len(listings)} объявлений")
    
    return {
        "status": "queued",
        "total": len(listings),
        "tasks": task_ids
    }

@router.get("/report/{listing_id}", response_model=ListingOut)
@cached(ttl=300)  # Кэш на 5 минут
async def get_report(listing_id: int, db: AsyncSession = Depends(get_db)):
    """Получение отчёта"""
    result = await db.execute(
        select(CarListing).where(CarListing.id == listing_id)
    )
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    risks = listing.ai_risks if isinstance(listing.ai_risks, list) else []
    
    return ListingOut(
        id=listing.id,
        brand=listing.brand,
        model=listing.model,
        year=listing.year,
        price=int(listing.price_rub) if listing.price_rub else 0,
        mileage=listing.mileage,
        region=listing.region,
        market_price=int(listing.fair_price) if listing.fair_price else 0,
        verdict=listing.ai_verdict,
        summary=listing.ai_summary or "",
        risks=risks,
        url=listing.url
    )

@router.get("/reports", response_model=ReportsResponse)
@cached(ttl=60)  # Кэш на 1 минуту
async def get_all_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    verdict: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("price", pattern="^(price|year|created_at)$"),
    sort_order: Optional[str] = Query("asc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    """Получение всех отчётов с пагинацией и фильтрацией"""
    
    query = select(CarListing).where(
        CarListing.is_deleted == False,
        CarListing.ai_verdict.isnot(None)
    )
    
    if verdict:
        normalized_verdict = CarListingAnalyzer.normalize_verdict(verdict)
        query = query.where(CarListing.ai_verdict == normalized_verdict)
    
    if brand:
        query = query.where(CarListing.brand.ilike(f"%{brand}%"))
    if model:
        query = query.where(CarListing.model.ilike(f"%{model}%"))
    if region:
        query = query.where(CarListing.region.ilike(f"%{region}%"))
    
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar()
    
    sort_column = getattr(CarListing, sort_by, CarListing.price_rub)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    listings = result.scalars().all()
    
    reports = []
    for listing in listings:
        risks = listing.ai_risks if isinstance(listing.ai_risks, list) else []
        reports.append(ListingOut(
            id=listing.id,
            brand=listing.brand,
            model=listing.model,
            year=listing.year,
            price=int(listing.price_rub) if listing.price_rub else 0,
            mileage=listing.mileage,
            region=listing.region,
            market_price=int(listing.fair_price) if listing.fair_price else 0,
            verdict=listing.ai_verdict,
            summary=listing.ai_summary or "",
            risks=risks,
            url=listing.url
        ))
    
    page = (skip // limit) + 1 if limit > 0 else 1
    
    return ReportsResponse(
        count=len(reports),
        total=total,
        page=page,
        per_page=limit,
        reports=reports
    )

@router.post("/cache/invalidate", dependencies=[Depends(require_api_key)])
async def invalidate_cache():
    """Инвалидация всего кэша"""
    from app.core.cache import cache
    try:
        await cache.clear()
        return {"status": "ok", "message": "Cache invalidated"}
    except Exception as e:
        logger.error(f"Ошибка инвалидации кэша: {e}")
        raise HTTPException(status_code=500, detail=str(e))

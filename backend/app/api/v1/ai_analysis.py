from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.car_listing import CarListing
from app.services.ai_agent import AiAgent
from app.tasks.ai_tasks import run_deep_analysis
from typing import List

router = APIRouter()

@router.post("/analyze/{listing_id}")
async def analyze_listing(
    listing_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Запуск AI-анализа одного объявления"""
    background_tasks.add_task(run_deep_analysis, listing_id)
    return {
        "status": "queued",
        "listing_id": listing_id
    }

@router.post("/analyze-all")
async def analyze_all_listings(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Запуск AI-анализа всех объявлений"""
    
    result = await db.execute(select(CarListing))
    listings = result.scalars().all()
    
    task_ids = []
    for listing in listings:
        task = run_deep_analysis.delay(listing.id)
        task_ids.append({"listing_id": listing.id, "task_id": task.id})
    
    return {
        "status": "queued",
        "total": len(listings),
        "tasks": task_ids
    }

@router.get("/report/{listing_id}")
async def get_report(listing_id: int, db: AsyncSession = Depends(get_db)):
    """Получение отчёта"""
    agent = AiAgent()
    return await agent.get_report(db, listing_id)

@router.get("/reports")
async def get_all_reports(db: AsyncSession = Depends(get_db)):
    """Получение всех отчётов — чистый формат"""
    
    result = await db.execute(select(CarListing))
    listings = result.scalars().all()
    
    reports = []
    for listing in listings:
        if listing.ai_verdict:
            # ai_risks уже массив, не нужно парсить
            risks = listing.ai_risks if isinstance(listing.ai_risks, list) else []
            
            reports.append({
                "id": listing.id,
                "brand": listing.brand,
                "model": listing.model,
                "year": listing.year,
                "price": int(listing.price_rub) if listing.price_rub else 0,
                "mileage": int(listing.mileage) if listing.mileage else 0,
                "region": listing.region or "",
                "market_price": int(listing.fair_price) if listing.fair_price else 0,
                "verdict": listing.ai_verdict,
                "summary": listing.ai_summary or "",
                "risks": risks,
                "url": listing.url
            })
    
    return {
        "count": len(reports),
        "reports": reports
    }

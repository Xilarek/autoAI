from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.car_listing import CarListing

router = APIRouter()

@router.get("/")
async def get_listings(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Получить список объявлений"""
    result = await db.execute(select(CarListing).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{listing_id}")
async def get_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
    """Получить объявление по ID"""
    result = await db.execute(select(CarListing).where(CarListing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing

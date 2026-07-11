from typing import Optional

from app.models.car_listing import CarListing
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/")
async def get_listings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    brand: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Получить список объявлений"""
    query = select(CarListing).where(CarListing.is_deleted == False)

    if brand:
        query = query.where(CarListing.brand.ilike(f"%{brand}%"))

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{listing_id}")
async def get_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
    """Получить объявление по ID"""
    result = await db.execute(select(CarListing).where(CarListing.id == listing_id, CarListing.is_deleted == False))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.delete("/{listing_id}")
async def delete_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
    """Soft delete объявления"""
    result = await db.execute(select(CarListing).where(CarListing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    from sqlalchemy import func

    listing.is_deleted = True
    listing.deleted_at = func.now()
    await db.commit()

    return {"status": "deleted", "id": listing_id}

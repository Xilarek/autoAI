from typing import Any, Dict, List

from app.models.car_listing import CarListing, SourcePlatform
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.logger import setup_logger

logger = setup_logger(__name__)


class ListingService:
    """Сервис для работы с объявлениями"""

    # Асинхронные методы (для FastAPI)
    
    async def save_listings(self, db: AsyncSession, listings: List[Dict[str, Any]]) -> List[CarListing]:
        """Сохраняем объявления в БД (асинхронно)"""
        saved = []

        for listing_data in listings:
            source_str = listing_data.get("source", "avito")
            source = SourcePlatform.AVITO if source_str == "avito" else SourcePlatform.DROM

            result = await db.execute(
                select(CarListing).where(
                    CarListing.external_id == listing_data["external_id"], 
                    CarListing.source == source.value
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                for key, value in listing_data.items():
                    if hasattr(existing, key) and key not in ["id", "source", "external_id"]:
                        setattr(existing, key, value)
                existing.is_deleted = False
                saved.append(existing)
            else:
                listing = CarListing(
                    external_id=listing_data["external_id"],
                    source=source.value,
                    url=listing_data.get("url"),
                    brand=listing_data.get("brand"),
                    model=listing_data.get("model"),
                    year=listing_data.get("year"),
                    mileage=listing_data.get("mileage"),
                    engine_volume=listing_data.get("engine_volume"),
                    fuel_type=listing_data.get("fuel_type"),
                    transmission=listing_data.get("transmission"),
                    body_type=listing_data.get("body_type"),
                    vin=listing_data.get("vin"),
                    region=listing_data.get("region"),
                    price_rub=listing_data.get("price_rub"),
                    description=listing_data.get("description"),
                    photos=listing_data.get("photos"),
                    seller_info=listing_data.get("seller_info"),
                )
                db.add(listing)
                saved.append(listing)

        await db.commit()

        for listing in saved:
            if not listing.id:
                await db.refresh(listing)

        logger.info(f"Сохранено {len(saved)} объявлений")
        return saved

    async def get_listings(self, db: AsyncSession, skip: int = 0, limit: int = 20) -> List[CarListing]:
        """Получаем список объявлений (асинхронно)"""
        result = await db.execute(
            select(CarListing).where(CarListing.is_deleted == False).offset(skip).limit(limit)
        )
        return result.scalars().all()

    # Синхронные методы (для Celery)
    
    def save_listings_sync(self, db: Session, listings: List[Dict[str, Any]]) -> List[CarListing]:
        """Сохраняем объявления в БД (синхронно для Celery)"""
        saved = []

        for listing_data in listings:
            source_str = listing_data.get("source", "avito")
            source = SourcePlatform.AVITO if source_str == "avito" else SourcePlatform.DROM

            result = db.execute(
                select(CarListing).where(
                    CarListing.external_id == listing_data["external_id"], 
                    CarListing.source == source.value
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                for key, value in listing_data.items():
                    if hasattr(existing, key) and key not in ["id", "source", "external_id"]:
                        setattr(existing, key, value)
                existing.is_deleted = False
                saved.append(existing)
            else:
                listing = CarListing(
                    external_id=listing_data["external_id"],
                    source=source.value,
                    url=listing_data.get("url"),
                    brand=listing_data.get("brand"),
                    model=listing_data.get("model"),
                    year=listing_data.get("year"),
                    mileage=listing_data.get("mileage"),
                    engine_volume=listing_data.get("engine_volume"),
                    fuel_type=listing_data.get("fuel_type"),
                    transmission=listing_data.get("transmission"),
                    body_type=listing_data.get("body_type"),
                    vin=listing_data.get("vin"),
                    region=listing_data.get("region"),
                    price_rub=listing_data.get("price_rub"),
                    description=listing_data.get("description"),
                    photos=listing_data.get("photos"),
                    seller_info=listing_data.get("seller_info"),
                )
                db.add(listing)
                saved.append(listing)

        db.commit()

        for listing in saved:
            if not listing.id:
                db.refresh(listing)

        logger.info(f"Сохранено {len(saved)} объявлений")
        return saved

    def get_listings_sync(self, db: Session, skip: int = 0, limit: int = 20) -> List[CarListing]:
        """Получаем список объявлений (синхронно для Celery)"""
        result = db.execute(
            select(CarListing).where(CarListing.is_deleted == False).offset(skip).limit(limit)
        )
        return result.scalars().all()

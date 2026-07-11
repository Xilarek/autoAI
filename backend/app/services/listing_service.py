from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.car_listing import CarListing, SourcePlatform
from typing import List, Dict, Any

class ListingService:
    """Сервис для работы с объявлениями"""
    
    async def save_listings(self, db: AsyncSession, listings: List[Dict[str, Any]]) -> List[CarListing]:
        """Сохраняем объявления в БД"""
        
        saved = []
        
        for listing_data in listings:
            source_str = listing_data.get("source", "avito")
            source = SourcePlatform.AVITO if source_str == "avito" else SourcePlatform.DROM
            
            result = await db.execute(
                select(CarListing).where(
                    CarListing.external_id == listing_data["external_id"],
                    CarListing.source == source
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                for key, value in listing_data.items():
                    if hasattr(existing, key) and key not in ['id', 'source']:
                        setattr(existing, key, value)
                saved.append(existing)
            else:
                listing = CarListing(
                    external_id=listing_data["external_id"],
                    source=source,
                    url=listing_data["url"],
                    brand=listing_data["brand"],
                    model=listing_data["model"],
                    year=listing_data["year"],
                    mileage=listing_data["mileage"],
                    engine_volume=listing_data["engine_volume"],
                    fuel_type=listing_data["fuel_type"],
                    transmission=listing_data["transmission"],
                    body_type=listing_data["body_type"],
                    vin=listing_data["vin"],
                    region=listing_data["region"],
                    price_rub=listing_data["price_rub"],
                    description=listing_data["description"],
                    photos=listing_data["photos"],
                    seller_info=listing_data["seller_info"],
                )
                db.add(listing)
                saved.append(listing)
        
        await db.commit()
        
        for listing in saved:
            if not listing.id:
                await db.refresh(listing)
        
        return saved
    
    async def get_listings(self, db: AsyncSession, skip: int = 0, limit: int = 20) -> List[CarListing]:
        """Получаем список объявлений"""
        
        result = await db.execute(
            select(CarListing).offset(skip).limit(limit)
        )
        
        return result.scalars().all()

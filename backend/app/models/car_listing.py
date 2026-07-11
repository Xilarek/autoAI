import enum
from sqlalchemy import Column, Integer, String, Float, JSON, Enum, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class SourcePlatform(str, enum.Enum):
    AVITO = "avito"
    AUTORU = "autoru"
    DROM = "drom"
    CARPRICE = "carprice"

class CarListing(Base):
    __tablename__ = "car_listings"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=False)
    source = Column(Enum(SourcePlatform), nullable=False, index=True)
    url = Column(String, nullable=False)

    # Основные характеристики
    brand = Column(String, index=True)
    model = Column(String, index=True)
    year = Column(Integer, index=True)
    mileage = Column(Integer)
    engine_volume = Column(Float)
    fuel_type = Column(String)
    transmission = Column(String)
    body_type = Column(String)
    vin = Column(String, index=True)
    region = Column(String, index=True)

    # Цена и аналитика
    price_rub = Column(Float, index=True)
    fair_price = Column(Float)
    value_score = Column(Float)

    # Контент
    description = Column(Text)
    photos = Column(JSON)
    seller_info = Column(JSON)

    # AI-анализ
    ai_summary = Column(Text)
    ai_risks = Column(JSON)
    ai_verdict = Column(String)

    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    parsed_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
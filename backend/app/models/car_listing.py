import enum

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, Numeric, String, Text
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import UniqueConstraint

from app.core.database import Base


class SourcePlatform(str, enum.Enum):
    AVITO = "avito"
    DROM = "drom"
    AUTO_RU = "auto_ru"


class CarListing(Base):
    __tablename__ = "car_listings"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), nullable=False, index=True)
    source = Column(String(20), nullable=False, index=True)

    url = Column(String(500), nullable=True)

    brand = Column(String(100), index=True)
    model = Column(String(100), index=True)
    year = Column(Integer, index=True)
    mileage = Column(Integer, nullable=True)

    engine_volume = Column(Float, nullable=True)
    fuel_type = Column(String(50), nullable=True)
    transmission = Column(String(50), nullable=True)
    body_type = Column(String(50), nullable=True)

    vin = Column(String(17), nullable=True, index=True)

    region = Column(String(100), index=True)
    price_rub = Column(Numeric(12, 2), index=True)  # Было Float
    fair_price = Column(Numeric(12, 2))  # Было Float

    description = Column(Text, nullable=True)
    photos = Column(JSON, nullable=True)
    seller_info = Column(JSON, nullable=True)

    # AI анализ
    ai_summary = Column(Text, nullable=True)
    ai_risks = Column(JSON, nullable=True)
    ai_verdict = Column(String(50), index=True, nullable=True)
    value_score = Column(Float, nullable=True)

    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Soft delete
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("external_id", "source", name="uq_listing_source"),)

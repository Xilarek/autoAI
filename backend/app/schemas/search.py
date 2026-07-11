from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SearchParams(BaseModel):
    """Параметры поиска"""

    query: str = Field(default="", max_length=200)
    region: str = Field(default="", max_length=100)
    price_max: Optional[int] = Field(default=None, gt=0, lt=1_000_000_000)
    price_min: Optional[int] = Field(default=None, gt=0, lt=1_000_000_000)
    year_min: Optional[int] = Field(default=None, ge=1950, le=2030)
    year_max: Optional[int] = Field(default=None, ge=1950, le=2030)
    brand: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)


class ListingOut(BaseModel):
    """Выходная схема объявления"""

    id: int
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: int
    mileage: Optional[int] = None
    region: Optional[str] = None
    market_price: Optional[int] = None
    verdict: Optional[str] = None
    summary: Optional[str] = None
    risks: List[dict] = []
    url: Optional[str] = None

    class Config:
        from_attributes = True


class ReportsResponse(BaseModel):
    """Ответ со списком отчётов"""

    count: int
    total: int
    page: int
    per_page: int
    reports: List[ListingOut]


class HealthResponse(BaseModel):
    """Ответ health check"""

    status: str
    version: str

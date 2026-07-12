"""Pydantic схемы для поиска и объявлений"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class SearchParams(BaseModel):
    """
    Параметры поиска объявлений.
    
    Все поля опциональные, кроме query и region.
    Валидация только если поле передано (не None).
    """
    
    query: str = Field(default="", description="Поисковый запрос (марка модель)")
    region: str = Field(default="moscow", description="Регион поиска")
    
    # Опциональные фильтры
    price_min: Optional[int] = Field(
        default=None, 
        description="Минимальная цена (₽)",
        gt=0,
        examples=[1000000]
    )
    price_max: Optional[int] = Field(
        default=None, 
        description="Максимальная цена (₽)",
        gt=0,
        examples=[5000000]
    )
    year_min: Optional[int] = Field(
        default=None, 
        description="Минимальный год выпуска",
        ge=1980,
        le=2027,
        examples=[2015]
    )
    year_max: Optional[int] = Field(
        default=None, 
        description="Максимальный год выпуска",
        ge=1980,
        le=2027,
        examples=[2025]
    )
    brand: Optional[str] = Field(
        default=None, 
        description="Марка автомобиля",
        examples=["Toyota"]
    )
    model: Optional[str] = Field(
        default=None, 
        description="Модель автомобиля",
        examples=["Camry"]
    )
    
    @field_validator("year_max")
    @classmethod
    def validate_year_range(cls, v, info):
        """Проверка, что year_max >= year_min"""
        year_min = info.data.get("year_min")
        if v is not None and year_min is not None and v < year_min:
            raise ValueError("year_max must be >= year_min")
        return v
    
    @field_validator("price_max")
    @classmethod
    def validate_price_range(cls, v, info):
        """Проверка, что price_max >= price_min"""
        price_min = info.data.get("price_min")
        if v is not None and price_min is not None and v < price_min:
            raise ValueError("price_max must be >= price_min")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Toyota Camry",
                "region": "moscow",
                "year_min": 2020,
                "year_max": 2025,
                "price_min": 1500000,
                "price_max": 3000000
            }
        }


class ListingOut(BaseModel):
    """Выходная схема объявления"""
    id: int
    brand: str
    model: str
    year: int
    price: int
    mileage: Optional[int] = 0
    region: Optional[str] = ""
    market_price: Optional[int] = 0
    verdict: Optional[str] = None
    summary: Optional[str] = ""
    risks: Optional[List[str]] = []
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

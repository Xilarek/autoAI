"""Алиас для обратной совместимости. Используйте CarListingAnalyzer."""

from app.services.car_listing_analyzer import CarListingAnalyzer

# Алиас для совместимости
AiAgent = CarListingAnalyzer

__all__ = ["AiAgent", "CarListingAnalyzer"]

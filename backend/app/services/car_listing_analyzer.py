"""Анализатор объявлений автомобилей (rule-based)"""

from typing import Dict, Any, List
from datetime import datetime
from app.core.logger import setup_logger
from app.constants.market_prices import (
    MARKET_PRICES, BASE_PRICES, PREMIUM_BRANDS, ECONOMY_BRANDS,
    NORMAL_MILEAGE_PER_YEAR, DEPRECIATION_RATE, MIN_VALUE_FACTOR
)
from app.constants.risk_markers import RISK_MARKERS, RISK_LEVELS, RISK_PENALTIES

logger = setup_logger(__name__)

# Алиасы для вердиктов (английские + русские в нижнем регистре)
VERDICT_ALIASES = {
    "call": "ЗВОНИТЬ",
    "bargain": "ТОРГОВАТЬСЯ",
    "think": "ДУМАТЬ",
    "run": "БЕЖАТЬ",
    "звонить": "ЗВОНИТЬ",
    "торговаться": "ТОРГОВАТЬСЯ",
    "думать": "ДУМАТЬ",
    "бежать": "БЕЖАТЬ",
}


class CarListingAnalyzer:
    """Rule-based анализатор объявлений автомобилей
    
    Анализирует:
    - Цену относительно рынка
    - Пробег относительно возраста
    - Риски в тексте объявления
    - Формирует итоговый вердикт
    """
    
    @staticmethod
    def normalize_verdict(verdict: str) -> str:
        """Нормализует вердикт: принимает английские/русские названия
        
        Примеры:
        - "call" → "ЗВОНИТЬ"
        - "Call" → "ЗВОНИТЬ"
        - "ЗВОНИТЬ" → "ЗВОНИТЬ"
        - "звонить" → "ЗВОНИТЬ"
        """
        if not verdict:
            return verdict
        verdict_lower = verdict.lower().strip()
        return VERDICT_ALIASES.get(verdict_lower, verdict.upper())
    
    async def analyze_listing(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """Полный анализ объявления"""
        try:
            price_analysis = self._analyze_price(listing)
            mileage_analysis = self._analyze_mileage(listing)
            risks_analysis = self._analyze_text_risks(listing)
            verdict_data = self._make_verdict(price_analysis, mileage_analysis, risks_analysis)
            summary = self._generate_summary(price_analysis, mileage_analysis, risks_analysis)
            
            logger.info(
                f"Анализ завершён: {listing.get('brand')} {listing.get('model')} -> {verdict_data['verdict']}"
            )
            
            return {
                "summary": summary,
                "price_assessment": price_analysis["assessment"],
                "mileage_assessment": mileage_analysis["assessment"],
                "market_price": price_analysis["market_price"],
                "price_difference_percent": price_analysis["difference_percent"],
                "mileage_ratio": mileage_analysis["ratio"],
                "risks": risks_analysis["risks"],
                "risk_level": risks_analysis["risk_level"],
                "verdict": verdict_data["verdict"],
                "confidence": verdict_data["confidence"],
                "recommendations": verdict_data["recommendations"]
            }
        except Exception as e:
            logger.error(f"Ошибка анализа: {e}", exc_info=True)
            raise
    
    def _analyze_price(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ цены"""
        brand = listing.get("brand", "").lower()
        model = listing.get("model", "").lower()
        year = listing.get("year", 0)
        price = int(listing.get("price_rub", 0) or 0)
        
        market_price = MARKET_PRICES.get((brand, model, year))
        if not market_price:
            market_price = self._estimate_market_price(brand, model, year)
        
        if market_price == 0 or price == 0:
            return {
                "market_price": 0,
                "listing_price": price,
                "difference_percent": 0,
                "assessment": "нет данных",
                "score": 0.5
            }
        
        difference = ((price - market_price) / market_price) * 100
        
        if difference < -15:
            assessment, score = "сильно ниже рынка", 0.3
        elif difference < -5:
            assessment, score = "ниже рынка", 0.7
        elif difference < 5:
            assessment, score = "рыночная цена", 0.9
        elif difference < 15:
            assessment, score = "выше рынка", 0.6
        else:
            assessment, score = "сильно выше рынка", 0.2
        
        return {
            "market_price": market_price,
            "listing_price": price,
            "difference_percent": round(difference, 1),
            "assessment": assessment,
            "score": score
        }
    
    def _estimate_market_price(self, brand: str, model: str, year: int) -> int:
        """Оценка рыночной цены для неизвестных моделей"""
        if brand in PREMIUM_BRANDS:
            base = BASE_PRICES["premium"]
        elif brand in ECONOMY_BRANDS:
            base = BASE_PRICES["economy"]
        else:
            base = BASE_PRICES["middle"]
        
        current_year = datetime.now().year
        age = current_year - year
        factor = max(MIN_VALUE_FACTOR, 1 - age * DEPRECIATION_RATE)
        
        return int(base * factor)
    
    def _analyze_mileage(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ пробега"""
        mileage = int(listing.get("mileage", 0) or 0)
        year = listing.get("year", 0)
        current_year = datetime.now().year
        age = current_year - year
        
        if age <= 0 or mileage <= 0:
            return {
                "mileage": mileage,
                "expected_mileage": 0,
                "ratio": 1.0,
                "assessment": "нет данных",
                "score": 0.5
            }
        
        expected_mileage = age * NORMAL_MILEAGE_PER_YEAR
        ratio = mileage / expected_mileage
        
        if ratio < 0.5:
            assessment, score = "подозрительно малый пробег", 0.4
        elif ratio < 0.8:
            assessment, score = "малый пробег", 0.8
        elif ratio < 1.3:
            assessment, score = "нормальный пробег", 0.9
        elif ratio < 2.0:
            assessment, score = "большой пробег", 0.6
        else:
            assessment, score = "очень большой пробег", 0.3
        
        return {
            "mileage": mileage,
            "expected_mileage": expected_mileage,
            "ratio": round(ratio, 2),
            "assessment": assessment,
            "score": score
        }
    
    def _analyze_text_risks(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ текста на риски"""
        description = (listing.get("description", "") or "").lower()
        risks = []
        max_risk_level = "Низкий"
        
        for marker, (level, explanation) in RISK_MARKERS.items():
            if marker in description:
                risks.append({
                    "marker": marker,
                    "level": level,
                    "explanation": explanation
                })
                if RISK_LEVELS.get(level, 0) > RISK_LEVELS.get(max_risk_level, 0):
                    max_risk_level = level
        
        if not risks:
            return {"risks": [], "risk_level": "Низкий"}
        
        return {"risks": risks, "risk_level": max_risk_level}
    
    def _make_verdict(self, price_analysis: Dict, mileage_analysis: Dict, risks_analysis: Dict) -> Dict[str, Any]:
        """Формируем вердикт"""
        scores = [
            price_analysis.get("score", 0.5),
            mileage_analysis.get("score", 0.5),
        ]
        
        risk_level = risks_analysis.get("risk_level", "Низкий")
        risk_penalty = RISK_PENALTIES.get(risk_level, 0)
        
        avg_score = max(0, min(1, sum(scores) / len(scores) - risk_penalty))
        
        if avg_score >= 0.8:
            verdict, confidence = "ЗВОНИТЬ", 0.9
            recommendations = ["Отличный вариант", "Связаться с продавцом", "Проверить авто", "Заказать отчёт по VIN"]
        elif avg_score >= 0.6:
            verdict, confidence = "ТОРГОВАТЬСЯ", 0.7
            recommendations = ["Хороший вариант с нюансами", "Возможен торг", "Требуется проверка", "Заказать отчёт по VIN"]
        elif avg_score >= 0.4:
            verdict, confidence = "ДУМАТЬ", 0.5
            recommendations = ["Есть серьёзные риски", "Требуется экспертная проверка", "Обязателен сильный торг", "Проверить документы"]
        else:
            verdict, confidence = "БЕЖАТЬ", 0.8
            recommendations = ["Высокий риск", "Не рекомендуется", "Возможны скрытые дефекты", "Искать другой вариант"]
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "score": round(avg_score, 2),
            "recommendations": recommendations
        }
    
    def _generate_summary(self, price_analysis: Dict, mileage_analysis: Dict, risks_analysis: Dict) -> str:
        """Краткий summary"""
        parts = []
        
        price_assessment = price_analysis.get("assessment", "")
        diff = price_analysis.get("difference_percent", 0)
        if price_assessment and price_assessment != "нет данных":
            if diff != 0:
                parts.append(f"{price_assessment.capitalize()} ({diff:+.1f}%)")
            else:
                parts.append(price_assessment.capitalize())
        
        mileage_assessment = mileage_analysis.get("assessment", "")
        if mileage_assessment and mileage_assessment != "нет данных":
            parts.append(mileage_assessment.capitalize())
        
        risks = risks_analysis.get("risks", [])
        risk_level = risks_analysis.get("risk_level", "Низкий")
        if not risks:
            parts.append("Рисков не выявлено")
        else:
            risk_markers = [r["marker"] for r in risks]
            parts.append(f"Риски: {', '.join(risk_markers)} ({risk_level})")
        
        return ". ".join(parts) + "."
    
    async def get_report(self, db, listing_id: int) -> Dict[str, Any]:
        """Получение отчёта из БД"""
        from app.models.car_listing import CarListing
        from sqlalchemy import select
        
        result = await db.execute(
            select(CarListing).where(CarListing.id == listing_id)
        )
        listing = result.scalar_one_or_none()
        
        if not listing:
            return {"error": "Объявление не найдено"}
        
        return {
            "id": listing.id,
            "url": listing.url,
            "brand": listing.brand,
            "model": listing.model,
            "year": listing.year,
            "price": int(listing.price_rub) if listing.price_rub else 0,
            "fair_price": int(listing.fair_price) if listing.fair_price else 0,
            "ai_summary": listing.ai_summary,
            "ai_risks": listing.ai_risks,
            "ai_verdict": listing.ai_verdict
        }

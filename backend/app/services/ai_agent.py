from typing import Dict, Any, List
import re

class AiAgent:
    """AI-агент для анализа объявлений — чистый формат"""
    
    # Маркеры рисков
    RISK_MARKERS = {
        "требует вложений": ("Высокий", "Требует финансовых вложений"),
        "косметика": ("Средний", "Возможны косметические дефекты"),
        "на ходу": ("Средний", "Акцент на исправности — подозрительно"),
        "сел и поехал": ("Средний", "Типичная фраза перекупов"),
        "не бита": ("Низкий", "Подозрительно частое упоминание"),
        "срочно": ("Низкий", "Срочная продажа — возможен торг"),
        "торг": ("Низкий", "Продавец готов к торгу"),
        "вложений": ("Высокий", "Требует финансовых вложений"),
        "гнила": ("Критический", "Коррозия кузова"),
        "ржавчин": ("Высокий", "Коррозия — требует осмотра"),
        "дтп": ("Высокий", "Упоминание ДТП"),
        "перекуп": ("Средний", "Продавец — перекуп"),
        "документы": ("Средний", "Возможны проблемы с документами"),
        "без пробега по рф": ("Низкий", "Свежий пригон — нужна проверка"),
        "конструктор": ("Высокий", "Собрана из частей"),
        "распил": ("Критический", "Распил — юридические риски"),
    }
    
    # Эталонные цены
    MARKET_PRICES = {
        ("volkswagen", "tiguan", 2019): 2400000,
        ("volkswagen", "tiguan", 2020): 2700000,
        ("toyota", "camry", 2020): 2900000,
        ("toyota", "camry", 2019): 2600000,
        ("kia", "sportage", 2018): 2000000,
        ("hyundai", "solaris", 2021): 1500000,
        ("bmw", "x5", 2017): 3300000,
        ("mazda", "cx-5", 2019): 2500000,
        ("nissan", "qashqai", 2020): 2200000,
        ("skoda", "octavia", 2018): 1700000,
        ("ford", "focus", 2019): 1400000,
        ("renault", "duster", 2020): 1300000,
    }
    
    NORMAL_MILEAGE_PER_YEAR = 15000
    
    async def analyze_listing(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """Полный анализ объявления"""
        
        price_analysis = self._analyze_price(listing)
        mileage_analysis = self._analyze_mileage(listing)
        risks_analysis = self._analyze_text_risks(listing)
        verdict_data = self._make_verdict(price_analysis, mileage_analysis, risks_analysis)
        
        # Краткий summary — только уникальная информация
        summary = self._generate_summary(price_analysis, mileage_analysis, risks_analysis)
        
        return {
            "summary": summary,
            "price_assessment": price_analysis["assessment"],
            "mileage_assessment": mileage_analysis["assessment"],
            "market_price": price_analysis["market_price"],
            "price_difference_percent": price_analysis["difference_percent"],
            "mileage_ratio": mileage_analysis["ratio"],
            "risks": risks_analysis["risks"],  # Массив, не строка!
            "risk_level": risks_analysis["risk_level"],
            "verdict": verdict_data["verdict"],
            "confidence": verdict_data["confidence"],
            "recommendations": verdict_data["recommendations"]
        }
    
    def _analyze_price(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ цены — чистый формат"""
        
        brand = listing.get("brand", "").lower()
        model = listing.get("model", "").lower()
        year = listing.get("year", 0)
        price = int(listing.get("price_rub", 0) or 0)
        
        market_price = self.MARKET_PRICES.get((brand, model, year))
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
            assessment = "сильно ниже рынка"
            score = 0.3
        elif difference < -5:
            assessment = "ниже рынка"
            score = 0.7
        elif difference < 5:
            assessment = "рыночная цена"
            score = 0.9
        elif difference < 15:
            assessment = "выше рынка"
            score = 0.6
        else:
            assessment = "сильно выше рынка"
            score = 0.2
        
        return {
            "market_price": market_price,
            "listing_price": price,
            "difference_percent": round(difference, 1),
            "assessment": assessment,
            "score": score
        }
    
    def _estimate_market_price(self, brand: str, model: str, year: int) -> int:
        """Оценка рыночной цены"""
        base_prices = {
            "economy": 1000000,
            "middle": 2000000,
            "premium": 3500000,
        }
        
        premium_brands = ["bmw", "mercedes", "audi", "lexus", "porsche", "volvo"]
        economy_brands = ["hyundai", "kia", "renault", "lada", "chery"]
        
        if brand in premium_brands:
            base = base_prices["premium"]
        elif brand in economy_brands:
            base = base_prices["economy"]
        else:
            base = base_prices["middle"]
        
        current_year = 2026
        age = current_year - year
        factor = max(0.3, 1 - age * 0.1)
        
        return int(base * factor)
    
    def _analyze_mileage(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ пробега — чистый формат"""
        
        mileage = int(listing.get("mileage", 0) or 0)
        year = listing.get("year", 0)
        current_year = 2026
        age = current_year - year
        
        if age <= 0 or mileage <= 0:
            return {
                "mileage": mileage,
                "expected_mileage": 0,
                "ratio": 1.0,
                "assessment": "нет данных",
                "score": 0.5
            }
        
        expected_mileage = age * self.NORMAL_MILEAGE_PER_YEAR
        ratio = mileage / expected_mileage
        
        if ratio < 0.5:
            assessment = "подозрительно малый пробег"
            score = 0.4
        elif ratio < 0.8:
            assessment = "малый пробег"
            score = 0.8
        elif ratio < 1.3:
            assessment = "нормальный пробег"
            score = 0.9
        elif ratio < 2.0:
            assessment = "большой пробег"
            score = 0.6
        else:
            assessment = "очень большой пробег"
            score = 0.3
        
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
        
        risk_levels = {"Низкий": 1, "Средний": 2, "Высокий": 3, "Критический": 4}
        
        for marker, (level, explanation) in self.RISK_MARKERS.items():
            if marker in description:
                risks.append({
                    "marker": marker,
                    "level": level,
                    "explanation": explanation
                })
                if risk_levels.get(level, 0) > risk_levels.get(max_risk_level, 0):
                    max_risk_level = level
        
        if not risks:
            return {
                "risks": [],
                "risk_level": "Низкий"
            }
        
        return {
            "risks": risks,
            "risk_level": max_risk_level
        }
    
    def _make_verdict(self, price_analysis: Dict, mileage_analysis: Dict, risks_analysis: Dict) -> Dict[str, Any]:
        """Формируем вердикт"""
        
        scores = [
            price_analysis.get("score", 0.5),
            mileage_analysis.get("score", 0.5),
        ]
        
        risk_level = risks_analysis.get("risk_level", "Низкий")
        risk_penalties = {"Низкий": 0, "Средний": 0.2, "Высокий": 0.4, "Критический": 0.6}
        risk_penalty = risk_penalties.get(risk_level, 0)
        
        avg_score = sum(scores) / len(scores) - risk_penalty
        avg_score = max(0, min(1, avg_score))
        
        if avg_score >= 0.8:
            verdict = "ЗВОНИТЬ"
            confidence = 0.9
            recommendations = [
                "Отличный вариант",
                "Связаться с продавцом",
                "Проверить авто перед покупкой",
                "Заказать отчёт по VIN"
            ]
        elif avg_score >= 0.6:
            verdict = "ТОРГОВАТЬСЯ"
            confidence = 0.7
            recommendations = [
                "Хороший вариант с нюансами",
                "Возможен торг",
                "Требуется проверка",
                "Заказать отчёт по VIN"
            ]
        elif avg_score >= 0.4:
            verdict = "ДУМАТЬ"
            confidence = 0.5
            recommendations = [
                "Есть серьёзные риски",
                "Требуется экспертная проверка",
                "Обязателен сильный торг",
                "Проверить документы"
            ]
        else:
            verdict = "БЕЖАТЬ"
            confidence = 0.8
            recommendations = [
                "Высокий риск",
                "Не рекомендуется",
                "Возможны скрытые дефекты",
                "Искать другой вариант"
            ]
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "score": round(avg_score, 2),
            "recommendations": recommendations
        }
    
    def _generate_summary(self, price_analysis: Dict, mileage_analysis: Dict, risks_analysis: Dict) -> str:
        """Краткий summary — только уникальная информация"""
        
        parts = []
        
        # Цена
        price_assessment = price_analysis.get("assessment", "")
        diff = price_analysis.get("difference_percent", 0)
        if price_assessment and price_assessment != "нет данных":
            if diff != 0:
                parts.append(f"Цена {price_assessment} ({diff:+.1f}%)")
            else:
                parts.append(f"Цена {price_assessment}")
        
        # Пробег
        mileage_assessment = mileage_analysis.get("assessment", "")
        if mileage_assessment and mileage_assessment != "нет данных":
            parts.append(mileage_assessment)
        
        # Риски
        risks = risks_analysis.get("risks", [])
        risk_level = risks_analysis.get("risk_level", "Низкий")
        if not risks:
            parts.append("рисков не выявлено")
        else:
            risk_markers = [r["marker"] for r in risks]
            parts.append(f"риски: {', '.join(risk_markers)} ({risk_level})")
        
        return ". ".join(parts)
    
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
            "price": listing.price_rub,
            "fair_price": listing.fair_price,
            "ai_summary": listing.ai_summary,
            "ai_risks": listing.ai_risks,
            "ai_verdict": listing.ai_verdict
        }

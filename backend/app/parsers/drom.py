import hashlib
from typing import Any, Dict, List

from app.core.logger import setup_logger

from .base import BaseParser

logger = setup_logger(__name__)


class DromParser(BaseParser):
    """Мок-парсер Дрома для MVP"""

    MOCK_DATA = [
        {
            "brand": "Volkswagen",
            "model": "Tiguan",
            "year": 2019,
            "mileage": 85000,
            "engine_volume": 2.0,
            "fuel_type": "бензин",
            "transmission": "автомат",
            "region": "Москва",
            "price_rub": 2350000,
            "description": "Продаю свой Tiguan 2019 года. Один владелец, не бит, не крашен. Полное ТО у дилера. Зимняя резина в подарок. Состояние отличное, следил за машиной.",
            "seller_info": {"name": "Александр", "type": "Частное лицо"},
        },
        {
            "brand": "Toyota",
            "model": "Camry",
            "year": 2020,
            "mileage": 62000,
            "engine_volume": 2.5,
            "fuel_type": "бензин",
            "transmission": "автомат",
            "region": "Москва",
            "price_rub": 2800000,
            "description": "Camry в идеальном состоянии. Обслуживалась только у дилера. Косметических недостатков нет. Торг у капота. Полный пакет ключей.",
            "seller_info": {"name": "Дмитрий", "type": "Частное лицо"},
        },
        {
            "brand": "Kia",
            "model": "Sportage",
            "year": 2018,
            "mileage": 120000,
            "engine_volume": 2.0,
            "fuel_type": "бензин",
            "transmission": "автомат",
            "region": "Санкт-Петербург",
            "price_rub": 1950000,
            "description": "Sportage 2018 года. Требует небольших вложений по подвеске. Двигатель и коробка работают отлично. Косметика на 4+.",
            "seller_info": {"name": "Иван", "type": "Частное лицо"},
        },
        {
            "brand": "Hyundai",
            "model": "Solaris",
            "year": 2021,
            "mileage": 45000,
            "engine_volume": 1.6,
            "fuel_type": "бензин",
            "transmission": "автомат",
            "region": "Москва",
            "price_rub": 1450000,
            "description": "Solaris на максималке. Один владелец. Не бит, не крашен. Все ТО у дилера. Зимняя резина на дисках в подарок.",
            "seller_info": {"name": "Сергей", "type": "Частное лицо"},
        },
        {
            "brand": "BMW",
            "model": "X5",
            "year": 2017,
            "mileage": 150000,
            "engine_volume": 3.0,
            "fuel_type": "дизель",
            "transmission": "автомат",
            "region": "Москва",
            "price_rub": 3200000,
            "description": "X5 в отличном состоянии. Полный привод. Панорамная крыша. Кожаный салон. Обслуживалась в специализированном сервисе. Есть все чеки.",
            "seller_info": {"name": "Алексей", "type": "Частное лицо"},
        },
        {
            "brand": "Mazda",
            "model": "CX-5",
            "year": 2019,
            "mileage": 78000,
            "engine_volume": 2.5,
            "fuel_type": "бензин",
            "transmission": "автомат",
            "region": "Москва",
            "price_rub": 2450000,
            "description": "CX-5 2019 года. Один владелец. Не бит, не крашен. Полный пакет ключей. Зимняя резина в подарок. Состояние новой машины.",
            "seller_info": {"name": "Ольга", "type": "Частное лицо"},
        },
        {
            "brand": "Nissan",
            "model": "Qashqai",
            "year": 2020,
            "mileage": 55000,
            "engine_volume": 2.0,
            "fuel_type": "бензин",
            "transmission": "вариатор",
            "region": "Санкт-Петербург",
            "price_rub": 2100000,
            "description": "Qashqai в отличном состоянии. Обслуживалась у дилера. Не бит, не крашен. Полный пакет ключей. Зимняя резина на дисках.",
            "seller_info": {"name": "Андрей", "type": "Частное лицо"},
        },
        {
            "brand": "Skoda",
            "model": "Octavia",
            "year": 2018,
            "mileage": 135000,
            "engine_volume": 1.8,
            "fuel_type": "бензин",
            "transmission": "робот",
            "region": "Москва",
            "price_rub": 1650000,
            "description": "Octavia A7. Требует замены масла в коробке. Двигатель работает отлично. Косметика на 4. Полный пакет ключей.",
            "seller_info": {"name": "Михаил", "type": "Частное лицо"},
        },
        {
            "brand": "Ford",
            "model": "Focus",
            "year": 2019,
            "mileage": 92000,
            "engine_volume": 2.0,
            "fuel_type": "бензин",
            "transmission": "автомат",
            "region": "Москва",
            "price_rub": 1350000,
            "description": "Focus 3 в отличном состоянии. Один владелец. Не бит, не крашен. Все ТО у дилера. Зимняя резина в подарок.",
            "seller_info": {"name": "Екатерина", "type": "Частное лицо"},
        },
        {
            "brand": "Renault",
            "model": "Duster",
            "year": 2020,
            "mileage": 68000,
            "engine_volume": 2.0,
            "fuel_type": "бензин",
            "transmission": "механика",
            "region": "Москва",
            "price_rub": 1250000,
            "description": "Duster 4x4. Один владелец. Не бит, не крашен. Полный пакет ключей. Зимняя резина на дисках. Состояние отличное.",
            "seller_info": {"name": "Владимир", "type": "Частное лицо"},
        },
    ]

    def _generate_external_id(self, item: Dict[str, Any]) -> str:
        """Детерминированный ID на основе данных объявления"""
        data = f"{item['brand']}_{item['model']}_{item['year']}_{item['price_rub']}_{item['mileage']}"
        hash_value = hashlib.md5(data.encode()).hexdigest()[:12]
        return f"drom_{hash_value}"

    def _generate_url(self, external_id: str) -> str:
        """Генерируем URL на основе ID"""
        num_id = int(external_id.split("_")[1][:7], 16) % 9000000 + 1000000
        return f"https://www.drom.ru/bulletin/{num_id}.html"

    async def parse_search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Возвращаем мок-данные с фильтрацией"""
        logger.info(f"Парсинг Дрома с параметрами: {params}")

        query = params.get("query", "").lower()
        region = params.get("region", "").lower()
        price_max = params.get("price_max")
        price_min = params.get("price_min")
        year_min = params.get("year_min")
        year_max = params.get("year_max")

        filtered = []

        for item in self.MOCK_DATA:
            if query:
                car_name = f"{item['brand']} {item['model']}".lower()
                if query not in car_name:
                    continue

            if region and region not in item["region"].lower():
                continue

            if price_max and item["price_rub"] > price_max:
                continue
            if price_min and item["price_rub"] < price_min:
                continue

            if year_min and item["year"] < year_min:
                continue
            if year_max and item["year"] > year_max:
                continue

            external_id = self._generate_external_id(item)

            listing = {
                "source": "drom",
                "external_id": external_id,
                "url": self._generate_url(external_id),
                **item,
                "body_type": (
                    "внедорожник"
                    if item["model"] in ["Tiguan", "Sportage", "X5", "CX-5", "Qashqai", "Duster"]
                    else "седан"
                ),
                "vin": "",
                "photos": [f"https://example.com/photo_{hash(external_id) % 100}.jpg"],
            }

            filtered.append(listing)

        logger.info(f"Найдено объявлений: {len(filtered)}")
        return filtered

    async def parse_listing(self, url: str) -> Dict[str, Any]:
        """Парсинг отдельного объявления"""
        return {}

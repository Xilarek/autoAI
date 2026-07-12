"""
Базовый класс для всех парсеров через Apify.

Архитектура:
- BaseApifyParser содержит ВСЮ общую логику (Apify API, retry, errors, HTTP client)
- Каждая площадка наследуется и переопределяет только:
  * PLATFORM: str — название площадки
  * ACTORS: List[str] — список Apify акторов
  * REGION_MAP: Dict[str, str] — маппинг регионов
  * _build_search_url(params) -> str — построить URL поиска
  * _transform_listing(raw_data) -> Dict — преобразовать в наш формат

Добавление новой площадки:
1. Создать файл в platforms/{name}.py
2. Наследоваться от BaseApifyParser
3. Добавить декоратор @register_parser("name")
4. Реализовать 2 метода: _build_search_url и _transform_listing
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import hashlib
import json
import asyncio
import re
from app.core.logger import setup_logger
from app.core.config import settings
from app.core.http_client import get_http_client
from app.core.exceptions import (
    ParserError, ParserTimeoutError, ParserUnavailableError,
    ParserEmptyResultError
)

logger = setup_logger(__name__)


class BaseApifyParser(ABC):
    """
    Базовый класс для парсеров через Apify.
    
    Наследники должны реализовать только специфичную для площадки логику.
    Вся общая работа с Apify API, retry, errors, HTTP client — здесь.
    """
    
    # 🔧 Абстрактные свойства (обязательны для наследников)
    PLATFORM: str = ""
    ACTORS: List[str] = []
    REGION_MAP: Dict[str, str] = {}
    
    # 🔧 Настройки по умолчанию (можно переопределить в наследниках)
    DEFAULT_ACTOR = "apify~website-content-crawler"
    MAX_WAIT_SECONDS = 180
    MAX_RESULTS = 50
    
    # ============================================
    # АБСТРАКТНЫЕ МЕТОДЫ (обязательны для наследников)
    # ============================================
    
    @abstractmethod
    def _build_search_url(self, params: Dict[str, Any]) -> str:
        """Построить URL поиска для площадки"""
        pass
    
    @abstractmethod
    def _transform_listing(self, raw_data: Dict) -> Optional[Dict[str, Any]]:
        """
        Преобразовать сырые данные в наш формат.
        
        raw_data может содержать:
        - source: "jsonld" | "markdown"
        - Для jsonld: name, price, url
        - Для markdown: text, url
        """
        pass
    
    # ============================================
    # ГЛАВНЫЙ МЕТОД (не переопределяется)
    # ============================================
    
    async def parse_search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Главный метод — парсинг через Apify"""
        
        if not settings.APIFY_TOKEN:
            raise ParserUnavailableError(
                "Apify API token not configured",
                "Please set APIFY_TOKEN in .env file"
            )
        
        search_url = self._build_search_url(params)
        logger.info(f"🔗 [{self.PLATFORM}] Парсинг: {search_url}")
        
        try:
            run_id = await self._start_actor_run(search_url)
            
            if not run_id:
                raise ParserUnavailableError(
                    f"Failed to start Apify actor for {self.PLATFORM}",
                    "All actors returned errors"
                )
            
            result = await self._wait_for_result(run_id)
            
            if not result:
                raise ParserEmptyResultError(
                    f"Apify returned no results for {self.PLATFORM}",
                    f"Run ID: {run_id}"
                )
            
            logger.info(f"📦 [{self.PLATFORM}] Получено {len(result)} элементов от Apify")
            
            # Сохраняем для отладки
            with open(f"/tmp/{self.PLATFORM}_apify_debug.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # Извлекаем объявления
            listings = self._extract_listings(result)
            
            if not listings:
                raise ParserEmptyResultError(
                    f"No listings extracted from {self.PLATFORM} page",
                    "Page may have changed structure"
                )
            
            logger.info(f"✅ [{self.PLATFORM}] Извлечено {len(listings)} объявлений")
            return listings
            
        except (ParserTimeoutError, ParserUnavailableError, 
                ParserEmptyResultError):
            raise
        except Exception as e:
            logger.error(f"❌ [{self.PLATFORM}] Неизвестная ошибка: {e}", exc_info=True)
            raise ParserError(f"Unexpected {self.PLATFORM} parser error", str(e))
    
    # ============================================
    # ОБЩАЯ ЛОГИКА: Apify API
    # ============================================
    
    async def _start_actor_run(self, url: str) -> str:
        """Запустить Apify актор (общая логика для всех площадок)"""
        
        client = get_http_client()
        
        for actor_id in self.ACTORS:
            logger.info(f"🚀 [{self.PLATFORM}] Пробуем актор: {actor_id}")
            
            run_input = self._build_actor_input(url)
            
            try:
                response = await client.post(
                    f"https://api.apify.com/v2/acts/{actor_id}/runs",
                    params={"token": settings.APIFY_TOKEN},
                    json=run_input
                )
                
                logger.info(f"📡 [{self.PLATFORM}] {actor_id}: статус {response.status_code}")
                
                if response.status_code == 201:
                    data = response.json()
                    run_id = data["data"]["id"]
                    logger.info(f"✅ [{self.PLATFORM}] Актор запущен: {run_id}")
                    return run_id
                
                logger.warning(f"❌ [{self.PLATFORM}] {actor_id}: {response.status_code} - {response.text[:300]}")
                
            except Exception as e:
                logger.warning(f"❌ [{self.PLATFORM}] Ошибка запуска {actor_id}: {e}")
                continue
        
        logger.error(f"❌ [{self.PLATFORM}] Все акторы не сработали")
        return ""
    
    def _build_actor_input(self, url: str) -> Dict[str, Any]:
        """Построить input для Apify актора (можно переопределить)"""
        return {
            "startUrls": [{"url": url}],
            "crawlerType": "playwright:firefox",
            "maxCrawlDepth": 0,
            "maxCrawlPages": 1,
            "maxResults": self.MAX_RESULTS,
            "waitUntil": {"event": "networkidle", "timeout": 30000},
        }
    
    async def _wait_for_result(self, run_id: str) -> List[Dict]:
        """Ждать результат выполнения актора (общая логика)"""
        
        client = get_http_client()
        
        for i in range(self.MAX_WAIT_SECONDS // 3):
            try:
                response = await client.get(
                    f"https://api.apify.com/v2/actor-runs/{run_id}",
                    params={"token": settings.APIFY_TOKEN}
                )
                
                if response.status_code != 200:
                    logger.error(f"[{self.PLATFORM}] Ошибка получения статуса: {response.status_code}")
                    return []
                
                data = response.json()
                status = data["data"]["status"]
                
                if status == "SUCCEEDED":
                    dataset_id = data["data"]["defaultDatasetId"]
                    logger.info(f"✅ [{self.PLATFORM}] Актор завершён. Dataset: {dataset_id}")
                    return await self._get_dataset_items(dataset_id)
                
                if status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                    logger.error(f"❌ [{self.PLATFORM}] Актор завершился с ошибкой: {status}")
                    status_msg = data["data"].get("statusMessage", "")
                    if status_msg:
                        logger.error(f"❌ [{self.PLATFORM}] Сообщение: {status_msg}")
                    return []
                
                logger.info(f"⏳ [{self.PLATFORM}] Статус: {status}, ждём... ({i*3}с)")
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.warning(f"⏱️ [{self.PLATFORM}] Ошибка при проверке статуса: {e}")
                await asyncio.sleep(3)
                continue
        
        raise ParserTimeoutError(
            f"{self.PLATFORM} actor timeout",
            f"Actor {run_id} did not complete in {self.MAX_WAIT_SECONDS} seconds"
        )
    
    async def _get_dataset_items(self, dataset_id: str) -> List[Dict]:
        """Получить элементы из датасета (общая логика)"""
        
        client = get_http_client()
        
        response = await client.get(
            f"https://api.apify.com/v2/datasets/{dataset_id}/items",
            params={
                "token": settings.APIFY_TOKEN,
                "format": "json",
                "limit": self.MAX_RESULTS
            }
        )
        
        if response.status_code == 200:
            items = response.json()
            logger.info(f"📦 [{self.PLATFORM}] Получено {len(items)} элементов из датасета")
            return items
        
        logger.error(f"❌ [{self.PLATFORM}] Ошибка получения датасета: {response.status_code}")
        return []
    
    # ============================================
    # ОБЩАЯ ЛОГИКА: Извлечение данных
    # ============================================
    
    def _extract_listings(self, items: List[Dict]) -> List[Dict[str, Any]]:
        """Извлечь объявления из сырых данных Apify (общая логика)"""
        
        all_listings = []
        
        for item in items:
            try:
                crawl = item.get("crawl", {})
                http_status = crawl.get("httpStatusCode", 0)
                
                if http_status == 404:
                    logger.warning(f"❌ [{self.PLATFORM}] Страница вернула 404: {item.get('url')}")
                    continue
                
                if http_status == 403:
                    logger.warning(f"🚫 [{self.PLATFORM}] Страница заблокирована: {item.get('url')}")
                    continue
                
                if http_status != 200:
                    logger.warning(f"⚠️ [{self.PLATFORM}] Страница вернула статус {http_status}")
                    continue
                
                # Метод 1: JSON-LD (самый надёжный)
                jsonld_listings = self._extract_from_jsonld(item)
                if jsonld_listings:
                    logger.info(f"🎯 [{self.PLATFORM}] Извлечено {len(jsonld_listings)} объявлений из JSON-LD")
                    all_listings.extend(jsonld_listings)
                    continue
                
                # Метод 2: Markdown (fallback)
                markdown_listings = self._extract_from_markdown(item)
                if markdown_listings:
                    logger.info(f"📝 [{self.PLATFORM}] Извлечено {len(markdown_listings)} объявлений из markdown")
                    all_listings.extend(markdown_listings)
                    
            except Exception as e:
                logger.error(f"Ошибка трансформации: {e}", exc_info=True)
                continue
        
        return all_listings
    
    def _extract_from_jsonld(self, item: Dict) -> List[Dict[str, Any]]:
        """Извлечь объявления из JSON-LD метаданных (общая логика)"""
        
        metadata = item.get("metadata", {})
        jsonld = metadata.get("jsonLd", [])
        
        if not jsonld:
            return []
        
        if isinstance(jsonld, dict):
            jsonld = [jsonld]
        
        listings = []
        
        for schema in jsonld:
            if not isinstance(schema, dict):
                continue
            
            if schema.get("@type") == "Product":
                offers_data = schema.get("offers", {})
                
                if isinstance(offers_data, dict):
                    offers = offers_data.get("offers", [])
                    
                    if isinstance(offers, dict):
                        offers = [offers]
                    
                    for offer in offers:
                        listing = self._parse_jsonld_offer(offer)
                        if listing:
                            listings.append(listing)
        
        return listings
    
    def _parse_jsonld_offer(self, offer: Dict) -> Optional[Dict[str, Any]]:
        """Парсить JSON-LD предложение и вызвать _transform_listing"""
        
        name = offer.get("name", "")
        price = offer.get("price", 0)
        url = offer.get("url", "")
        
        if not name or not price:
            return None
        
        raw_data = {
            "name": name,
            "price": price,
            "url": url,
            "source": "jsonld",
        }
        
        return self._transform_listing(raw_data)
    
    def _extract_from_markdown(self, item: Dict) -> List[Dict[str, Any]]:
        """Извлечь объявления из markdown (общая логика, fallback)"""
        
        content = item.get("markdown") or item.get("text") or ""
        url = item.get("url", "")
        
        if not content or len(content) < 100:
            return []
        
        listings = []
        price_pattern = r'(\d{1,3}(?:[\s\xa0]\d{3})+)\s*₽'
        
        for price_match in re.finditer(price_pattern, content):
            try:
                start = max(0, price_match.start() - 500)
                end = min(len(content), price_match.end() + 500)
                context = content[start:end]
                
                raw_data = {
                    "text": context,
                    "url": url,
                    "source": "markdown",
                }
                
                listing = self._transform_listing(raw_data)
                if listing:
                    if not any(l['external_id'] == listing['external_id'] for l in listings):
                        listings.append(listing)
            except Exception as e:
                logger.error(f"Ошибка парсинга блока: {e}")
                continue
        
        return listings
    
    # ============================================
    # УТИЛИТЫ (общие для всех площадок)
    # ============================================
    
    def _generate_external_id(self, url: str, **kwargs) -> str:
        """Генерация детерминированного ID (общая логика)"""
        if url:
            hash_value = hashlib.md5(url.encode()).hexdigest()[:12]
            return f"{self.PLATFORM}_{hash_value}"
        
        data = "_".join(str(v) for v in kwargs.values())
        hash_value = hashlib.md5(data.encode()).hexdigest()[:12]
        return f"{self.PLATFORM}_{hash_value}"
    
    def _parse_title(self, title: str) -> tuple:
        """Парсить название 'Brand Model, Year' (общая логика)"""
        match = re.match(r'^([A-Za-zА-Яа-я]+)\s+([A-Za-zА-Яа-я0-9]+)(?:,\s*(\d{4}))?', title)
        
        if match:
            brand = match.group(1)
            model = match.group(2)
            year = int(match.group(3)) if match.group(3) else 0
            
            if year and (year < 1980 or year > 2027):
                year = 0
            
            return brand, model, year
        
        return "", "", 0
    
    def _extract_region_from_url(self, url: str, pattern: str) -> str:
        """Извлечь регион из URL (общая логика)"""
        match = re.search(pattern, url)
        if match:
            region_slug = match.group(1)
            for ru_name, slug in self.REGION_MAP.items():
                if slug == region_slug:
                    return ru_name.capitalize()
            return region_slug.replace('_', ' ').replace('-', ' ').capitalize()
        return ""
    
    def _extract_price_from_text(self, text: str) -> int:
        """Извлечь цену из текста (общая логика)"""
        match = re.search(r'(\d{1,3}(?:[\s\xa0]\d{3})+)\s*₽', text)
        if match:
            return int(match.group(1).replace('\xa0', '').replace(' ', ''))
        return 0
    
    def _extract_mileage_from_text(self, text: str) -> int:
        """Извлечь пробег из текста (общая логика)"""
        match = re.search(r'(\d{1,3}(?:[\s\xa0]\d{3})*)\s*км', text)
        if match:
            return int(match.group(1).replace('\xa0', '').replace(' ', ''))
        return 0
    
    def _extract_fuel_from_text(self, text: str) -> str:
        """Извлечь тип топлива из текста (общая логика)"""
        text_lower = text.lower()
        if "бензин" in text_lower:
            return "бензин"
        elif "дизель" in text_lower:
            return "дизель"
        elif "гибрид" in text_lower:
            return "гибрид"
        elif "электро" in text_lower:
            return "электро"
        return ""
    
    def _extract_transmission_from_text(self, text: str) -> str:
        """Извлечь тип КПП из текста (общая логика)"""
        text_lower = text.lower()
        if "автомат" in text_lower or "акпп" in text_lower:
            return "автомат"
        elif "механик" in text_lower or "мкпп" in text_lower:
            return "механика"
        elif "вариатор" in text_lower:
            return "вариатор"
        elif "робот" in text_lower:
            return "робот"
        return ""
    
    def _extract_engine_from_text(self, text: str) -> float:
        """Извлечь объём двигателя из текста (общая логика)"""
        match = re.search(r'(\d+\.?\d*)\s*л', text)
        if match:
            return float(match.group(1))
        return 0.0

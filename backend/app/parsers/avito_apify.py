"""Парсер Авито через Apify"""

from typing import List, Dict, Any
import hashlib
import json
import asyncio
import re
from app.core.logger import setup_logger
from app.core.config import settings
from app.core.http_client import get_http_client
from app.core.exceptions import (
    ParserError, ParserTimeoutError, ParserUnavailableError,
    ParserBlockedError, ParserEmptyResultError, ApifyAPIError
)

logger = setup_logger(__name__)


class AvitoApifyParser:
    """Парсер Авито через Apify API"""
    
    ACTORS = [
        "apify~website-content-crawler",
        "apify~web-scraper",
    ]
    
    REGION_MAP = {
        "moscow": "moskva", "москва": "moskva",
        "spb": "sankt-peterburg", "санкт-петербург": "sankt-peterburg",
        "новосибирск": "novosibirsk", "екатеринбург": "ekaterinburg",
        "казань": "kazan", "нижний новгород": "nizhniy_novgorod",
        "самара": "samara", "ростов": "rostov-na-donu",
        "краснодар": "krasnodar", "воронеж": "voronezh",
        "уфа": "ufa", "челябинск": "chelyabinsk",
        "омск": "omsk", "пермь": "perm",
        "волгоград": "volgograd", "тюмень": "tyumen",
        "красноярск": "krasnoyarsk", "саратов": "saratov",
        "владивосток": "vladivostok", "ярославль": "yaroslavl",
        "хабаровск": "khabarovsk", "тольятти": "tolyatti",
        "ижевск": "izhevsk", "барнаул": "barnaul",
        "ульяновск": "ulyanovsk", "томск": "tomsk",
        "рязань": "ryazan", "кемерово": "kemerovo",
        "пенза": "penza", "астрахань": "astrakhan",
        "липецк": "lipetsk", "тула": "tula",
        "киров": "kirov", "чебоксары": "cheboksary",
        "калининград": "kaliningrad", "брянск": "bryansk",
        "курск": "kursk", "ставрополь": "stavropol",
        "тверь": "tver", "иваново": "ivanovo",
        "белгород": "belgorod", "архангельск": "arkhangelsk",
        "сочи": "sochi", "оренбург": "orenburg",
    }
    
    async def parse_search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Парсинг через Apify"""
        
        if not settings.APIFY_TOKEN:
            raise ParserUnavailableError(
                "Apify API token not configured",
                "Please set APIFY_TOKEN in .env file"
            )
        
        search_url = self._build_search_url(params)
        logger.info(f"🔗 Apify парсинг Авито: {search_url}")
        
        try:
            run_id = await self._start_actor_run(search_url)
            
            if not run_id:
                raise ParserUnavailableError(
                    "Failed to start Apify actor",
                    "All actors returned errors"
                )
            
            result = await self._wait_for_result(run_id)
            
            if not result:
                raise ParserEmptyResultError(
                    "Apify returned no results",
                    f"Run ID: {run_id}"
                )
            
            logger.info(f"📦 Получено {len(result)} элементов от Apify")
            
            with open("/tmp/avito_apify_debug.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            listings = self._transform_results(result)
            
            if not listings:
                raise ParserEmptyResultError(
                    "No listings extracted from page",
                    "Page may have changed structure"
                )
            
            logger.info(f"✅ После трансформации: {len(listings)} объявлений")
            return listings
            
        except (ParserTimeoutError, ParserUnavailableError, 
                ParserBlockedError, ParserEmptyResultError, ApifyAPIError):
            raise
        except Exception as e:
            logger.error(f"❌ Неизвестная ошибка парсера: {e}", exc_info=True)
            raise ParserError("Unexpected parser error", str(e))
    
    async def _start_actor_run(self, url: str) -> str:
        """Запускаем актор на выполнение"""
        
        client = get_http_client()
        
        for actor_id in self.ACTORS:
            logger.info(f"🚀 Пробуем актор: {actor_id}")
            
            run_input = {
                "startUrls": [{"url": url}],
                "crawlerType": "playwright:firefox",
                "maxCrawlDepth": 0,
                "maxCrawlPages": 1,
                "maxResults": 50,
                "waitUntil": {"event": "networkidle", "timeout": 30000},
            }
            
            try:
                response = await client.post(
                    f"https://api.apify.com/v2/acts/{actor_id}/runs",
                    params={"token": settings.APIFY_TOKEN},
                    json=run_input
                )
                
                logger.info(f"📡 {actor_id}: статус {response.status_code}")
                
                if response.status_code == 201:
                    data = response.json()
                    run_id = data["data"]["id"]
                    logger.info(f"✅ Актор {actor_id} запущен: {run_id}")
                    return run_id
                
                logger.warning(f"❌ {actor_id}: {response.status_code}")
                
            except Exception as e:
                logger.warning(f"❌ Ошибка при запуске {actor_id}: {e}")
                continue
        
        return ""
    
    async def _wait_for_result(self, run_id: str, max_wait: int = 180) -> List[Dict]:
        """Ждём завершения выполнения актора"""
        
        client = get_http_client()
        
        for i in range(max_wait // 3):
            try:
                response = await client.get(
                    f"https://api.apify.com/v2/actor-runs/{run_id}",
                    params={"token": settings.APIFY_TOKEN}
                )
                
                if response.status_code != 200:
                    return []
                
                data = response.json()
                status = data["data"]["status"]
                
                if status == "SUCCEEDED":
                    dataset_id = data["data"]["defaultDatasetId"]
                    logger.info(f"✅ Актор завершён. Dataset: {dataset_id}")
                    return await self._get_dataset_items(dataset_id)
                
                if status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                    logger.error(f"❌ Актор завершился с ошибкой: {status}")
                    return []
                
                logger.info(f"⏳ Статус: {status}, ждём... ({i*3}с)")
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.warning(f"⏱️ Ошибка при проверке статуса: {e}")
                await asyncio.sleep(3)
                continue
        
        raise ParserTimeoutError(
            "Actor execution timeout",
            f"Actor {run_id} did not complete in {max_wait} seconds"
        )
    
    async def _get_dataset_items(self, dataset_id: str) -> List[Dict]:
        """Получаем элементы из датасета"""
        
        client = get_http_client()
        
        response = await client.get(
            f"https://api.apify.com/v2/datasets/{dataset_id}/items",
            params={
                "token": settings.APIFY_TOKEN,
                "format": "json",
                "limit": 50
            }
        )
        
        if response.status_code == 200:
            items = response.json()
            logger.info(f"📦 Получено {len(items)} элементов из датасета")
            return items
        
        return []
    
    def _transform_results(self, items: List[Dict]) -> List[Dict[str, Any]]:
        """Преобразуем результаты Apify в наш формат"""
        
        all_listings = []
        
        for item in items:
            try:
                crawl = item.get("crawl", {})
                http_status = crawl.get("httpStatusCode", 0)
                
                if http_status not in [200, 0]:
                    logger.warning(f"⚠️ Страница вернула статус {http_status}")
                    continue
                
                jsonld_listings = self._extract_from_jsonld(item)
                if jsonld_listings:
                    logger.info(f"🎯 Извлечено {len(jsonld_listings)} объявлений из JSON-LD")
                    all_listings.extend(jsonld_listings)
                    continue
                
                markdown_listings = self._extract_from_markdown(item)
                if markdown_listings:
                    logger.info(f"📝 Извлечено {len(markdown_listings)} объявлений из markdown")
                    all_listings.extend(markdown_listings)
                    
            except Exception as e:
                logger.error(f"Ошибка трансформации: {e}", exc_info=True)
                continue
        
        return all_listings
    
    def _extract_from_jsonld(self, item: Dict) -> List[Dict[str, Any]]:
        """Извлекаем объявления из JSON-LD"""
        
        metadata = item.get("metadata", {})
        jsonld = metadata.get("jsonLd", [])
        
        if not jsonld:
            return []
        
        listings = []
        
        if isinstance(jsonld, dict):
            jsonld = [jsonld]
        
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
    
    def _parse_jsonld_offer(self, offer: Dict) -> Dict[str, Any]:
        """Парсим одно предложение из JSON-LD"""
        
        name = offer.get("name", "")
        price = offer.get("price", 0)
        url = offer.get("url", "")
        
        if not name or not price:
            return None
        
        brand, model, year = self._parse_jsonld_name(name)
        
        if not brand:
            return None
        
        region = self._extract_region_from_url(url)
        
        external_id = self._generate_external_id(brand, model, year, price, 0, url)
        
        return {
            "source": "avito",
            "external_id": external_id,
            "url": url,
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": 0,
            "engine_volume": 0.0,
            "fuel_type": "",
            "transmission": "",
            "body_type": "",
            "vin": "",
            "region": region,
            "price_rub": int(price),
            "description": name,
            "photos": [],
            "seller_info": {"name": "", "type": ""}
        }
    
    def _parse_jsonld_name(self, name: str) -> tuple:
        """Парсим название из JSON-LD"""
        
        match = re.match(r'^([A-Za-zА-Яа-я]+)\s+([A-Za-zА-Яа-я0-9]+)(?:,\s*(\d{4}))?', name)
        
        if match:
            brand = match.group(1)
            model = match.group(2)
            year = int(match.group(3)) if match.group(3) else 0
            
            if year and (year < 1980 or year > 2027):
                year = 0
            
            return brand, model, year
        
        return "", "", 0
    
    def _extract_region_from_url(self, url: str) -> str:
        """Извлекаем регион из URL"""
        
        match = re.search(r'avito\.ru/([a-z_]+)/', url)
        if match:
            region_slug = match.group(1)
            for ru_name, slug in self.REGION_MAP.items():
                if slug == region_slug:
                    return ru_name.capitalize()
            return region_slug.replace('_', ' ').capitalize()
        
        return ""
    
    def _extract_from_markdown(self, item: Dict) -> List[Dict[str, Any]]:
        """Fallback: парсим markdown"""
        
        url = item.get("url", "")
        markdown = item.get("markdown", "")
        text = item.get("text", "")
        
        content = markdown or text
        
        if not content or len(content) < 100:
            return []
        
        return self._extract_listings_from_markdown(content, url)
    
    def _extract_listings_from_markdown(self, content: str, base_url: str) -> List[Dict[str, Any]]:
        """Извлекаем объявления из markdown"""
        
        listings = []
        
        price_pattern = r'(\d{1,3}(?:[\s\xa0]\d{3})+)\s*₽'
        prices = list(re.finditer(price_pattern, content))
        
        for price_match in prices:
            try:
                start = max(0, price_match.start() - 500)
                end = min(len(content), price_match.end() + 500)
                context = content[start:end]
                
                listing = self._parse_listing_block(context, base_url)
                if listing:
                    if not any(l['external_id'] == listing['external_id'] for l in listings):
                        listings.append(listing)
            except Exception as e:
                logger.error(f"Ошибка парсинга блока: {e}")
                continue
        
        return listings
    
    def _parse_listing_block(self, block: str, base_url: str) -> Dict[str, Any]:
        """Парсим блок текста как объявление"""
        
        title_match = re.search(
            r'(Audi|BMW|Chevrolet|Citroen|Ford|Honda|Hyundai|Kia|Lada|Lexus|'
            r'Mazda|Mercedes|Mini|Mitsubishi|Nissan|Opel|Peugeot|Porsche|'
            r'Renault|Skoda|Subaru|Suzuki|Toyota|Volkswagen|Volvo|УАЗ)\s+'
            r'(\w+)\s*,?\s*(\d{4})',
            block,
            re.IGNORECASE
        )
        
        if not title_match:
            title_match = re.search(r'(\w+)\s+(\w+)\s+(\d{4})', block)
            if not title_match:
                return None
            
            brand = title_match.group(1)
            model = title_match.group(2)
            year = int(title_match.group(3))
            
            if year < 1980 or year > 2027:
                return None
        else:
            brand = title_match.group(1)
            model = title_match.group(2)
            year = int(title_match.group(3))
        
        price = 0
        price_match = re.search(r'(\d{1,3}(?:[\s\xa0]\d{3})+)\s*₽', block)
        if price_match:
            price_str = price_match.group(1).replace('\xa0', ' ').replace(' ', '')
            price = int(price_str)
        
        if price < 50000:
            return None
        
        mileage = 0
        mileage_match = re.search(r'(\d{1,3}(?:[\s\xa0]\d{3})*)\s*км', block)
        if mileage_match:
            mileage_str = mileage_match.group(1).replace('\xa0', ' ').replace(' ', '')
            mileage = int(mileage_str)
        
        engine_volume = 0.0
        engine_match = re.search(r'(\d+\.?\d*)\s*л', block)
        if engine_match:
            engine_volume = float(engine_match.group(1))
        
        fuel_type = ""
        block_lower = block.lower()
        if "бензин" in block_lower:
            fuel_type = "бензин"
        elif "дизель" in block_lower:
            fuel_type = "дизель"
        elif "гибрид" in block_lower:
            fuel_type = "гибрид"
        elif "электро" in block_lower:
            fuel_type = "электро"
        
        transmission = ""
        if "автомат" in block_lower or "акпп" in block_lower:
            transmission = "автомат"
        elif "механик" in block_lower or "мкпп" in block_lower:
            transmission = "механика"
        elif "вариатор" in block_lower:
            transmission = "вариатор"
        elif "робот" in block_lower:
            transmission = "робот"
        
        url = ""
        url_match = re.search(r'https://www\.avito\.ru/\S+/\d+', block)
        if url_match:
            url = url_match.group(0)
        
        region = ""
        region_match = re.search(r'(Москва|Санкт-Петербург|Московская|Ленинградская)', block)
        if region_match:
            region = region_match.group(1)
        
        external_id = self._generate_external_id(brand, model, year, price, mileage, url)
        
        return {
            "source": "avito",
            "external_id": external_id,
            "url": url,
            "brand": brand.capitalize(),
            "model": model.capitalize(),
            "year": year,
            "mileage": mileage,
            "engine_volume": engine_volume,
            "fuel_type": fuel_type,
            "transmission": transmission,
            "body_type": "",
            "vin": "",
            "region": region,
            "price_rub": price,
            "description": block[:500],
            "photos": [],
            "seller_info": {"name": "", "type": ""}
        }
    
    def _build_search_url(self, params: Dict[str, Any]) -> str:
        """Формируем URL поиска для Авито"""
        
        query = params.get("query", "").lower().strip()
        region = params.get("region", "moscow").lower().strip()
        
        region_slug = self.REGION_MAP.get(region, region.replace(' ', '_'))
        
        base_url = f"https://www.avito.ru/{region_slug}/avtomobili"
        
        query_params = []
        
        if query:
            parts = query.split()
            if len(parts) >= 2:
                brand, model = parts[0], parts[1]
                query_params.append(f"q={brand}+{model}")
            elif len(parts) == 1:
                query_params.append(f"q={parts[0]}")
        
        if params.get("year_min"):
            query_params.append(f"year_min={params['year_min']}")
        if params.get("year_max"):
            query_params.append(f"year_max={params['year_max']}")
        if params.get("price_min"):
            query_params.append(f"price_min={params['price_min']}")
        if params.get("price_max"):
            query_params.append(f"price_max={params['price_max']}")
        
        if query_params:
            base_url += "?" + "&".join(query_params)
        
        return base_url
    
    def _generate_external_id(self, brand: str, model: str, year: int, 
                               price: int, mileage: int, url: str) -> str:
        """Детерминированный ID"""
        if url:
            hash_value = hashlib.md5(url.encode()).hexdigest()[:12]
            return f"avito_{hash_value}"
        
        data = f"{brand}_{model}_{year}_{price}_{mileage}"
        hash_value = hashlib.md5(data.encode()).hexdigest()[:12]
        return f"avito_{hash_value}"
    
    async def parse_listing(self, url: str) -> Dict[str, Any]:
        """Парсинг отдельного объявления"""
        return {}

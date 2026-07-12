"""Парсер Дрома через Apify"""

from typing import List, Dict, Any
import httpx
import hashlib
import json
import asyncio
import re
from app.core.logger import setup_logger
from app.core.config import settings

logger = setup_logger(__name__)


class DromApifyParser:
    """Парсер Дрома через Apify API"""
    
    ACTORS = [
        "apify~website-content-crawler",
        "apify~web-scraper",
        "apify~cheerio-scraper",
    ]
    
    REGION_MAP = {
        "moscow": "moscow",
        "москва": "moscow",
        "spb": "saint-petersburg",
        "санкт-петербург": "saint-petersburg",
        "новосибирск": "novosibirsk",
        "екатеринбург": "ekaterinburg",
        "казань": "kazan",
        "нижний новгород": "nizhniy-novgorod",
        "самара": "samara",
        "ростов": "rostov-na-donu",
        "краснодар": "krasnodar",
        "воронеж": "voronezh",
        "уфа": "ufa",
        "челябинск": "chelyabinsk",
        "омск": "omsk",
        "пермь": "perm",
        "волгоград": "volgograd",
        "тюмень": "tyumen",
        "красноярск": "krasnoyarsk",
        "саратов": "saratov",
        "владивосток": "vladivostok",
        "ярославль": "yaroslavl",
        "хабаровск": "khabarovsk",
        "тольятти": "tolyatti",
        "ижевск": "izhevsk",
        "барнаул": "barnaul",
        "ульяновск": "ulyanovsk",
        "томск": "tomsk",
        "рязань": "ryazan",
        "кемерово": "kemerovo",
        "пенза": "penza",
        "астрахань": "astrakhan",
        "липецк": "lipetsk",
        "тула": "tula",
        "киров": "kirov",
        "чебоксары": "cheboksary",
        "калининград": "kaliningrad",
        "брянск": "bryansk",
        "курск": "kursk",
        "ставрополь": "stavropol",
        "тверь": "tver",
        "иваново": "ivanovo",
        "белгород": "belgorod",
        "архангельск": "arkhangelsk",
        "сочи": "sochi",
        "оренбург": "orenburg",
        "набережные челны": "naberezhnye-chelny",
        "магнитогорск": "magnitogorsk",
    }
    
    async def parse_search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Парсинг через Apify"""
        
        if not settings.APIFY_TOKEN:
            logger.error("❌ APIFY_TOKEN не установлен в .env")
            return []
        
        search_url = self._build_search_url(params)
        logger.info(f"🔗 Apify парсинг Дрома: {search_url}")
        
        try:
            run_id = await self._start_actor_run(search_url)
            
            if not run_id:
                logger.error("❌ Не удалось запустить актор")
                return []
            
            result = await self._wait_for_result(run_id)
            
            if not result:
                logger.error("❌ Актор не вернул результатов")
                return []
            
            logger.info(f"📦 Получено {len(result)} элементов от Apify")
            
            with open("/tmp/apify_debug.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info("💾 Результаты Apify сохранены в /tmp/apify_debug.json")
            
            listings = self._transform_results(result)
            
            logger.info(f"✅ После трансформации: {len(listings)} объявлений")
            return listings
            
        except Exception as e:
            logger.error(f"Ошибка Apify: {e}", exc_info=True)
            return []
    
    async def _start_actor_run(self, url: str) -> str:
        """Запускаем актор на выполнение"""
        
        async with httpx.AsyncClient(timeout=60.0) as client:
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
                
                logger.warning(f"❌ {actor_id}: {response.status_code} - {response.text[:300]}")
            
            logger.error("❌ Все акторы не сработали")
            return ""
    
    async def _wait_for_result(self, run_id: str, max_wait: int = 180) -> List[Dict]:
        """Ждём завершения выполнения актора"""
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(max_wait // 3):
                response = await client.get(
                    f"https://api.apify.com/v2/actor-runs/{run_id}",
                    params={"token": settings.APIFY_TOKEN}
                )
                
                if response.status_code != 200:
                    logger.error(f"Ошибка получения статуса: {response.status_code}")
                    return []
                
                data = response.json()
                status = data["data"]["status"]
                
                if status == "SUCCEEDED":
                    dataset_id = data["data"]["defaultDatasetId"]
                    logger.info(f"✅ Актор завершён. Dataset: {dataset_id}")
                    return await self._get_dataset_items(dataset_id)
                
                if status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                    logger.error(f"❌ Актор завершился с ошибкой: {status}")
                    status_msg = data["data"].get("statusMessage", "")
                    if status_msg:
                        logger.error(f"❌ Сообщение: {status_msg}")
                    return []
                
                logger.info(f"⏳ Статус: {status}, ждём... ({i*3}с)")
                await asyncio.sleep(3)
            
            logger.error("⏱️ Таймаут ожидания результата")
            return []
    
    async def _get_dataset_items(self, dataset_id: str) -> List[Dict]:
        """Получаем элементы из датасета"""
        
        async with httpx.AsyncClient(timeout=30.0) as client:
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
            
            logger.error(f"Ошибка получения датасета: {response.status_code}")
            return []
    
    def _transform_results(self, items: List[Dict]) -> List[Dict[str, Any]]:
        """Преобразуем результаты Apify в наш формат"""
        
        all_listings = []
        
        for item in items:
            try:
                crawl = item.get("crawl", {})
                http_status = crawl.get("httpStatusCode", 0)
                
                if http_status == 404:
                    logger.warning(f"❌ Страница вернула 404: {item.get('url')}")
                    continue
                
                if http_status != 200:
                    logger.warning(f"⚠️ Страница вернула статус {http_status}")
                    continue
                
                # Метод 1: Извлекаем из JSON-LD (самый надёжный)
                jsonld_listings = self._extract_from_jsonld(item)
                if jsonld_listings:
                    logger.info(f"🎯 Извлечено {len(jsonld_listings)} объявлений из JSON-LD")
                    all_listings.extend(jsonld_listings)
                    continue
                
                # Метод 2: Парсим markdown (fallback)
                markdown_listings = self._extract_from_markdown(item)
                if markdown_listings:
                    logger.info(f"📝 Извлечено {len(markdown_listings)} объявлений из markdown")
                    all_listings.extend(markdown_listings)
                    
            except Exception as e:
                logger.error(f"Ошибка трансформации: {e}", exc_info=True)
                continue
        
        return all_listings
    
    def _extract_from_jsonld(self, item: Dict) -> List[Dict[str, Any]]:
        """Извлекаем объявления из JSON-LD метаданных (самый надёжный способ)"""
        
        metadata = item.get("metadata", {})
        jsonld = metadata.get("jsonLd", [])
        
        if not jsonld:
            logger.debug("Нет JSON-LD в метаданных")
            return []
        
        listings = []
        
        # JSON-LD может быть списком или одним объектом
        if isinstance(jsonld, dict):
            jsonld = [jsonld]
        
        for schema in jsonld:
            if not isinstance(schema, dict):
                continue
            
            # Ищем Product с offers
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
        
        # Парсим название: "Toyota Camry, 2022"
        brand, model, year = self._parse_jsonld_name(name)
        
        if not brand:
            return None
        
        # Извлекаем регион из URL
        region = self._extract_region_from_url(url)
        
        external_id = self._generate_external_id(brand, model, year, price, 0, url)
        
        return {
            "source": "drom",
            "external_id": external_id,
            "url": url,
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": 0,  # Нет данных в JSON-LD
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
        """Парсим название из JSON-LD: 'Toyota Camry, 2022'"""
        
        # Паттерн: "Brand Model, Year"
        match = re.match(r'^([A-Za-zА-Яа-я]+)\s+([A-Za-zА-Яа-я0-9]+)(?:,\s*(\d{4}))?', name)
        
        if match:
            brand = match.group(1)
            model = match.group(2)
            year = int(match.group(3)) if match.group(3) else 0
            
            # Валидация года
            if year and (year < 1980 or year > 2027):
                year = 0
            
            return brand, model, year
        
        return "", "", 0
    
    def _extract_region_from_url(self, url: str) -> str:
        """Извлекаем регион из URL Дрома"""
        
        # URL формат: https://auto.drom.ru/moscow/toyota/camry/123456.html
        match = re.search(r'auto\.drom\.ru/([a-z-]+)/', url)
        if match:
            region_slug = match.group(1)
            # Обратный маппинг
            for ru_name, slug in self.REGION_MAP.items():
                if slug == region_slug:
                    return ru_name.capitalize()
            return region_slug.capitalize()
        
        return ""
    
    def _extract_from_markdown(self, item: Dict) -> List[Dict[str, Any]]:
        """Fallback: парсим markdown"""
        
        url = item.get("url", "")
        markdown = item.get("markdown", "")
        text = item.get("text", "")
        
        content = markdown or text
        
        if not content or len(content) < 100:
            return []
        
        logger.info(f"📄 Контент страницы: {len(content)} символов")
        
        return self._extract_listings_from_markdown(content, url)
    
    def _extract_listings_from_markdown(self, content: str, base_url: str) -> List[Dict[str, Any]]:
        """Извлекаем объявления из markdown"""
        
        listings = []
        
        # Ищем все цены (с учётом неразрывных пробелов \xa0)
        price_pattern = r'(\d{1,3}(?:[\s\xa0]\d{3})+)\s*₽'
        prices = list(re.finditer(price_pattern, content))
        
        logger.info(f"🔍 Найдено {len(prices)} цен в markdown")
        
        for price_match in prices:
            try:
                # Берём контекст вокруг цены
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
        
        # Ищем название (марка модель год)
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
        
        # Ищем цену (с учётом неразрывных пробелов)
        price = 0
        price_match = re.search(r'(\d{1,3}(?:[\s\xa0]\d{3})+)\s*₽', block)
        if price_match:
            # Заменяем неразрывные пробелы на обычные
            price_str = price_match.group(1).replace('\xa0', ' ').replace(' ', '')
            price = int(price_str)
        
        if price < 50000:
            return None
        
        # Ищем пробег (с учётом неразрывных пробелов)
        mileage = 0
        mileage_match = re.search(r'(\d{1,3}(?:[\s\xa0]\d{3})*)\s*км', block)
        if mileage_match:
            mileage_str = mileage_match.group(1).replace('\xa0', ' ').replace(' ', '')
            mileage = int(mileage_str)
        
        # Ищем двигатель
        engine_volume = 0.0
        engine_match = re.search(r'(\d+\.?\d*)\s*л', block)
        if engine_match:
            engine_volume = float(engine_match.group(1))
        
        # Определяем топливо
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
        
        # Определяем коробку
        transmission = ""
        if "автомат" in block_lower or "акпп" in block_lower:
            transmission = "автомат"
        elif "механик" in block_lower or "мкпп" in block_lower:
            transmission = "механика"
        elif "вариатор" in block_lower:
            transmission = "вариатор"
        elif "робот" in block_lower:
            transmission = "робот"
        
        # Ищем ссылку на объявление
        url = ""
        url_match = re.search(r'https://auto\.drom\.ru/\S+/\d+\.html', block)
        if url_match:
            url = url_match.group(0)
        
        # Ищем регион
        region = ""
        region_match = re.search(r'(Москва|Санкт-Петербург|Московская|Ленинградская)', block)
        if region_match:
            region = region_match.group(1)
        
        external_id = self._generate_external_id(brand, model, year, price, mileage, url)
        
        return {
            "source": "drom",
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
        """Формируем URL поиска в правильном формате auto.drom.ru"""
        
        query = params.get("query", "").lower().strip()
        region = params.get("region", "moscow").lower().strip()
        
        region_slug = self.REGION_MAP.get(region, region.replace(' ', '-'))
        
        if not query:
            base_url = f"https://auto.drom.ru/{region_slug}/"
        else:
            parts = query.split()
            
            if len(parts) >= 2:
                brand, model = parts[0], parts[1]
                base_url = f"https://auto.drom.ru/{region_slug}/{brand}/{model}/"
            elif len(parts) == 1:
                brand = parts[0]
                base_url = f"https://auto.drom.ru/{region_slug}/{brand}/"
            else:
                base_url = f"https://auto.drom.ru/{region_slug}/"
        
        # ПРАВИЛЬНЫЕ параметры фильтрации Дрома
        query_params = []
        
        if params.get("year_min"):
            query_params.append(f"minyear={params['year_min']}")
        if params.get("year_max"):
            query_params.append(f"maxyear={params['year_max']}")
        if params.get("price_min"):
            query_params.append(f"minprice={params['price_min']}")
        if params.get("price_max"):
            query_params.append(f"maxprice={params['price_max']}")
        
        if query_params:
            base_url += "?" + "&".join(query_params)
        
        return base_url
    
    def _generate_external_id(self, brand: str, model: str, year: int, 
                               price: int, mileage: int, url: str) -> str:
        """Детерминированный ID"""
        if url:
            hash_value = hashlib.md5(url.encode()).hexdigest()[:12]
            return f"drom_{hash_value}"
        
        data = f"{brand}_{model}_{year}_{price}_{mileage}"
        hash_value = hashlib.md5(data.encode()).hexdigest()[:12]
        return f"drom_{hash_value}"
    
    async def parse_listing(self, url: str) -> Dict[str, Any]:
        """Парсинг отдельного объявления"""
        return {}

"""Реальный парсер Дрома через Playwright"""

from typing import List, Dict, Any
from playwright.async_api import async_playwright, Page, Browser
import hashlib
import random
import re
from app.core.logger import setup_logger
from app.core.config import settings

logger = setup_logger(__name__)


class DromRealParser:
    """Реальный парсер Дрома через Playwright с обходом блокировок"""
    
    BASE_URL = "https://www.drom.ru"
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    
    REGION_CODES = {
        "moscow": "77",
        "москва": "77",
        "spb": "78",
        "санкт-петербург": "78",
    }
    
    async def parse_search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Парсинг страницы поиска"""
        
        if settings.SCRAPERAPI_KEY:
            return await self._parse_with_scraperapi(params)
        
        return await self._parse_with_playwright(params)
    
    async def _parse_with_scraperapi(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Парсинг через ScraperAPI"""
        import httpx
        
        search_url = self._build_search_url(params)
        logger.info(f"Парсинг через ScraperAPI: {search_url}")
        
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.get(
                    "http://api.scraperapi.com",
                    params={
                        "api_key": settings.SCRAPERAPI_KEY,
                        "url": search_url,
                        "render": "true",
                        "premium": "true",
                        "country_code": "ru"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"ScraperAPI вернул статус {response.status_code}")
                    return []
                
                html = response.text
                
                with open("/tmp/drom_scraperapi_debug.html", "w", encoding="utf-8") as f:
                    f.write(html)
                logger.info("💾 HTML сохранён в /tmp/drom_scraperapi_debug.html")
                
                return self._parse_html(html)
                
        except Exception as e:
            logger.error(f"Ошибка ScraperAPI: {e}", exc_info=True)
            return []
    
    async def _parse_with_playwright(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Прямой парсинг через Playwright"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                ]
            )
            
            try:
                context = await browser.new_context(
                    user_agent=random.choice(self.USER_AGENTS),
                    viewport={"width": 1920, "height": 1080},
                    locale="ru-RU",
                    timezone_id="Europe/Moscow",
                )
                
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
                
                page = await context.new_page()
                
                # ШАГ 1: Сначала заходим на главную страницу
                logger.info("🏠 Заходим на главную страницу Дрома...")
                await page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(3000)
                
                main_title = await page.title()
                logger.info(f"📄 Главная страница: {main_title}")
                
                # ШАГ 2: Переходим к поиску
                search_url = self._build_search_url(params)
                logger.info(f"🔗 Переходим к поиску: {search_url}")
                
                await page.goto(search_url, wait_until="networkidle", timeout=60000)
                await page.wait_for_timeout(8000)  # Ждём дольше
                
                content = await page.content()
                
                with open("/tmp/drom_playwright_debug.html", "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info(f"💾 HTML сохранён ({len(content)} байт)")
                
                # Проверка блокировки
                if "captcha" in content.lower() or "Доступ ограничен" in content:
                    logger.warning("⚠️ Обнаружена блокировка или капча")
                    return []
                
                if "File not found" in content or len(content) < 500:
                    logger.error(f"❌ Страница не найдена (размер: {len(content)} байт)")
                    return []
                
                title = await page.title()
                logger.info(f"📄 Заголовок страницы поиска: {title}")
                
                return await self._parse_page(page)
                
            except Exception as e:
                logger.error(f"Критическая ошибка Playwright: {e}", exc_info=True)
                return []
            finally:
                await browser.close()
    
    async def _parse_page(self, page: Page) -> List[Dict[str, Any]]:
        """Парсинг страницы через Playwright"""
        
        # Ждём появления карточек
        try:
            await page.wait_for_selector('[data-ftid="bull-card"]', timeout=15000)
            logger.info("✅ Карточки загружены")
        except:
            logger.warning("⏱️ Таймаут ожидания карточек, пробуем другие селекторы")
        
        selectors = [
            '[data-ftid="bull-card"]',
            '[class*="ListingCard"]',
            '[class*="BulletinCard"]',
            '[class*="listing"]',
            'article',
        ]
        
        items = []
        for selector in selectors:
            items = await page.query_selector_all(selector)
            if items:
                logger.info(f"✅ Найдено элементов по '{selector}': {len(items)}")
                break
        
        if not items:
            logger.warning("❌ Не найдено ни одного объявления")
            return []
        
        listings = []
        for item in items[:20]:
            try:
                listing = await self._extract_item_data(item)
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.error(f"Ошибка извлечения: {e}")
                continue
        
        logger.info(f"✅ Успешно распарсено: {len(listings)} объявлений")
        return listings
    
    def _parse_html(self, html: str) -> List[Dict[str, Any]]:
        """Парсинг HTML через BeautifulSoup"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'lxml')
        
        selectors = [
            '[data-ftid="bull-card"]',
            '[class*="ListingCard"]',
            '[class*="BulletinCard"]',
            'article',
        ]
        
        items = []
        for selector in selectors:
            items = soup.select(selector)
            if items:
                logger.info(f"✅ Найдено элементов по '{selector}': {len(items)}")
                break
        
        if not items:
            logger.warning("❌ Не найдено ни одного объявления")
            return []
        
        listings = []
        for item in items[:20]:
            try:
                listing = self._extract_item_from_soup(item)
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.error(f"Ошибка извлечения: {e}")
                continue
        
        logger.info(f"✅ Успешно распарсено: {len(listings)} объявлений")
        return listings
    
    async def _extract_item_data(self, item) -> Dict[str, Any]:
        """Извлекаем данные из карточки (Playwright)"""
        
        title = ""
        for selector in ['h3', '[data-name="BulletinTitle"]', 'a']:
            title_elem = await item.query_selector(selector)
            if title_elem:
                title = await title_elem.inner_text()
                if title and len(title) > 5:
                    break
        
        if not title:
            return None
        
        brand, model, year = self._parse_title(title)
        
        price = 0
        for selector in ['[data-name="BulletinPrice"]', '[class*="Price"]', 'span']:
            price_elem = await item.query_selector(selector)
            if price_elem:
                price_text = await price_elem.inner_text()
                price = self._extract_price(price_text)
                if price > 0:
                    break
        
        url = ""
        link_elem = await item.query_selector('a[href*="/bulletin/"]')
        if link_elem:
            url = await link_elem.get_attribute("href")
            if url and not url.startswith("http"):
                url = f"{self.BASE_URL}{url}"
        
        item_text = await item.inner_text()
        mileage = self._extract_mileage(item_text)
        engine_volume, fuel_type, transmission = self._extract_specs(item_text)
        
        region = ""
        geo_elem = await item.query_selector('[data-name="BulletinGeo"]')
        if geo_elem:
            region = await geo_elem.inner_text()
        
        photo_url = ""
        img_elem = await item.query_selector('img')
        if img_elem:
            photo_url = await img_elem.get_attribute("src")
        
        external_id = self._generate_external_id(brand, model, year, price, mileage)
        
        return {
            "source": "drom",
            "external_id": external_id,
            "url": url,
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": mileage,
            "engine_volume": engine_volume,
            "fuel_type": fuel_type,
            "transmission": transmission,
            "body_type": "",
            "vin": "",
            "region": region,
            "price_rub": price,
            "description": item_text[:500],
            "photos": [photo_url] if photo_url else [],
            "seller_info": {"name": "", "type": ""}
        }
    
    def _extract_item_from_soup(self, item) -> Dict[str, Any]:
        """Извлекаем данные из карточки (BeautifulSoup)"""
        
        title = ""
        for selector in ['h3', '[data-name="BulletinTitle"]', 'a']:
            title_elem = item.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 5:
                    break
        
        if not title:
            return None
        
        brand, model, year = self._parse_title(title)
        
        price = 0
        for selector in ['[data-name="BulletinPrice"]', '[class*="Price"]', 'span']:
            price_elem = item.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price = self._extract_price(price_text)
                if price > 0:
                    break
        
        url = ""
        link_elem = item.select_one('a[href*="/bulletin/"]')
        if link_elem:
            url = link_elem.get('href', '')
            if url and not url.startswith("http"):
                url = f"{self.BASE_URL}{url}"
        
        item_text = item.get_text()
        mileage = self._extract_mileage(item_text)
        engine_volume, fuel_type, transmission = self._extract_specs(item_text)
        
        region = ""
        geo_elem = item.select_one('[data-name="BulletinGeo"]')
        if geo_elem:
            region = geo_elem.get_text(strip=True)
        
        photo_url = ""
        img_elem = item.select_one('img')
        if img_elem:
            photo_url = img_elem.get('src', '')
        
        external_id = self._generate_external_id(brand, model, year, price, mileage)
        
        return {
            "source": "drom",
            "external_id": external_id,
            "url": url,
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": mileage,
            "engine_volume": engine_volume,
            "fuel_type": fuel_type,
            "transmission": transmission,
            "body_type": "",
            "vin": "",
            "region": region,
            "price_rub": price,
            "description": item_text[:500],
            "photos": [photo_url] if photo_url else [],
            "seller_info": {"name": "", "type": ""}
        }
    
    def _build_search_url(self, params: Dict[str, Any]) -> str:
        """Формируем URL поиска"""
        
        query = params.get("query", "").lower()
        region = params.get("region", "moscow")
        
        region_code = self.REGION_CODES.get(region.lower(), "77")
        
        base_url = f"{self.BASE_URL}/b/u/"
        
        if query:
            parts = query.split()
            if len(parts) >= 2:
                brand, model = parts[0], parts[1]
                base_url = f"{self.BASE_URL}/b/u/{brand}/{model}/"
            elif len(parts) == 1:
                brand = parts[0]
                base_url = f"{self.BASE_URL}/b/u/{brand}/"
        
        query_params = [f"region={region_code}"]
        
        if params.get("year_min"):
            query_params.append(f"year_from={params['year_min']}")
        
        if params.get("year_max"):
            query_params.append(f"year_to={params['year_max']}")
        
        if params.get("price_min"):
            query_params.append(f"price_from={params['price_min']}")
        
        if params.get("price_max"):
            query_params.append(f"price_to={params['price_max']}")
        
        url = base_url + "?" + "&".join(query_params)
        
        return url
    
    def _parse_title(self, title: str) -> tuple:
        """Парсим название"""
        
        brand, model, year = "", "", 0
        
        parts = title.split()
        if len(parts) >= 1:
            brand = parts[0]
        if len(parts) >= 2:
            model = parts[1]
        
        year_match = re.search(r'\b(19|20)\d{2}\b', title)
        if year_match:
            year = int(year_match.group())
        
        return brand, model, year
    
    def _extract_price(self, text: str) -> int:
        """Извлекаем цену"""
        match = re.search(r'(\d[\d\s]*)\s*₽', text)
        if match:
            return int(match.group(1).replace(" ", ""))
        return 0
    
    def _extract_mileage(self, text: str) -> int:
        """Извлекаем пробег"""
        match = re.search(r'(\d{1,3}(?:\s\d{3})*|\d+)\s*км', text)
        if match:
            return int(match.group(1).replace(" ", ""))
        return 0
    
    def _extract_specs(self, text: str) -> tuple:
        """Извлекаем характеристики"""
        
        engine_volume, fuel_type, transmission = 0.0, "", ""
        
        engine_match = re.search(r'(\d+\.?\d*)\s*л', text)
        if engine_match:
            engine_volume = float(engine_match.group(1))
        
        text_lower = text.lower()
        if "бензин" in text_lower:
            fuel_type = "бензин"
        elif "дизель" in text_lower:
            fuel_type = "дизель"
        
        if "автомат" in text_lower or "акпп" in text_lower:
            transmission = "автомат"
        elif "механик" in text_lower:
            transmission = "механика"
        
        return engine_volume, fuel_type, transmission
    
    def _generate_external_id(self, brand: str, model: str, year: int, price: int, mileage: int) -> str:
        """Детерминированный ID"""
        data = f"{brand}_{model}_{year}_{price}_{mileage}"
        hash_value = hashlib.md5(data.encode()).hexdigest()[:12]
        return f"drom_{hash_value}"
    
    async def parse_listing(self, url: str) -> Dict[str, Any]:
        """Парсинг отдельного объявления"""
        return {}

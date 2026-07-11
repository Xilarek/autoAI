from typing import List, Dict, Any
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
import asyncio
from .base import BaseParser

class AvitoParser(BaseParser):
    """Реальный парсер для Авито"""
    
    BASE_URL = "https://www.avito.ru"
    SEARCH_URL = f"{BASE_URL}/rossiya/avtomobili"
    
    async def parse_search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Парсинг страницы поиска Авито
        
        Параметры:
        - query: поисковый запрос (например, "Tiguan")
        - region: регион (например, "moskva")
        - price_max: максимальная цена
        - year_min: минимальный год
        """
        
        async with async_playwright() as p:
            # Запускаем браузер в stealth-режиме
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                ]
            )
            
            context = await browser.new_context(
                user_agent=self._random_ua(),
                viewport={"width": 1920, "height": 1080},
                locale="ru-RU",
            )
            
            # Добавляем скрипты для обхода детекции
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)
            
            page = await context.new_page()
            
            try:
                # Формируем URL поиска
                search_url = self._build_search_url(params)
                
                print(f"Парсинг URL: {search_url}")
                
                # Переходим на страницу
                await page.goto(search_url, wait_until="networkidle", timeout=30000)
                
                # Ждем загрузки контента
                await page.wait_for_timeout(3000)
                
                # Проверяем, не заблокированы ли мы
                content = await page.content()
                if "Доступ ограничен" in content or "captcha" in content.lower():
                    print("⚠️ Обнаружена блокировка или капча")
                    return []
                
                # Парсим объявления
                listings = await self._extract_listings(page)
                
                print(f"✅ Найдено объявлений: {len(listings)}")
                
                return listings
                
            except Exception as e:
                print(f"❌ Ошибка парсинга: {e}")
                return []
            
            finally:
                await browser.close()
    
    def _build_search_url(self, params: Dict[str, Any]) -> str:
        """Формируем URL поиска с параметрами"""
        
        query = params.get("query", "")
        region = params.get("region", "rossiya")
        
        # Базовый URL
        url = f"{self.BASE_URL}/{region}/avtomobili"
        
        # Добавляем параметры
        query_params = []
        
        if query:
            query_params.append(f"q={query}")
        
        if params.get("price_max"):
            query_params.append(f"pmax={params['price_max']}")
        
        if params.get("price_min"):
            query_params.append(f"pmin={params['price_min']}")
        
        if params.get("year_min"):
            query_params.append(f"year_min={params['year_min']}")
        
        if params.get("year_max"):
            query_params.append(f"year_max={params['year_max']}")
        
        if query_params:
            url += "?" + "&".join(query_params)
        
        return url
    
    async def _extract_listings(self, page) -> List[Dict[str, Any]]:
        """Извлекаем объявления со страницы"""
        
        listings = []
        
        # Ждем появления карточек объявлений
        try:
            await page.wait_for_selector('[data-marker="item"]', timeout=10000)
        except:
            print("Не найдены карточки объявлений")
            return []
        
        # Получаем все карточки
        items = await page.query_selector_all('[data-marker="item"]')
        
        for item in items[:20]:  # Ограничиваем до 20 объявлений
            try:
                listing = await self._extract_item_data(item)
                if listing:
                    listings.append(listing)
            except Exception as e:
                print(f"Ошибка извлечения объявления: {e}")
                continue
        
        return listings
    
    async def _extract_item_data(self, item) -> Dict[str, Any]:
        """Извлекаем данные из одной карточки"""
        
        # Название
        title_elem = await item.query_selector('[itemprop="name"]')
        title = await title_elem.inner_text() if title_elem else ""
        
        # Парсим название: "Volkswagen Tiguan, 2019"
        brand, model, year = self._parse_title(title)
        
        # Цена
        price_elem = await item.query_selector('[itemprop="price"] meta[itemprop="price"]')
        price = await price_elem.get_attribute("content") if price_elem else "0"
        price = int(price) if price and price.isdigit() else 0
        
        # Ссылка
        link_elem = await item.query_selector('a[data-marker="item-title"]')
        url = await link_elem.get_attribute("href") if link_elem else ""
        if url and not url.startswith("http"):
            url = f"{self.BASE_URL}{url}"
        
        # Пробег
        params_elem = await item.query_selector('[data-marker="item-params"]')
        params_text = await params_elem.inner_text() if params_elem else ""
        mileage = self._extract_mileage(params_text)
        
        # Характеристики
        engine_volume, fuel_type, transmission = self._extract_specs(params_text)
        
        # Регион
        geo_elem = await item.query_selector('[data-marker="item-address"]')
        region = await geo_elem.inner_text() if geo_elem else ""
        
        # Описание (короткое)
        desc_elem = await item.query_selector('[data-marker="item-description"]')
        description = await desc_elem.inner_text() if desc_elem else ""
        
        # Фото
        img_elem = await item.query_selector('img[itemprop="image"]')
        photo_url = await img_elem.get_attribute("src") if img_elem else ""
        
        # Извлекаем ID из URL
        external_id = self._extract_id_from_url(url)
        
        return {
            "source": "avito",
            "external_id": external_id,
            "url": url,
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": mileage,
            "engine_volume": engine_volume,
            "fuel_type": fuel_type,
            "transmission": transmission,
            "body_type": "",  # Нужно парсить отдельно
            "vin": "",  # Скрыт до звонка
            "region": region,
            "price_rub": price,
            "description": description,
            "photos": [photo_url] if photo_url else [],
            "seller_info": {
                "name": "",  # Нужно парсить отдельно
                "type": ""
            }
        }
    
    def _parse_title(self, title: str) -> tuple:
        """Парсим название: "Volkswagen Tiguan, 2019" """
        
        brand = ""
        model = ""
        year = 0
        
        # Разделяем по запятой
        parts = title.split(",")
        
        if len(parts) >= 1:
            car_parts = parts[0].strip().split()
            if len(car_parts) >= 2:
                brand = car_parts[0]
                model = " ".join(car_parts[1:])
        
        if len(parts) >= 2:
            year_str = parts[1].strip()
            year = int(year_str) if year_str.isdigit() else 0
        
        return brand, model, year
    
    def _extract_mileage(self, text: str) -> int:
        """Извлекаем пробег из текста"""
        
        # Ищем паттерн: "120 000 км" или "120000 км"
        match = re.search(r'(\d{1,3}(?:\s\d{3})*|\d+)\s*км', text)
        if match:
            mileage_str = match.group(1).replace(" ", "")
            return int(mileage_str)
        
        return 0
    
    def _extract_specs(self, text: str) -> tuple:
        """Извлекаем характеристики: объем двигателя, топливо, КПП"""
        
        engine_volume = 0.0
        fuel_type = ""
        transmission = ""
        
        # Объем двигателя: "2.0 л"
        engine_match = re.search(r'(\d+\.?\d*)\s*л', text)
        if engine_match:
            engine_volume = float(engine_match.group(1))
        
        # Топливо
        if "бензин" in text.lower():
            fuel_type = "бензин"
        elif "дизель" in text.lower():
            fuel_type = "дизель"
        elif "гибрид" in text.lower():
            fuel_type = "гибрид"
        elif "электро" in text.lower():
            fuel_type = "электро"
        
        # КПП
        if "автомат" in text.lower() or "акпп" in text.lower():
            transmission = "автомат"
        elif "механик" in text.lower() or "мкпп" in text.lower():
            transmission = "механика"
        elif "робот" in text.lower():
            transmission = "робот"
        elif "вариатор" in text.lower():
            transmission = "вариатор"
        
        return engine_volume, fuel_type, transmission
    
    def _extract_id_from_url(self, url: str) -> str:
        """Извлекаем ID объявления из URL"""
        
        # URL формат: https://www.avito.ru/moskva/avtomobili/volkswagen_tiguan_2019_123456789
        match = re.search(r'_(\d+)$', url)
        if match:
            return match.group(1)
        
        return ""
    
    async def parse_listing(self, url: str) -> Dict[str, Any]:
        """Парсинг отдельного объявления (детальная информация)"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self._random_ua(),
                viewport={"width": 1920, "height": 1080},
            )
            
            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)
                
                # Здесь можно извлечь дополнительную информацию:
                # - Полное описание
                # - Все фото
                # - VIN (если указан)
                # - Информация о продавце
                # TODO: Реализовать детальное парсинг
                
                return {}
                
            except Exception as e:
                print(f"Ошибка парсинга объявления: {e}")
                return {}
            
            finally:
                await browser.close()
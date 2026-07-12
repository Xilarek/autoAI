"""
Парсер Дрома — только специфика площадки.

Вся общая логика (Apify API, retry, errors, HTTP client) — в BaseApifyParser.
Здесь только то, что уникально для Дрома:
- URL формат: auto.drom.ru/region/brand/model/?minyear=...
- Параметры: minyear, maxyear, minprice, maxprice
- Регионы: moscow, saint-petersburg, ...
"""

from typing import Dict, Any, Optional
import re
from app.parsers.base import BaseApifyParser
from app.parsers.registry import register_parser
from app.core.logger import setup_logger

logger = setup_logger(__name__)


@register_parser("drom")
class DromParser(BaseApifyParser):
    """Парсер Дрома — переопределяет только специфику"""
    
    PLATFORM = "drom"
    
    # Оставляем только website-content-crawler (он точно работает)
    # web-scraper и cheerio-scraper требуют одобрения в Apify Console
    ACTORS = [
        "apify~website-content-crawler",
    ]
    
    # Маппинг регионов: русское название → slug в URL
    REGION_MAP = {
        "москва": "moscow",
        "moscow": "moscow",
        "санкт-петербург": "saint-petersburg",
        "spb": "saint-petersburg",
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
    
    def _build_search_url(self, params: Dict[str, Any]) -> str:
        """
        Специфика Дрома: auto.drom.ru/region/brand/model/?minyear=...
        
        Параметры Дрома:
        - minyear, maxyear (не year_from/year_to)
        - minprice, maxprice (не price_from/price_to)
        """
        
        query = params.get("query", "").lower().strip()
        region = params.get("region", "moscow").lower().strip()
        
        # Находим slug региона
        region_slug = self.REGION_MAP.get(region, region.replace(' ', '-'))
        
        # Строим URL
        if not query:
            base_url = f"https://auto.drom.ru/{region_slug}/"
        else:
            parts = query.split()
            if len(parts) >= 2:
                brand, model = parts[0], parts[1]
                base_url = f"https://auto.drom.ru/{region_slug}/{brand}/{model}/"
            elif len(parts) == 1:
                base_url = f"https://auto.drom.ru/{region_slug}/{parts[0]}/"
            else:
                base_url = f"https://auto.drom.ru/{region_slug}/"
        
        # Параметры Дрома
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
    
    def _transform_listing(self, raw_data: Dict) -> Optional[Dict[str, Any]]:
        """Специфика Дрома: преобразование в наш формат"""
        
        source = raw_data.get("source")
        
        if source == "jsonld":
            return self._transform_jsonld(raw_data)
        elif source == "markdown":
            return self._transform_markdown(raw_data)
        
        return None
    
    def _transform_jsonld(self, raw_data: Dict) -> Optional[Dict[str, Any]]:
        """Трансформация JSON-LD для Дрома"""
        
        name = raw_data.get("name", "")
        price = raw_data.get("price", 0)
        url = raw_data.get("url", "")
        
        brand, model, year = self._parse_title(name)
        if not brand:
            return None
        
        region = self._extract_region_from_url(url, r'auto\.drom\.ru/([a-z-]+)/')
        
        return {
            "source": "drom",
            "external_id": self._generate_external_id(url),
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
    
    def _transform_markdown(self, raw_data: Dict) -> Optional[Dict[str, Any]]:
        """Трансформация markdown для Дрома (fallback)"""
        
        text = raw_data.get("text", "")
        url = raw_data.get("url", "")
        
        # Ищем название (марка модель год)
        title_match = re.search(
            r'(Audi|BMW|Chevrolet|Citroen|Ford|Honda|Hyundai|Kia|Lada|Lexus|'
            r'Mazda|Mercedes|Mini|Mitsubishi|Nissan|Opel|Peugeot|Porsche|'
            r'Renault|Skoda|Subaru|Suzuki|Toyota|Volkswagen|Volvo|УАЗ)\s+'
            r'(\w+)\s*,?\s*(\d{4})',
            text, re.IGNORECASE
        )
        
        if not title_match:
            return None
        
        brand = title_match.group(1).capitalize()
        model = title_match.group(2).capitalize()
        year = int(title_match.group(3))
        
        # Извлекаем характеристики через утилиты базового класса
        price = self._extract_price_from_text(text)
        if price < 50000:
            return None
        
        mileage = self._extract_mileage_from_text(text)
        engine_volume = self._extract_engine_from_text(text)
        fuel_type = self._extract_fuel_from_text(text)
        transmission = self._extract_transmission_from_text(text)
        
        # Ссылка на объявление
        url_match = re.search(r'https://auto\.drom\.ru/\S+/\d+\.html', text)
        if url_match:
            url = url_match.group(0)
        
        # Регион
        region = ""
        region_match = re.search(r'(Москва|Санкт-Петербург|Московская|Ленинградская)', text)
        if region_match:
            region = region_match.group(1)
        
        return {
            "source": "drom",
            "external_id": self._generate_external_id(url),
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
            "description": text[:500],
            "photos": [],
            "seller_info": {"name": "", "type": ""}
        }

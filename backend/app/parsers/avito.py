from typing import Any, Dict, List

from app.core.logger import setup_logger

from .base import BaseParser

logger = setup_logger(__name__)


class AvitoParser(BaseParser):
    """Парсер Авито (заглушка для MVP)"""

    async def parse_search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Парсинг поиска Авито (заглушка)"""
        logger.warning("Парсер Авито не реализован — возвращаем пустой список")
        return []

    async def parse_listing(self, url: str) -> Dict[str, Any]:
        """Парсинг отдельного объявления (заглушка)"""
        logger.warning("Парсинг объявления Авито не реализован")
        return {}

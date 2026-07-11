import random
from typing import Any, Dict, List


class BaseParser:
    """Базовый класс для парсеров"""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def _random_ua(self) -> str:
        return random.choice(self.USER_AGENTS)

    async def parse_search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Парсинг страницы поиска"""
        raise NotImplementedError

    async def parse_listing(self, url: str) -> Dict[str, Any]:
        """Парсинг отдельного объявления"""
        raise NotImplementedError

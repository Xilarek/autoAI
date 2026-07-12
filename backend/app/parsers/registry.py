"""
Реестр парсеров — отдельный файл для избежания циклического импорта.

Архитектура:
- registry.py — содержит registry и декоратор (не импортирует площадки)
- platforms/*.py — импортируют registry.py (не parsers/__init__.py)
- parsers/__init__.py — импортирует площадки для регистрации
"""

from typing import Dict, Type
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# Реестр всех парсеров: {"drom": DromParser, "avito": AvitoParser, ...}
_PARSER_REGISTRY: Dict[str, Type] = {}


def register_parser(platform: str):
    """
    Декоратор для регистрации парсера.
    
    Использование:
        from app.parsers.registry import register_parser
        
        @register_parser("drom")
        class DromParser(BaseApifyParser):
            ...
    """
    def decorator(cls):
        _PARSER_REGISTRY[platform] = cls
        logger.info(f"📝 Зарегистрирован парсер: {platform} -> {cls.__name__}")
        return cls
    return decorator


def get_parser(platform: str):
    """
    Получить экземпляр парсера по названию площадки.
    
    Raises:
        ValueError: если площадка не зарегистрирована
    """
    if platform not in _PARSER_REGISTRY:
        available = ", ".join(_PARSER_REGISTRY.keys()) or "(none)"
        raise ValueError(f"Unknown platform: '{platform}'. Available: {available}")
    
    return _PARSER_REGISTRY[platform]()


def list_platforms() -> list:
    """Список всех поддерживаемых площадок"""
    return list(_PARSER_REGISTRY.keys())

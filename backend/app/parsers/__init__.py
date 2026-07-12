"""
Реестр парсеров и фабрика.

Использование:
    from app.parsers import get_parser, list_platforms
    
    parser = get_parser("drom")
    listings = await parser.parse_search(params)

Архитектура:
- registry.py — содержит registry (не импортирует площадки)
- platforms/*.py — импортируют registry.py
- parsers/__init__.py — импортирует площадки для регистрации
"""

# Импортируем из registry
from app.parsers.registry import get_parser, list_platforms, register_parser

# ============================================
# ИМПОРТ ПЛАТФОРМ для автоматической регистрации
# При добавлении новой площадки — добавить импорт здесь
# ============================================

from app.parsers.platforms import drom  # noqa: F401, E402
from app.parsers.platforms import avito  # noqa: F401, E402
# from app.parsers.platforms import auto_ru  # раскомментировать при добавлении

__all__ = ["get_parser", "list_platforms", "register_parser"]

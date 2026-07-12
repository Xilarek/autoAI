"""Кастомные исключения для AutoAI"""


class ParserError(Exception):
    """Базовое исключение парсера"""
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(message)


class ParserTimeoutError(ParserError):
    """Таймаут парсера"""
    pass


class ParserUnavailableError(ParserError):
    """Парсер недоступен"""
    pass


class ParserBlockedError(ParserError):
    """Парсер заблокирован (капча, 403)"""
    pass


class ParserEmptyResultError(ParserError):
    """Парсер вернул пустой результат"""
    pass


class ApifyAPIError(ParserError):
    """Ошибка Apify API"""
    pass


class InvalidURLError(ParserError):
    """Неправильный URL"""
    pass

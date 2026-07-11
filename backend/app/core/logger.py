import logging
import sys
from typing import Optional


def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Настройка логгера"""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level or logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(handler)

    logger.propagate = False
    return logger


# Глобальный логгер
logger = setup_logger("autoai")

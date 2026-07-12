"""Circuit Breaker для внешних сервисов"""

import pybreaker
from app.core.logger import setup_logger

logger = setup_logger(__name__)

# Circuit breaker для Apify
# Если 5 ошибок за 60 секунд — открываем цепь на 60 секунд
apify_breaker = pybreaker.CircuitBreaker(
    fail_max=5,           # Макс ошибок перед открытием
    reset_timeout=60,     # Секунд до попытки восстановления
    name="apify_api",
)


def on_apify_state_change(old_state, new_state):
    """Callback при изменении состояния circuit breaker"""
    logger.warning(f"⚡ Apify circuit breaker: {old_state} → {new_state}")


apify_breaker.add_listener(pybreaker.CircuitBreakerStateChange(on_apify_state_change))

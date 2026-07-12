"""Celery приложение"""

from celery import Celery
from app.core.config import settings

# Инициализация Celery
celery_app = Celery(
    "autoai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.ai_tasks", "app.tasks.parse_tasks"],
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_max_tasks_per_child=100,
    task_acks_late=True,  # Подтверждение только после выполнения
    worker_prefetch_multiplier=1,  # Не брать больше 1 задачи за раз
)

# Автоматическое обнаружение задач
celery_app.autodiscover_tasks(["app.tasks"])

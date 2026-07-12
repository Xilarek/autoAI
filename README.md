# 🚗 AutoAI - Система умного подбора автомобилей

## 🚀 Быстрый старт

### Запуск проекта
./start.sh start    # Запустить
./start.sh stop     # Остановить
./start.sh restart  # Перезапустить
./start.sh status   # Статус
./start.sh logs     # Логи
./start.sh ai       # AI-анализ
./start.sh parse    # Парсинг Дрома

parsers/
├── init.py # Registry + фабрика (get_parser, list_platforms)
├── base.py # BaseApifyParser — общая логика для всех площадок
├── README.md # Этот файл
└── platforms/ # 🔌 ПЛАГИНЫ ПЛОЩАДОК
├── init.py
├── drom.py # Только специфика Дрома
├── avito.py # Только специфика Авито
└── auto_ru.py # (будет добавлен)


## Как это работает

### 1. BaseApifyParser (base.py)

Содержит **всю общую логику**:
- Работа с Apify API (запуск актора, ожидание результата, получение датасета)
- Retry логика, обработка ошибок
- HTTP connection pooling
- Извлечение из JSON-LD и markdown
- Утилиты для парсинга (цена, пробег, топливо, КПП)

### 2. Площадки (platforms/*.py)

Каждая площадка наследуется от `BaseApifyParser` и переопределяет **только специфику**:
- `PLATFORM` — название площадки
- `ACTORS` — список Apify акторов
- `REGION_MAP` — маппинг регионов
- `_build_search_url(params)` — построить URL поиска
- `_transform_listing(raw_data)` — преобразовать в наш формат
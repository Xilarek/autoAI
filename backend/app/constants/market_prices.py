"""Эталонные рыночные цены для популярных моделей авто"""

# Формат: (brand, model, year) -> price_rub
MARKET_PRICES = {
    ("volkswagen", "tiguan", 2019): 2400000,
    ("volkswagen", "tiguan", 2020): 2700000,
    ("toyota", "camry", 2020): 2900000,
    ("toyota", "camry", 2019): 2600000,
    ("kia", "sportage", 2018): 2000000,
    ("hyundai", "solaris", 2021): 1500000,
    ("bmw", "x5", 2017): 3300000,
    ("mazda", "cx-5", 2019): 2500000,
    ("nissan", "qashqai", 2020): 2200000,
    ("skoda", "octavia", 2018): 1700000,
    ("ford", "focus", 2019): 1400000,
    ("renault", "duster", 2020): 1300000,
}

# Базовые цены по классам авто
BASE_PRICES = {
    "economy": 1000000,
    "middle": 2000000,
    "premium": 3500000,
}

# Премиум бренды
PREMIUM_BRANDS = ["bmw", "mercedes", "audi", "lexus", "porsche", "volvo"]

# Эконом бренды
ECONOMY_BRANDS = ["hyundai", "kia", "renault", "lada", "chery"]

# Нормальный пробег в год (км)
NORMAL_MILEAGE_PER_YEAR = 15000

# Амортизация в год (10%)
DEPRECIATION_RATE = 0.1

# Минимальный коэффициент стоимости (30% от новой)
MIN_VALUE_FACTOR = 0.3

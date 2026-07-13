import asyncio
import sys
from pathlib import Path

# Добавляем путь к backend, чтобы импортировать настройки
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import settings
from app.models.car_listing import CarListing

def fix_text(text: str) -> str:
    """Исправляет двойную кодировку (UTF-8 -> cp1251 -> UTF-8)"""
    if not text:
        return text
    try:
        # Пытаемся закодировать в cp1251 и декодировать обратно в utf-8
        return text.encode('cp1251').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Если не получилось, значит строка уже нормальная или повреждена иначе
        return text

async def main():
    # Используем синхронную замену URL для psycopg2, если нужно, или asyncpg
    # Для простоты используем тот же URL, но убедимся, что он рабочий
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    async with AsyncSession(engine) as session:
        # Получаем все не удаленные объявления
        result = await session.execute(
            select(CarListing).where(CarListing.is_deleted == False)
        )
        listings = result.scalars().all()
        
        fixed_count = 0
        for listing in listings:
            needs_update = False
            
            # Список текстовых полей, которые могли пострадать
            text_fields = [
                'brand', 'model', 'fuel_type', 'transmission', 
                'body_type', 'region', 'description', 'ai_summary', 'ai_verdict'
            ]
            
            for field in text_fields:
                original_value = getattr(listing, field)
                if isinstance(original_value, str):
                    fixed_value = fix_text(original_value)
                    if fixed_value != original_value:
                        setattr(listing, field, fixed_value)
                        needs_update = True
            
            # Также проверяем JSON поля (seller_info, ai_risks)
            for json_field in ['seller_info', 'ai_risks']:
                original_value = getattr(listing, json_field)
                if isinstance(original_value, dict):
                    new_dict = {}
                    changed = False
                    for k, v in original_value.items():
                        fixed_k = fix_text(str(k))
                        fixed_v = fix_text(str(v)) if isinstance(v, str) else v
                        if fixed_k != k or fixed_v != v:
                            changed = True
                        new_dict[fixed_k] = fixed_v
                    
                    if changed:
                        setattr(listing, json_field, new_dict)
                        needs_update = True

            if needs_update:
                fixed_count += 1
                
        if fixed_count > 0:
            await session.commit()
            print(f"✅ Успешно исправлено записей: {fixed_count}")
        else:
            print("ℹ️ Все записи уже в правильной кодировке или не требуют исправлений.")
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
"""Скрипт для инициализации базы данных"""
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from pyramid.paster import get_appsettings
from vols_gis.db import Base
from vols_gis.models import Node, Vols, Fiber, Link, WebMap, User

def init_db():
    """Создает все таблицы в базе данных"""
    # Загружаем настройки из development.ini
    settings = get_appsettings('development.ini')
    database_url = settings.get('sqlalchemy.url')
    
    if not database_url:
        print("Ошибка: не найден sqlalchemy.url в настройках")
        return
    
    print(f"Подключение к базе данных: {database_url.split('@')[1] if '@' in database_url else database_url}")
    
    # Создаем движок
    engine = create_engine(database_url)
    
    # Импортируем все модели (важно для создания таблиц)
    print("Импорт моделей...")
    print("  - Node")
    print("  - Vols")
    print("  - Fiber")
    print("  - Link")
    print("  - WebMap")
    print("  - User")
    
    # Создаем все таблицы
    print("\nСоздание таблиц...")
    try:
        Base.metadata.create_all(engine)
        print("✅ Таблицы успешно созданы!")
        
        # Проверяем существование таблиц
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\nТаблицы в базе данных ({len(tables)}):")
        for table in sorted(tables):
            print(f"  - {table}")
            
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    print("="*60)
    print("Инициализация базы данных Vols GIS")
    print("="*60)
    success = init_db()
    if success:
        print("\n" + "="*60)
        print("✅ База данных готова к использованию!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ Ошибка инициализации базы данных")
        print("="*60)
        sys.exit(1)



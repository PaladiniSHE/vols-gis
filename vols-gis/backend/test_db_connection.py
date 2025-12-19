"""Тест подключения к базе данных"""
import sys
from sqlalchemy import create_engine, text
from pyramid.paster import get_appsettings

def test_db_connection():
    """Проверяет подключение к базе данных"""
    try:
        settings = get_appsettings('development.ini')
        database_url = settings.get('sqlalchemy.url')
        
        print(f"Подключение к БД: {database_url.split('@')[1] if '@' in database_url else database_url}")
        
        engine = create_engine(database_url)
        
        # Пробуем подключиться
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Подключение к БД успешно!")
            
            # Проверяем наличие таблиц
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            print(f"\nТаблицы в базе данных ({len(tables)}):")
            for table in tables:
                print(f"  - {table}")
            
            # Проверяем наличие нужных таблиц
            required_tables = ['nodes', 'vols', 'fibers', 'links']
            missing_tables = [t for t in required_tables if t not in tables]
            
            if missing_tables:
                print(f"\n⚠️ Отсутствуют таблицы: {', '.join(missing_tables)}")
                print("Запустите init_db.py для создания таблиц")
            else:
                print("\n✅ Все необходимые таблицы присутствуют")
            
            return True
            
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("="*60)
    print("Тест подключения к базе данных")
    print("="*60)
    success = test_db_connection()
    print("="*60)
    sys.exit(0 if success else 1)



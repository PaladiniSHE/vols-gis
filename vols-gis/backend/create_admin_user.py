"""Скрипт для создания администратора"""
from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from vols_gis.models.users import User
from vols_gis.models.base import Base
import hashlib
import sys
import os

def hash_password(password: str) -> str:
    """Хеширует пароль"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin():
    """Создает администратора, если его еще нет"""
    # Настройка подключения к БД
    config_uri = 'development.ini'
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        # Проверяем, есть ли уже админ
        admin = db.query(User).filter(User.username == 'admin').first()
        if admin:
            print(f"✅ Администратор уже существует: {admin.username}")
            print(f"   Email: {admin.email}")
            print(f"   Role: {admin.role}")
            return
        
        # Создаем нового администратора
        admin = User(
            username='admin',
            email='admin@vols-gis.local',
            password_hash=hash_password('admin123'),
            role='admin',
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("✅ Администратор успешно создан!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@vols-gis.local")
        print("   Role: admin")
        print("\n⚠️  ВАЖНО: Измените пароль после первого входа!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при создании администратора: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == '__main__':
    print("="*60)
    print("Создание администратора Vols GIS")
    print("="*60)
    create_admin()
    print("="*60)


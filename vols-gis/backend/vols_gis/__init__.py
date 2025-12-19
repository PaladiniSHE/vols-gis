"""Vols GIS - Минималистичный аналог NextGIS Web для учета ВОЛС"""
from pyramid.config import Configurator
from pyramid.tweens import EXCVIEW
from sqlalchemy import engine_from_config, text
from sqlalchemy.orm import sessionmaker
from .db import Base


def main(global_config, **settings):
    """Возвращает Pyramid WSGI приложение."""
    import logging
    logger = logging.getLogger(__name__)
    
    config = Configurator(settings=settings)
    
    # Настройка базы данных
    engine = None
    DBSession = None
    try:
        engine = engine_from_config(settings, prefix='sqlalchemy.')
        # Тестируем подключение
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        logger.info('✅ База данных успешно подключена')
    except Exception as e:
        logger.error(f'❌ Ошибка подключения к базе данных: {e}')
        import traceback
        logger.error(traceback.format_exc())
        logger.warning('⚠️ Приложение запущено без БД. Запросы к БД будут возвращать ошибки.')
        # Создаем заглушку для DBSession
        DBSession = None
    
    # Добавляем DBSession в request
    def get_db(request):
        if DBSession is None:
            logger.warning('Попытка создать DB сессию, но БД не подключена')
            # Возвращаем None вместо исключения, чтобы view мог обработать это
            return None
        try:
            session = DBSession()
            # Проверяем, что сессия действительно работает
            session.execute(text("SELECT 1"))
            return session
        except Exception as e:
            logger.error(f'Ошибка создания DB сессии: {e}')
            import traceback
            logger.error(traceback.format_exc())
            # Возвращаем None вместо исключения
            return None
    
    config.add_request_method(
        get_db,
        'db',
        reify=True
    )
    
    # Подключение routes
    config.include('.routes')
    
    # Exception views для обработки всех ошибок (должен быть после routes)
    config.scan('vols_gis.exception_views')
    
    # Закрытие сессии после запроса
    config.add_tween('vols_gis.db_close_tween.db_close_tween_factory', under=EXCVIEW)
    
    # CORS middleware (должен быть над EXCVIEW, чтобы перехватывать все ошибки)
    # Используем under=EXCVIEW чтобы он был последним в цепочке
    config.add_tween('vols_gis.middleware.cors.cors_tween_factory', under=EXCVIEW)
    
    # Статические файлы для frontend
    import os
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'frontend')
    config.add_static_view('static', frontend_path, cache_max_age=3600)
    
    return config.make_wsgi_app()


"""Tween для автоматического закрытия DB сессии после запроса"""
from pyramid.tweens import EXCVIEW


def db_close_tween_factory(handler, registry):
    """Закрывает DB сессию после обработки запроса"""
    def db_close_tween(request):
        try:
            response = handler(request)
            return response
        except Exception as e:
            # Логируем ошибку перед закрытием сессии
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Ошибка в обработчике запроса: {e}', exc_info=True)
            raise
        finally:
            if hasattr(request, 'db') and request.db is not None:
                try:
                    request.db.close()
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f'Ошибка при закрытии DB сессии: {e}')
    
    return db_close_tween





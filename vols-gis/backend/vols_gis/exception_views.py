"""Exception views для обработки всех ошибок"""
from pyramid.view import exception_view_config
from pyramid.response import Response
import logging

logger = logging.getLogger(__name__)


@exception_view_config(Exception)
def exception_view(exc, request):
    """Обрабатывает все необработанные исключения и возвращает JSON"""
    logger.error(f'Необработанное исключение: {exc}', exc_info=True)
    
    # Определяем тип ошибки
    error_type = type(exc).__name__
    error_message = str(exc)
    
    # Определяем понятное сообщение
    if 'connection' in error_message.lower() or 'postgresql' in error_message.lower() or 'database' in error_message.lower():
        message = 'Ошибка подключения к базе данных. Убедитесь, что PostgreSQL запущен на порту 5433.'
    elif 'OperationalError' in error_type:
        message = 'Ошибка подключения к базе данных. PostgreSQL не запущен или недоступен.'
    else:
        message = f'Внутренняя ошибка сервера: {error_message}'
    
    return Response(
        json_body={
            'error': 'Internal Server Error',
            'message': message,
            'type': error_type,
            'details': error_message
        },
        status=500,
        content_type='application/json'
    )



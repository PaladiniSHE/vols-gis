"""Простой CORS middleware"""
from pyramid.response import Response


def cors_tween_factory(handler, registry):
    """Добавляет CORS заголовки к ответам и перехватывает ошибки"""
    def cors_tween(request):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            response = handler(request)
        except Exception as e:
            # Если произошла ошибка, создаем JSON ответ
            logger.error(f'Ошибка в обработчике: {e}', exc_info=True)
            
            # Определяем тип ошибки
            error_message = str(e)
            error_type = type(e).__name__
            
            if 'connection' in error_message.lower() or 'postgresql' in error_message.lower() or 'database' in error_message.lower() or 'OperationalError' in error_type:
                error_msg = 'Ошибка подключения к базе данных. Убедитесь, что PostgreSQL запущен на порту 5433.'
            else:
                error_msg = f'Internal Server Error: {error_message}'
            
            response = Response(
                json_body={
                    'error': 'Internal Server Error',
                    'message': error_msg,
                    'type': error_type,
                    'details': error_message
                },
                status=500,
                content_type='application/json'
            )
        
        # Добавляем CORS заголовки ко всем ответам
        if response:
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Max-Age'] = '3600'
            
            # Устанавливаем Content-Type для JSON ответов
            if hasattr(response, 'content_type') and 'json' in response.content_type:
                response.headers['Content-Type'] = 'application/json'
            elif 'Content-Type' not in response.headers or 'text/html' in response.headers.get('Content-Type', ''):
                # Если это HTML ошибка, заменяем на JSON
                response.headers['Content-Type'] = 'application/json'
        
        # Обработка preflight запросов
        if request.method == 'OPTIONS':
            return Response(status=200, headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            })
        
        return response
    
    return cors_tween





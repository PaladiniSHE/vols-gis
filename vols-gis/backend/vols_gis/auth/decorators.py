"""Декораторы для авторизации"""
from functools import wraps
from pyramid.view import view_config
from pyramid.response import Response
from ..auth.jwt import get_user_from_token
import logging

logger = logging.getLogger(__name__)


def get_token_from_request(request):
    """Извлекает токен из заголовка Authorization"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]  # Убираем "Bearer "
    return None


def require_auth(view_func):
    """Декоратор для проверки аутентификации"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = get_token_from_request(request)
        
        if not token:
            return Response(
                json_body={
                    'error': 'Unauthorized',
                    'message': 'Требуется аутентификация. Отправьте токен в заголовке Authorization: Bearer <token>'
                },
                status=401,
                content_type='application/json'
            )
        
        user_info = get_user_from_token(token)
        if not user_info:
            return Response(
                json_body={
                    'error': 'Invalid token',
                    'message': 'Неверный или истекший токен'
                },
                status=401,
                content_type='application/json'
            )
        
        # Добавляем информацию о пользователе в request
        request.user = user_info
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_role(*allowed_roles):
    """Декоратор для проверки роли пользователя"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Сначала проверяем аутентификацию
            token = get_token_from_request(request)
            
            if not token:
                return Response(
                    json_body={
                        'error': 'Unauthorized',
                        'message': 'Требуется аутентификация'
                    },
                    status=401,
                    content_type='application/json'
                )
            
            user_info = get_user_from_token(token)
            if not user_info:
                return Response(
                    json_body={
                        'error': 'Invalid token',
                        'message': 'Неверный или истекший токен'
                    },
                    status=401,
                    content_type='application/json'
                )
            
            # Проверяем роль
            user_role = user_info.get('role')
            if user_role not in allowed_roles:
                return Response(
                    json_body={
                        'error': 'Forbidden',
                        'message': f'Доступ запрещен. Требуются роли: {", ".join(allowed_roles)}'
                    },
                    status=403,
                    content_type='application/json'
                )
            
            # Добавляем информацию о пользователе в request
            request.user = user_info
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


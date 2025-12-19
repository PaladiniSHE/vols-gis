"""Views для аутентификации"""
from pyramid.view import view_config
from pyramid.response import Response
from ..models.users import User
from ..schemas.users import UserLogin
from ..auth.jwt import create_access_token
import logging
import traceback
import hashlib

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Хеширует пароль (используем тот же метод, что в users.py)"""
    return hashlib.sha256(password.encode()).hexdigest()


@view_config(route_name='api_auth_login', request_method='POST')
def auth_login(request):
    """Вход пользователя и получение JWT токена"""
    try:
        logger.info('Запрос на вход пользователя')
        
        if not hasattr(request, 'db') or request.db is None:
            logger.error('DB сессия не доступна')
            return Response(
                json_body={
                    'error': 'Database session not available',
                    'message': 'PostgreSQL не запущен или недоступен.'
                },
                status=500,
                content_type='application/json'
            )
        
        db = request.db
        
        try:
            data = request.json_body
        except Exception as e:
            logger.error(f'Ошибка парсинга JSON: {e}')
            return Response(
                json_body={'error': 'Invalid JSON', 'message': 'Неверный формат данных'},
                status=400,
                content_type='application/json'
            )
        
        # Валидация данных
        try:
            login_data = UserLogin(**data)
        except Exception as e:
            logger.error(f'Ошибка валидации: {e}')
            return Response(
                json_body={'error': 'Validation error', 'message': str(e)},
                status=400,
                content_type='application/json'
            )
        
        # Поиск пользователя
        try:
            user = db.query(User).filter(User.username == login_data.username).first()
        except Exception as query_error:
            logger.error(f'Ошибка выполнения запроса: {query_error}')
            return Response(
                json_body={
                    'error': 'Database query error',
                    'message': f'Ошибка при выполнении запроса: {str(query_error)}'
                },
                status=500,
                content_type='application/json'
            )
        
        if not user:
            logger.warning(f'Попытка входа с несуществующим username: {login_data.username}')
            return Response(
                json_body={
                    'error': 'Invalid credentials',
                    'message': 'Неверное имя пользователя или пароль'
                },
                status=401,
                content_type='application/json'
            )
        
        # Проверка активности
        if not user.is_active:
            logger.warning(f'Попытка входа неактивного пользователя: {user.id}')
            return Response(
                json_body={
                    'error': 'Account disabled',
                    'message': 'Аккаунт пользователя отключен'
                },
                status=403,
                content_type='application/json'
            )
        
        # Проверка пароля
        password_hash = hash_password(login_data.password)
        if user.password_hash != password_hash:
            logger.warning(f'Неверный пароль для пользователя: {user.id}')
            return Response(
                json_body={
                    'error': 'Invalid credentials',
                    'message': 'Неверное имя пользователя или пароль'
                },
                status=401,
                content_type='application/json'
            )
        
        # Создание токена
        token = create_access_token(user.id, user.username, user.role or 'viewer')
        
        logger.info(f'Пользователь успешно вошел: {user.id} ({user.username})')
        
        return Response(
            json_body={
                'access_token': token,
                'token_type': 'Bearer',
                'user': user.to_dict(),
                'message': 'Успешный вход'
            },
            content_type='application/json'
        )
        
    except Exception as e:
        logger.error(f'Ошибка при входе: {str(e)}')
        logger.error(traceback.format_exc())
        
        if hasattr(request, 'db') and request.db is not None:
            try:
                request.db.rollback()
            except:
                pass
        
        return Response(
            json_body={'error': f'Internal Server Error: {str(e)}'},
            status=500,
            content_type='application/json'
        )


@view_config(route_name='api_auth_me', request_method='GET')
def auth_me(request):
    """Получение информации о текущем пользователе"""
    from ..auth.decorators import get_token_from_request, get_user_from_token
    
    try:
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
        
        # Получаем полную информацию о пользователе из БД
        if not hasattr(request, 'db') or request.db is None:
            return Response(
                json_body={
                    'error': 'Database session not available',
                    'message': 'PostgreSQL не запущен или недоступен.'
                },
                status=500,
                content_type='application/json'
            )
        
        db = request.db
        user = db.query(User).filter(User.id == user_info['user_id']).first()
        
        if not user:
            return Response(
                json_body={
                    'error': 'User not found',
                    'message': 'Пользователь не найден'
                },
                status=404,
                content_type='application/json'
            )
        
        return Response(
            json_body={'user': user.to_dict()},
            content_type='application/json'
        )
        
    except Exception as e:
        logger.error(f'Ошибка при получении информации о пользователе: {str(e)}')
        logger.error(traceback.format_exc())
        
        return Response(
            json_body={'error': f'Internal Server Error: {str(e)}'},
            status=500,
            content_type='application/json'
        )


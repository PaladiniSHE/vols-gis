"""Views для управления пользователями"""
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.exc import IntegrityError
from ..models.users import User
from ..schemas.users import UserCreate, UserUpdate, UserLogin
from ..auth.decorators import require_auth, require_role
import logging
import traceback
import hashlib

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Хеширует пароль"""
    return hashlib.sha256(password.encode()).hexdigest()


@view_config(route_name='api_users_list', request_method='GET')
@require_auth
def users_list(request):
    """Список всех пользователей"""
    try:
        logger.info('Запрос списка пользователей')
        
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
            users = db.query(User).all()
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
        
        logger.info(f'Найдено пользователей: {len(users)}')
        
        users_list = []
        for user in users:
            try:
                users_list.append(user.to_dict())
            except Exception as e:
                logger.warning(f'Ошибка при преобразовании пользователя {user.id}: {e}')
                continue
        
        result = {'users': users_list, 'count': len(users_list)}
        logger.info(f'Список пользователей успешно сформирован: {len(users_list)} элементов')
        return Response(json_body=result, content_type='application/json')
        
    except Exception as e:
        logger.error(f'Ошибка при получении списка пользователей: {str(e)}')
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


@view_config(route_name='api_users_list', request_method='POST')
@require_role('admin')
def users_create(request):
    """Создание нового пользователя"""
    try:
        logger.info('Запрос на создание пользователя')
        
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
            user_data = UserCreate(**data)
        except Exception as e:
            logger.error(f'Ошибка валидации: {e}')
            return Response(
                json_body={'error': 'Validation error', 'message': str(e)},
                status=400,
                content_type='application/json'
            )
        
        # Проверка уникальности username и email
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            return Response(
                json_body={
                    'error': 'User already exists',
                    'message': 'Пользователь с таким username или email уже существует'
                },
                status=409,
                content_type='application/json'
            )
        
        # Создание пользователя
        try:
            new_user = User(
                username=user_data.username,
                email=user_data.email,
                password_hash=hash_password(user_data.password),
                role=user_data.role,
                is_active=user_data.is_active
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            logger.info(f'Пользователь создан: {new_user.id}')
            return Response(
                json_body={'user': new_user.to_dict(), 'message': 'Пользователь успешно создан'},
                status=201,
                content_type='application/json'
            )
        except IntegrityError as e:
            db.rollback()
            logger.error(f'Ошибка целостности данных: {e}')
            return Response(
                json_body={
                    'error': 'Integrity error',
                    'message': 'Пользователь с таким username или email уже существует'
                },
                status=409,
                content_type='application/json'
            )
        except Exception as e:
            db.rollback()
            logger.error(f'Ошибка при создании пользователя: {e}')
            return Response(
                json_body={'error': 'Database error', 'message': str(e)},
                status=500,
                content_type='application/json'
            )
            
    except Exception as e:
        logger.error(f'Ошибка при создании пользователя: {str(e)}')
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


@view_config(route_name='api_users_get', request_method='GET')
def users_get(request):
    """Получение пользователя по ID"""
    try:
        user_id = int(request.matchdict['id'])
        logger.info(f'Запрос пользователя с ID: {user_id}')
        
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
            user = db.query(User).filter(User.id == user_id).first()
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
            return Response(
                json_body={'error': 'Not found', 'message': 'Пользователь не найден'},
                status=404,
                content_type='application/json'
            )
        
        logger.info(f'Пользователь найден: {user.id}')
        return Response(
            json_body={'user': user.to_dict()},
            content_type='application/json'
        )
        
    except ValueError:
        return Response(
            json_body={'error': 'Invalid ID', 'message': 'Неверный ID пользователя'},
            status=400,
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f'Ошибка при получении пользователя: {str(e)}')
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


@view_config(route_name='api_users_get', request_method='PUT')
@require_auth
def users_update(request):
    """Обновление пользователя"""
    try:
        user_id = int(request.matchdict['id'])
        logger.info(f'Запрос на обновление пользователя с ID: {user_id}')
        
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
            user = db.query(User).filter(User.id == user_id).first()
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
            return Response(
                json_body={'error': 'Not found', 'message': 'Пользователь не найден'},
                status=404,
                content_type='application/json'
            )
        
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
            user_update = UserUpdate(**data)
        except Exception as e:
            logger.error(f'Ошибка валидации: {e}')
            return Response(
                json_body={'error': 'Validation error', 'message': str(e)},
                status=400,
                content_type='application/json'
            )
        
        # Проверка прав: пользователь может редактировать только свой профиль (если не админ)
        user_role = request.user.get('role', 'viewer')
        if user_role != 'admin' and user_id != request.user.get('user_id'):
            return Response(
                json_body={
                    'error': 'Forbidden',
                    'message': 'Вы можете редактировать только свой профиль'
                },
                status=403,
                content_type='application/json'
            )
        
        # Обновление полей
        update_data = user_update.dict(exclude_unset=True)
        
        if 'password' in update_data:
            update_data['password_hash'] = hash_password(update_data.pop('password'))
        
        # Проверка уникальности username и email
        if 'username' in update_data or 'email' in update_data:
            existing_user = db.query(User).filter(
                User.id != user_id,
                ((User.username == update_data.get('username', '')) |
                 (User.email == update_data.get('email', '')))
            ).first()
            
            if existing_user:
                return Response(
                    json_body={
                        'error': 'User already exists',
                        'message': 'Пользователь с таким username или email уже существует'
                    },
                    status=409,
                    content_type='application/json'
                )
        
        try:
            for key, value in update_data.items():
                setattr(user, key, value)
            
            db.commit()
            db.refresh(user)
            
            logger.info(f'Пользователь обновлен: {user.id}')
            return Response(
                json_body={'user': user.to_dict(), 'message': 'Пользователь успешно обновлен'},
                content_type='application/json'
            )
        except IntegrityError as e:
            db.rollback()
            logger.error(f'Ошибка целостности данных: {e}')
            return Response(
                json_body={
                    'error': 'Integrity error',
                    'message': 'Пользователь с таким username или email уже существует'
                },
                status=409,
                content_type='application/json'
            )
        except Exception as e:
            db.rollback()
            logger.error(f'Ошибка при обновлении пользователя: {e}')
            return Response(
                json_body={'error': 'Database error', 'message': str(e)},
                status=500,
                content_type='application/json'
            )
            
    except ValueError:
        return Response(
            json_body={'error': 'Invalid ID', 'message': 'Неверный ID пользователя'},
            status=400,
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f'Ошибка при обновлении пользователя: {str(e)}')
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


@view_config(route_name='api_users_get', request_method='DELETE')
@require_role('admin')
def users_delete(request):
    """Удаление пользователя"""
    try:
        user_id = int(request.matchdict['id'])
        logger.info(f'Запрос на удаление пользователя с ID: {user_id}')
        
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
            user = db.query(User).filter(User.id == user_id).first()
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
            return Response(
                json_body={'error': 'Not found', 'message': 'Пользователь не найден'},
                status=404,
                content_type='application/json'
            )
        
        try:
            db.delete(user)
            db.commit()
            
            logger.info(f'Пользователь удален: {user_id}')
            return Response(
                json_body={'message': 'Пользователь успешно удален'},
                status=200,
                content_type='application/json'
            )
        except Exception as e:
            db.rollback()
            logger.error(f'Ошибка при удалении пользователя: {e}')
            return Response(
                json_body={'error': 'Database error', 'message': str(e)},
                status=500,
                content_type='application/json'
            )
            
    except ValueError:
        return Response(
            json_body={'error': 'Invalid ID', 'message': 'Неверный ID пользователя'},
            status=400,
            content_type='application/json'
        )
    except Exception as e:
        logger.error(f'Ошибка при удалении пользователя: {str(e)}')
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


"""JWT утилиты для аутентификации"""
import jwt
import datetime
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Секретный ключ (в продакшене должен быть в переменных окружения)
SECRET_KEY = "vols-gis-secret-key-change-in-production"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


def create_access_token(user_id: int, username: str, role: str) -> str:
    """Создает JWT токен для пользователя"""
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": expire,
        "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> Optional[Dict]:
    """Декодирует и проверяет JWT токен"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None


def get_user_from_token(token: str) -> Optional[Dict]:
    """Получает информацию о пользователе из токена"""
    payload = decode_access_token(token)
    if payload:
        return {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "role": payload.get("role")
        }
    return None


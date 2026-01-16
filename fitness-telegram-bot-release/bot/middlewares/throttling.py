"""
Rate limiting middleware для защиты от спама
"""
import time
from typing import Any, Awaitable, Callable, Dict
from collections import defaultdict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware для ограничения частоты запросов от пользователей.
    
    Использует простой алгоритм token bucket для ограничения.
    """
    
    def __init__(
        self, 
        rate_limit: float = 0.5,  # Минимальный интервал между запросами (секунды)
        max_burst: int = 3,       # Максимальное количество запросов подряд
        cooldown: float = 3.0     # Время блокировки при превышении лимита (секунды)
    ):
        """
        Args:
            rate_limit: Минимальный интервал между запросами в секундах
            max_burst: Максимальное количество запросов подряд без задержки
            cooldown: Время блокировки пользователя при превышении лимита
        """
        self.rate_limit = rate_limit
        self.max_burst = max_burst
        self.cooldown = cooldown
        
        # Хранилище данных о запросах пользователей
        # user_id -> {"last_time": float, "burst_count": int, "blocked_until": float}
        self.users: Dict[int, Dict[str, float]] = defaultdict(
            lambda: {"last_time": 0, "burst_count": 0, "blocked_until": 0}
        )
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Обработка события с проверкой rate limit"""
        
        # Получаем user_id из события
        user_id = self._get_user_id(event)
        if user_id is None:
            return await handler(event, data)
        
        current_time = time.time()
        user_data = self.users[user_id]
        
        # Проверяем, заблокирован ли пользователь
        if current_time < user_data["blocked_until"]:
            remaining = user_data["blocked_until"] - current_time
            await self._send_throttle_message(event, remaining)
            return None
        
        # Рассчитываем время с последнего запроса
        time_passed = current_time - user_data["last_time"]
        
        if time_passed < self.rate_limit:
            # Запрос слишком частый
            user_data["burst_count"] += 1
            
            if user_data["burst_count"] > self.max_burst:
                # Превышен лимит - блокируем пользователя
                user_data["blocked_until"] = current_time + self.cooldown
                user_data["burst_count"] = 0
                await self._send_throttle_message(event, self.cooldown)
                return None
        else:
            # Достаточный интервал - сбрасываем счетчик
            user_data["burst_count"] = max(0, user_data["burst_count"] - 1)
        
        # Обновляем время последнего запроса
        user_data["last_time"] = current_time
        
        return await handler(event, data)
    
    def _get_user_id(self, event: TelegramObject) -> int | None:
        """Получить ID пользователя из события"""
        if isinstance(event, Message):
            return event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            return event.from_user.id if event.from_user else None
        return None
    
    async def _send_throttle_message(self, event: TelegramObject, remaining: float):
        """Отправить сообщение о превышении лимита"""
        message_text = f"⏳ Слишком много запросов! Подожди {remaining:.1f} сек."
        
        try:
            if isinstance(event, Message):
                await event.answer(message_text)
            elif isinstance(event, CallbackQuery):
                await event.answer(message_text, show_alert=True)
        except Exception:
            pass  # Игнорируем ошибки отправки


class AntiFloodMiddleware(BaseMiddleware):
    """
    Простой middleware для защиты от флуда.
    
    Отклоняет запросы если пользователь отправляет более N сообщений в минуту.
    """
    
    def __init__(self, max_requests_per_minute: int = 30):
        """
        Args:
            max_requests_per_minute: Максимальное количество запросов в минуту
        """
        self.max_requests = max_requests_per_minute
        self.window_size = 60.0  # 1 минута
        
        # user_id -> [timestamp1, timestamp2, ...]
        self.request_history: Dict[int, list] = defaultdict(list)
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Обработка события с проверкой на флуд"""
        
        user_id = self._get_user_id(event)
        if user_id is None:
            return await handler(event, data)
        
        current_time = time.time()
        history = self.request_history[user_id]
        
        # Удаляем старые записи (старше 1 минуты)
        cutoff_time = current_time - self.window_size
        self.request_history[user_id] = [t for t in history if t > cutoff_time]
        history = self.request_history[user_id]
        
        # Проверяем количество запросов
        if len(history) >= self.max_requests:
            try:
                if isinstance(event, Message):
                    await event.answer("🚫 Слишком много запросов. Попробуйте позже.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("🚫 Слишком много запросов!", show_alert=True)
            except Exception:
                pass
            return None
        
        # Добавляем текущий запрос
        history.append(current_time)
        
        return await handler(event, data)
    
    def _get_user_id(self, event: TelegramObject) -> int | None:
        """Получить ID пользователя из события"""
        if isinstance(event, Message):
            return event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            return event.from_user.id if event.from_user else None
        return None

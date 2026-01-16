"""
Тесты для middleware
"""
import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

from bot.middlewares.throttling import ThrottlingMiddleware, AntiFloodMiddleware


class TestThrottlingMiddleware:
    """Тесты для ThrottlingMiddleware"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.middleware = ThrottlingMiddleware(
            rate_limit=0.5,
            max_burst=2,
            cooldown=1.0
        )
    
    def create_mock_message(self, user_id: int):
        """Создать mock сообщения"""
        message = MagicMock()
        message.from_user = MagicMock()
        message.from_user.id = user_id
        message.answer = AsyncMock()
        return message
    
    @pytest.mark.asyncio
    async def test_first_request_passes(self):
        """Первый запрос должен проходить"""
        message = self.create_mock_message(123)
        handler = AsyncMock(return_value="OK")
        
        result = await self.middleware(handler, message, {})
        
        assert result == "OK"
        handler.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_rapid_requests_blocked(self):
        """Быстрые запросы должны блокироваться после burst"""
        message = self.create_mock_message(456)
        handler = AsyncMock(return_value="OK")
        
        # Первые 3 запроса проходят (max_burst=2 + 1 первый)
        for i in range(3):
            await self.middleware(handler, message, {})
        
        # Четвертый должен быть заблокирован
        result = await self.middleware(handler, message, {})
        
        # handler был вызван только 3 раза (не 4)
        assert handler.call_count == 3
    
    @pytest.mark.asyncio
    async def test_requests_after_interval_pass(self):
        """Запросы после интервала должны проходить"""
        message = self.create_mock_message(789)
        handler = AsyncMock(return_value="OK")
        
        # Первый запрос
        await self.middleware(handler, message, {})
        
        # Ждем больше rate_limit
        await asyncio.sleep(0.6)
        
        # Второй запрос должен пройти
        result = await self.middleware(handler, message, {})
        
        assert result == "OK"
        assert handler.call_count == 2
    
    @pytest.mark.asyncio
    async def test_different_users_isolated(self):
        """Разные пользователи не должны влиять друг на друга"""
        message1 = self.create_mock_message(111)
        message2 = self.create_mock_message(222)
        handler = AsyncMock(return_value="OK")
        
        # User1 делает много запросов
        for _ in range(5):
            await self.middleware(handler, message1, {})
        
        # User2 делает первый запрос - должен пройти
        result = await self.middleware(handler, message2, {})
        
        assert result == "OK"


class TestAntiFloodMiddleware:
    """Тесты для AntiFloodMiddleware"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.middleware = AntiFloodMiddleware(max_requests_per_minute=5)
    
    def create_mock_message(self, user_id: int):
        """Создать mock сообщения"""
        message = MagicMock()
        message.from_user = MagicMock()
        message.from_user.id = user_id
        message.answer = AsyncMock()
        return message
    
    @pytest.mark.asyncio
    async def test_under_limit_passes(self):
        """Запросы в пределах лимита должны проходить"""
        message = self.create_mock_message(333)
        handler = AsyncMock(return_value="OK")
        
        # 5 запросов (= лимиту)
        for _ in range(5):
            result = await self.middleware(handler, message, {})
            assert result == "OK"
        
        assert handler.call_count == 5
    
    @pytest.mark.asyncio
    async def test_over_limit_blocked(self):
        """Запросы сверх лимита должны блокироваться"""
        message = self.create_mock_message(444)
        handler = AsyncMock(return_value="OK")
        
        # 6 запросов (> лимита)
        results = []
        for _ in range(6):
            result = await self.middleware(handler, message, {})
            results.append(result)
        
        # Первые 5 прошли, 6-й заблокирован
        assert results.count("OK") == 5
        assert results[-1] is None
    
    @pytest.mark.asyncio
    async def test_different_users_independent(self):
        """Лимиты для разных пользователей независимы"""
        message1 = self.create_mock_message(555)
        message2 = self.create_mock_message(666)
        handler = AsyncMock(return_value="OK")
        
        # User1 исчерпывает лимит
        for _ in range(5):
            await self.middleware(handler, message1, {})
        
        # User2 все еще может делать запросы
        result = await self.middleware(handler, message2, {})
        
        assert result == "OK"

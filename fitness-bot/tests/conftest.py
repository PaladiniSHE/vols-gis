"""
Конфигурация pytest
"""
import pytest
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def event_loop():
    """Создать event loop для асинхронных тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_user_data():
    """Пример данных пользователя"""
    return {
        "telegram_id": 123456789,
        "username": "test_user",
        "first_name": "Test",
        "last_name": "User",
        "height": 175,
        "weight": 70,
        "age": 30,
        "gender": "male",
        "goal": "lose",
        "activity_level": "medium"
    }


@pytest.fixture
def sample_food_data():
    """Пример данных продукта"""
    return {
        "name": "Куриная грудка",
        "calories_100g": 165,
        "protein_100g": 31,
        "fat_100g": 3.6,
        "carbs_100g": 0,
        "category": "Мясо"
    }


@pytest.fixture
def sample_food_entry():
    """Пример записи о приеме пищи"""
    return {
        "meal_type": "lunch",
        "portion_size": 150,
        "calories": 248,
        "protein": 46.5,
        "fat": 5.4,
        "carbs": 0
    }

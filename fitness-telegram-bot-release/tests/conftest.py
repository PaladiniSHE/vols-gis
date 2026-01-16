"""
Pytest конфигурация и общие фикстуры
"""
import pytest
import asyncio
from typing import Generator


# Настройка asyncio для pytest
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Создать event loop для всех тестов сессии.
    
    Это необходимо для корректной работы async тестов с pytest-asyncio.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# Настройки pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


def pytest_configure(config):
    """
    Конфигурация pytest при запуске.
    
    Добавляем маркеры для категоризации тестов.
    """
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


@pytest.fixture
def anyio_backend():
    """Бэкенд для anyio (используется pytest-asyncio)"""
    return 'asyncio'
